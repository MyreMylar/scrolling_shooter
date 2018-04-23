import random
import math
import pygame
import csv
import os
from pygame.locals import *

from game.tile import *
from game.standard_monster import *


class TiledLevel():
    def __init__(self, levelTileSize, allTileSprites, allMonsterSprites, monsters, screenData, explosionsSpriteSheet):

        self.initialScreenOffset = [0,0]
        self.positionOffset = [0,0]
        self.currentCentrePosition = [100000000,111111111111]

        self.fileName = "data/level.csv"
        self.explosionsSpriteSheet = explosionsSpriteSheet
        
        self.screenData = screenData

        self.tile_map = self.loadTileTable("images/tiles/tile_map.png", 64, 64, False)

        self.allMonsterSprites = allMonsterSprites
        self.monsters = monsters

        self.zeroTileX = 0
        self.zeroTileY = 0
        self.endTileX = 0
        self.endTileY = 0

        self.tileGrid = []
        self.tiles = []
        self.collidableTiles = []
        self.walkable_tiles = []
        
        self.aiSpawns = []

        self.levelTileSize = levelTileSize
        self.levelPixelSize = [self.levelTileSize[0]*64,self.levelTileSize[1]*64]

        for tileX in range(0, self.levelTileSize[0]):
            column = []
            for tileY in range(0, self.levelTileSize[1]):
                column.append(None)
            self.tileGrid.append(column)
            
        self.initialOffset = True

        self.allTileData = {}
        tileDataFiles = [file for file in os.listdir("data/tiles/") if os.path.isfile(os.path.join("data/tiles/", file))]

        self.defaultTile = None
        for fileName in tileDataFiles:
            newTileData = TileData(os.path.join("data/tiles/", fileName), self.tile_map)
            newTileData.loadTileData()
            self.allTileData[newTileData.tileID] = newTileData
            if self.defaultTile == None:
                self.defaultTile = newTileData


    def clearLevelToDefaultTile(self):
        for x in range(0, self.levelTileSize[0]):
            for y in range(0,self.levelTileSize[1]):
                xCentre = 32 + (x * 64)
                yCentre = 32 + (y * 64)
                defaultTile = Tile([xCentre, yCentre], 0, self.defaultTile)
                self.tiles.append(defaultTile)
                self.walkable_tiles.append(defaultTile)
        
    def resetGuards(self):
        pass

    def isPositionOnScreen(self, worldPosition):
        isOnscreen = False
        if worldPosition[0] > self.positionOffset[0] and worldPosition[1] > self.positionOffset[1]:
            if worldPosition[0] < self.positionOffset[0] + self.screenData.playArea[0] and worldPosition[1] < self.positionOffset[1] + self.screenData.playArea[1]:
                isOnscreen = True
        return isOnscreen
    
    def updateOffsetPosition(self, centrePosition, allTileSprites):
        shouldUpdate = False
        self.currentCentrePosition = centrePosition
        xOffset = int(self.currentCentrePosition[0] - self.initialScreenOffset[0])
        yOffset = int(self.currentCentrePosition[1] - self.initialScreenOffset[1])

        if xOffset <= 0:
            xOffset = 0
        if xOffset >= int(self.levelPixelSize[0] - self.screenData.playArea[0]):
            xOffset = int(self.levelPixelSize[0] - self.screenData.playArea[0])

        if yOffset <= 0:
            yOffset = 0
        if yOffset >= int(self.levelPixelSize[1] - self.screenData.playArea[1]):
            yOffset = int(self.levelPixelSize[1] - self.screenData.playArea[1])
            
        if self.initialOffset or not (xOffset == self.positionOffset[0] and yOffset == self.positionOffset[1]) :
            if self.initialOffset:
                self.initialOffset = False
            self.positionOffset = [xOffset, yOffset]

            screenTileWidth = int(self.screenData.playArea[0]/64) + 1
            screenTileHeight = int(self.screenData.playArea[1]/64) + 2

            oldZeroTileX = self.zeroTileX
            oldZeroTileY = self.zeroTileY

            self.zeroTileX = int(xOffset/64)
            self.zeroTileY = int(yOffset/64)

            if self.zeroTileX != oldZeroTileX or self.zeroTileY != oldZeroTileY:
                allTileSprites.empty()
                self.endTileX = self.zeroTileX + screenTileWidth
                self.endTileY = self.zeroTileY + screenTileHeight

                if self.endTileX >= len(self.tileGrid):
                    self.endTileX = len(self.tileGrid)
                if self.endTileY >= len(self.tileGrid[0]):
                    self.endTileY = len(self.tileGrid[0])
                
                for tileX in range(self.zeroTileX, self.endTileX):
                    for tileY in range(self.zeroTileY, self.endTileY):
                        tile = self.tileGrid[tileX][tileY]
                        if tile == None:
                            print("No tile at grid: " + str(tileX) + ", " + str(tileY))
                        else:
                            tile.updateOffsetPosition(self.positionOffset, self.screenData)
                            allTileSprites.add(tile.sprite)
            else:
                for tileX in range(self.zeroTileX, self.endTileX):
                    for tileY in range(self.zeroTileY, self.endTileY):
                        tile = self.tileGrid[tileX][tileY]
                        tile.updateOffsetPosition(self.positionOffset, self.screenData)

            for spawn in self.aiSpawns:
                spawn.updateOffsetPosition(self.positionOffset)

        return shouldUpdate


    def checkUpdateVisibleTiles(self):
        pass
    
    def findPlayerStart(self):
        playerStart = [0,0]
        shortestDistance = 100000
        worldCentre = [self.levelPixelSize[0]/2, self.levelPixelSize[1]/2]
        startPosition = [worldCentre[0], self.levelPixelSize[1]]#worldCentre
        screenCentre = [self.screenData.playArea[0]/2, self.screenData.playArea[1]/2]
        tileClosestToStartPosition = None
        for tile in self.walkable_tiles:
            xDist = float(startPosition[0]) -  float(tile.world_position[0])
            yDist =  float(startPosition[1]) -  float(tile.world_position[1])
            distance = math.sqrt((xDist * xDist) + (yDist * yDist))
            if distance < shortestDistance:
                shortestDistance = distance
                
                playerStart[0] = tile.world_position[0]
                playerStart[1] = tile.world_position[1]
                tileClosestToStartPosition = tile
        
        self.playerStart = playerStart
        
        self.initialScreenOffset[0] = screenCentre[0]
        self.initialScreenOffset[1] = screenCentre[1]
        
        self.currentCentrePosition = playerStart
        xOffset = int(self.currentCentrePosition[0] - self.initialScreenOffset[0])
        yOffset = int(self.currentCentrePosition[1] - self.initialScreenOffset[1])

        if xOffset <= 0:
            xOffset = 0
        if xOffset >= int(self.levelPixelSize[0] - self.screenData.playArea[0]):
            xOffset = int(self.levelPixelSize[0] - self.screenData.playArea[0])

        if yOffset <= 0:
            yOffset = 0
        if yOffset >= int(self.levelPixelSize[1] - self.screenData.playArea[1]):
            yOffset = int(self.levelPixelSize[1] - self.screenData.playArea[1])
            
        self.positionOffset = [xOffset, yOffset]

        self.initialOffset = True
        #print("Offset at start: " + str(self.positionOffset[0]) + ", " + str(self.positionOffset[1]))
        return playerStart


    def loadTileTable(self, filename, width, height, useTransparency):
        image = None
        if useTransparency:
            image = pygame.image.load(filename).convert_alpha()
        else:
            image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, int(image_width/width)):
            line = []
            tile_table.append(line)
            for tile_y in range(0, int(image_height/height)):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        return tile_table


    def getTileDataAtPos(self, clickPos):
        for tile in self.tiles:
            if tile.sprite.rect[0] <= clickPos[0] and tile.sprite.rect[1] <= clickPos[1]:
                if tile.sprite.rect[0] + tile.sprite.rect[2] > clickPos[0] and tile.sprite.rect[1] + tile.sprite.rect[3] > clickPos[1]:
                    return [tile.sprite.rect, tile.tileImage, tile.tileID, False, tile]
        return [pygame.Rect(0, 0, 0, 0), None, "", False, None]

    def setTileAtPos(self, clickPos, newTileImage, tileID, tileAngle):
        tileToSet = None
        for tile in self.tiles:
            if tile.sprite.rect[0] <= clickPos[0] and tile.sprite.rect[1] <= clickPos[1]:
                if tile.sprite.rect[0] + tile.sprite.rect[2] > clickPos[0] and tile.sprite.rect[1] + tile.sprite.rect[3] > clickPos[1]:
                    tileToSet = tile
                    break
        if tileToSet != None:
            if tileToSet.collidable:
                self.collidableTiles.remove(tileToSet)
            else:
                self.walkable_tiles.remove(tileToSet)
                
            newTile = None

            newTile = Tile(tileToSet.world_position, tileAngle, self.allTileData[tileID])
            newTile.position = tileToSet.position
                    
            self.tiles.remove(tileToSet)        
            self.tiles.append(newTile)

            self.tileGrid[int((newTile.world_position[0]-32)/64)][int((newTile.world_position[1]-32)/64)] = newTile


            if newTile.collidable:
                self.collidableTiles.append(newTile)
            else:
                self.walkable_tiles.append(newTile)
                
            

            self.checkUpdateVisibleTiles()

    def saveTiles(self):
        with open(self.fileName, "w", newline='') as tileFile:
            writer = csv.writer(tileFile)
            for tile in self.tiles:
                writer.writerow(["tile",tile.tileID,str(tile.world_position[0]),str(tile.world_position[1]),str(tile.angle)])

            for aiSpawn in self.aiSpawns:
                writer.writerow(["aiSpawn",aiSpawn.typeID,str(aiSpawn.world_position[0]),str(aiSpawn.world_position[1])])

    def loadTiles(self):
        if os.path.isfile(self.fileName):
            self.tiles[:] = []
            self.collidableTiles[:] = []
            self.walkable_tiles[:] = []
            
            with open(self.fileName, "r") as tileFile:
                reader = csv.reader(tileFile)
                for line in reader:
                    lineType = line[0]
                    
                    if lineType == "tile":
                        tileID = line[1]
                        tileXPos = int(line[2])
                        tileYPos = int(line[3])
                        tileAngle = int(line[4])
                        loadedTile = Tile([tileXPos, tileYPos], tileAngle, self.allTileData[tileID])                        
                        self.tiles.append(loadedTile)

                        self.tileGrid[int((tileXPos-32)/64)][int((tileYPos-32)/64)] = loadedTile

                        if loadedTile.collidable:
                            self.collidableTiles.append(loadedTile)
                        else:
                            self.walkable_tiles.append(loadedTile)
                            
                    elif lineType == "aiSpawn":
                        typeID = line[1]
                        tileXPos = int(line[2])
                        tileYPos = int(line[3])
                        newAISpawn = AISpawn(self.guardsSpriteMap[0][1], [tileXPos,tileYPos],typeID)
                        self.aiSpawns.append(newAISpawn)
        else:
            self.clearLevelToDefaultTile()

    def addAISpawnAtPos(self, clickPos, aiSpawn):      
        for tile in self.tiles:
            if tile.sprite.rect[0] <= clickPos[0] and tile.sprite.rect[1] <= clickPos[1]:
                if tile.sprite.rect[0] + tile.sprite.rect[2] > clickPos[0] and tile.sprite.rect[1] + tile.sprite.rect[3] > clickPos[1]:
                    tileToSet = tile
        alreadyPlaced = False
        for spawn in self.aiSpawns:
            if spawn.world_position[0] == tileToSet.world_position[0] and spawn.world_position[1] == tileToSet.world_position[1]:
                alreadyPlaced = True

        if not alreadyPlaced:
            newAISpawn = AISpawn(aiSpawn.tileImage, tileToSet.world_position, aiSpawn.typeID)
            newAISpawn.updateOffsetPosition(self.positionOffset)
            self.aiSpawns.append(newAISpawn)

