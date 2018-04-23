import pygame
from pygame.locals import *
from operator import attrgetter

import game.tiled_level as TiledLevel
from game.tile import *

import game.map_editor_instructions_window as MapEditorInstructionsWindowCode



class MapEditor():

    def __init__(self, tiledLevel, hudRect, fonts):
        self.tiledLevel = tiledLevel
        self.hudRect = hudRect
        
        self.leftMouseHeld = False
        self.rightMouseHeld = False

        self.needToRefreshTiles = True

        self.defaultTile = [ pygame.Rect(0, 0, 0, 0), self.tiledLevel.tile_map[0][0], "grass_tile", True, None]
        self.heldTileData = self.defaultTile

        self.heldAISpawn = None

        self.hoveredRec = None

        self.rotateSelectedTileLeft = False
        self.rotateSelectedTileRight = False

        self.palleteTiles = []
        xPos = 40
        yPos = 40
        for tileData in sorted(self.tiledLevel.allTileData.keys()):
            self.palleteTiles.append(Tile([self.hudRect[0]+xPos, self.hudRect[1]+yPos], 0, self.tiledLevel.allTileData[tileData]))
            xPos += 72

            if xPos > 904:
                xPos = 40
                yPos += 72
            
        
        self.palleteAISpawns = []
        #self.palleteAISpawns.append(AISpawn(self.tiledLevel.guardsSpriteMap[1][0], [self.hudRect[0]+616, self.hudRect[1]+112], "rifle"))
        #self.palleteAISpawns.append(AISpawn(self.tiledLevel.guardsSpriteMap[1][1], [self.hudRect[0]+688, self.hudRect[1]+112], "shotgun"))
        #self.palleteAISpawns.append(AISpawn(self.tiledLevel.guardsSpriteMap[1][2], [self.hudRect[0]+760, self.hudRect[1]+112], "launcher"))
        

        self.allPaletteTileSprites = pygame.sprite.Group()

        self.allAISpawnSprites = pygame.sprite.Group()
        
        for tile in self.palleteTiles:
            self.allPaletteTileSprites.add(tile.sprite)

        for aiSpawn in self.palleteAISpawns:
            self.allPaletteTileSprites.add(aiSpawn.sprite)


        self.leftScrollHeld = False
        self.rightScrollHeld = False
        self.upScrollHeld = False
        self.downScrollHeld = False

        self.mapPosition = self.tiledLevel.findPlayerStart()

        self.mapEditorInstructions = MapEditorInstructionsWindowCode.MapEditorInstructionsWindow([362,100, 300, 250], fonts)
            

    def run(self, screen, background, allTileSprites, hudRect, timeDelta):
        running = True
        for event in pygame.event.get():
            if self.mapEditorInstructions != None:
                self.mapEditorInstructions.handleInputEvent(event)
            else:
                if event.type == QUIT:
                    self.tiledLevel.saveTiles()
                    running = False
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.leftMouseHeld = True
                    if event.button == 3:
                        self.rightMouseHeld = True
                if event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        self.leftMouseHeld = False
                    if event.button == 3:
                        self.rightMouseHeld = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.tiledLevel.saveTiles()
                        running = False
                    if event.key == K_F5:
                        self.tiledLevel.saveTiles()
                    if event.key == K_PERIOD:
                        self.rotateSelectedTileRight = True
                    if event.key == K_COMMA:
                        self.rotateSelectedTileLeft = True
                    if event.key == K_UP:
                        self.upScrollHeld = True
                    if event.key == K_DOWN:
                        self.downScrollHeld = True
                    if event.key == K_LEFT:
                        self.leftScrollHeld = True
                    if event.key == K_RIGHT:
                        self.rightScrollHeld = True
                if event.type == KEYUP:
                    if event.key == K_UP:
                        self.upScrollHeld = False
                    if event.key == K_DOWN:
                        self.downScrollHeld = False
                    if event.key == K_LEFT:
                        self.leftScrollHeld = False
                    if event.key == K_RIGHT:
                        self.rightScrollHeld = False
            
        if self.mapEditorInstructions != None:
            self.mapEditorInstructions.update()
            if self.mapEditorInstructions.shouldExit:
                self.mapEditorInstructions = None

        if self.upScrollHeld:
            self.mapPosition[1] -= 256.0 * timeDelta
            if self.mapPosition[1] < self.tiledLevel.initialScreenOffset[1]:
                self.mapPosition[1] = self.tiledLevel.initialScreenOffset[1]
        if self.downScrollHeld:
            self.mapPosition[1] += 256.0 * timeDelta
            if self.mapPosition[1] > (self.tiledLevel.levelPixelSize[1] - self.tiledLevel.initialScreenOffset[1] + self.hudRect[1]):
                self.mapPosition[1] = (self.tiledLevel.levelPixelSize[1] - self.tiledLevel.initialScreenOffset[1] + self.hudRect[1])

        if self.leftScrollHeld:
            self.mapPosition[0] -= 256.0 * timeDelta
            if self.mapPosition[0] < self.tiledLevel.initialScreenOffset[0]:
                self.mapPosition[0] = self.tiledLevel.initialScreenOffset[0]
        if self.rightScrollHeld:
            self.mapPosition[0] += 256.0 * timeDelta
            if self.mapPosition[0] > (self.tiledLevel.levelPixelSize[0] - self.tiledLevel.initialScreenOffset[0] ):
                self.mapPosition[0] = (self.tiledLevel.levelPixelSize[0] - self.tiledLevel.initialScreenOffset[0])
                
        if self.rotateSelectedTileRight and self.heldTileData[4] != None:
            self.rotateSelectedTileRight = False
            self.heldTileData[4].rotateTileRight()
            self.needToRefreshTiles = True

        if self.rotateSelectedTileLeft and self.heldTileData[4] != None:
            self.rotateSelectedTileLeft = False
            self.heldTileData[4].rotateTileLeft()
            self.needToRefreshTiles = True
        
        if self.leftMouseHeld:
            clickPos = pygame.mouse.get_pos()
            if self.isInsideHUD(clickPos, hudRect):
                self.heldTileData = self.getPaletteTileDataAtPos(clickPos)
                if self.heldTileData == None:
                    self.heldAISpawn = self.getAISpawnDataAtPos(clickPos)
                    
            else:
                self.heldTileData = self.tiledLevel.getTileDataAtPos(clickPos)

        if self.rightMouseHeld:
            clickPos = pygame.mouse.get_pos()
            
            if self.isInsideHUD(clickPos, hudRect):
                pass
            else:
                angle = 0
                if self.heldTileData != None:
                    if self.heldTileData[4] != None:
                        angle = self.heldTileData[4].angle
                    self.rectOfTile = self.tiledLevel.setTileAtPos(clickPos, self.heldTileData[1], self.heldTileData[2], angle)
                    self.needToRefreshTiles = True
                elif self.heldAISpawn != None:
                    #placeAISpawn
                    self.tiledLevel.addAISpawnAtPos(clickPos,self.heldAISpawn)

        if self.tiledLevel.updateOffsetPosition(self.mapPosition, allTileSprites):
            self.needToRefreshTiles = True
                
##        if self.needToRefreshTiles:
##            self.needToRefreshTiles = False
##            allTileSprites.empty()
##            for tile in self.tiledLevel.visibleTiles:
##                allTileSprites.add(tile.sprite)

        self.allAISpawnSprites.empty()

        for aiSpawn in self.tiledLevel.aiSpawns:
            self.allAISpawnSprites.add(aiSpawn.sprite)

        self.hoveredRec = self.tiledLevel.getTileDataAtPos(pygame.mouse.get_pos())[0]

        screen.blit(background, (0, 0)) # draw the background
        allTileSprites.draw(screen)
        self.allAISpawnSprites.draw(screen)

        if self.heldTileData != None:
            if not self.heldTileData[3]:
                pygame.draw.rect(screen, pygame.Color(255, 100, 100), self.heldTileData[0], 1) # draw the selection rectangle
        if self.hoveredRec != None:
            pygame.draw.rect(screen, pygame.Color(255, 225, 100), self.hoveredRec, 1) # draw the selection rectangle 
        
        pygame.draw.rect(screen, pygame.Color(60, 60, 60), hudRect, 0) # draw the hud
        self.allPaletteTileSprites.draw(screen)
        if self.heldTileData != None:
            if self.heldTileData[3]:
                pygame.draw.rect(screen, pygame.Color(255, 100, 100), self.heldTileData[0], 1) # draw the selection rectangle

        if self.mapEditorInstructions != None:
            self.mapEditorInstructions.draw(screen)

        pygame.display.flip() # flip all our drawn stuff onto the screen

        return running

    def isInsideHUD(self, pos, hudRect):
        if hudRect[0] <= pos[0] and hudRect[1] <= pos[1]:
            if hudRect[0] + hudRect[2] > pos[0] and hudRect[1] + hudRect[3] > pos[1]:
                return True
        return False

    def getPaletteTileDataAtPos(self, clickPos):
        for tile in self.palleteTiles:
            if tile.sprite.rect[0] <= clickPos[0] and tile.sprite.rect[1] <= clickPos[1]:
                if tile.sprite.rect[0] + tile.sprite.rect[2] > clickPos[0] and tile.sprite.rect[1] + tile.sprite.rect[3] > clickPos[1]:
                    return [tile.sprite.rect, tile.tileImage, tile.tileID, True, None]
        return None

    def getAISpawnDataAtPos(self, clickPos):
        for aiSpawn in self.palleteAISpawns:
            if aiSpawn.sprite.rect[0] <= clickPos[0] and aiSpawn.sprite.rect[1] <= clickPos[1]:
                if aiSpawn.sprite.rect[0] + aiSpawn.sprite.rect[2] > clickPos[0] and aiSpawn.sprite.rect[1] + aiSpawn.sprite.rect[3] > clickPos[1]:
                    return aiSpawn
        return None
        
