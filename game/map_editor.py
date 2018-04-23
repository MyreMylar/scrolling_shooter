from game.tile import *
from game.map_editor_instructions_window import MapEditorInstructionsWindow
from pygame.locals import *


class MapEditor:

    def __init__(self, tiled_level, hud_rect, fonts):
        self.tiledLevel = tiled_level
        self.hudRect = hud_rect
        
        self.leftMouseHeld = False
        self.rightMouseHeld = False

        self.needToRefreshTiles = True

        self.defaultTile = [pygame.Rect(0, 0, 0, 0), self.tiledLevel.tile_map[0][0], "grass_tile", True, None]
        self.heldTileData = self.defaultTile

        self.heldAISpawn = None

        self.hoveredRec = None

        self.rotateSelectedTileLeft = False
        self.rotateSelectedTileRight = False

        self.palette_tiles = []
        x_pos = 40
        y_pos = 40
        for tileData in sorted(self.tiledLevel.allTileData.keys()):
            self.palette_tiles.append(Tile([self.hudRect[0] + x_pos, self.hudRect[1] + y_pos],
                                           0, self.tiledLevel.allTileData[tileData]))
            x_pos += 72

            if x_pos > 904:
                x_pos = 40
                y_pos += 72

        self.palette_ai_spawns = []
        self.all_palette_tile_sprites = pygame.sprite.Group()

        self.allAISpawnSprites = pygame.sprite.Group()
        
        for tile in self.palette_tiles:
            self.all_palette_tile_sprites.add(tile.sprite)

        for aiSpawn in self.palette_ai_spawns:
            self.all_palette_tile_sprites.add(aiSpawn.sprite)

        self.leftScrollHeld = False
        self.rightScrollHeld = False
        self.upScrollHeld = False
        self.downScrollHeld = False

        self.mapPosition = self.tiledLevel.find_player_start()

        self.mapEditorInstructions = MapEditorInstructionsWindow([362, 100, 300, 250], fonts)

        self.rect_of_tile = None

    def run(self, screen, background, all_tile_sprites, hud_rect, time_delta):
        running = True
        for event in pygame.event.get():
            if self.mapEditorInstructions is not None:
                self.mapEditorInstructions.handle_input_event(event)
            else:
                if event.type == QUIT:
                    self.tiledLevel.save_tiles()
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
                        self.tiledLevel.save_tiles()
                        running = False
                    if event.key == K_F5:
                        self.tiledLevel.save_tiles()
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
            
        if self.mapEditorInstructions is not None:
            self.mapEditorInstructions.update()
            if self.mapEditorInstructions.shouldExit:
                self.mapEditorInstructions = None

        if self.upScrollHeld:
            self.mapPosition[1] -= 256.0 * time_delta
            if self.mapPosition[1] < self.tiledLevel.initialScreenOffset[1]:
                self.mapPosition[1] = self.tiledLevel.initialScreenOffset[1]
        if self.downScrollHeld:
            self.mapPosition[1] += 256.0 * time_delta
            if self.mapPosition[1] > (self.tiledLevel.levelPixelSize[1] -
                                      self.tiledLevel.initialScreenOffset[1] + self.hudRect[1]):
                self.mapPosition[1] = (self.tiledLevel.levelPixelSize[1] -
                                       self.tiledLevel.initialScreenOffset[1] + self.hudRect[1])

        if self.leftScrollHeld:
            self.mapPosition[0] -= 256.0 * time_delta
            if self.mapPosition[0] < self.tiledLevel.initialScreenOffset[0]:
                self.mapPosition[0] = self.tiledLevel.initialScreenOffset[0]
        if self.rightScrollHeld:
            self.mapPosition[0] += 256.0 * time_delta
            if self.mapPosition[0] > (self.tiledLevel.levelPixelSize[0] - self.tiledLevel.initialScreenOffset[0]):
                self.mapPosition[0] = (self.tiledLevel.levelPixelSize[0] - self.tiledLevel.initialScreenOffset[0])
                
        if self.rotateSelectedTileRight and self.heldTileData[4] is not None:
            self.rotateSelectedTileRight = False
            self.heldTileData[4].rotate_tile_right()
            self.needToRefreshTiles = True

        if self.rotateSelectedTileLeft and self.heldTileData[4] is not None:
            self.rotateSelectedTileLeft = False
            self.heldTileData[4].rotate_tile_left()
            self.needToRefreshTiles = True
        
        if self.leftMouseHeld:
            click_pos = pygame.mouse.get_pos()
            if self.is_inside_hud(click_pos, hud_rect):
                self.heldTileData = self.get_palette_tile_data_at_pos(click_pos)
                if self.heldTileData is None:
                    self.heldAISpawn = self.get_ai_spawn_data_at_pos(click_pos)
                    
            else:
                self.heldTileData = self.tiledLevel.get_tile_data_at_pos(click_pos)

        if self.rightMouseHeld:
            click_pos = pygame.mouse.get_pos()
            
            if self.is_inside_hud(click_pos, hud_rect):
                pass
            else:
                angle = 0
                if self.heldTileData is not None:
                    if self.heldTileData[4] is not None:
                        angle = self.heldTileData[4].angle
                    self.rect_of_tile = self.tiledLevel.set_tile_at_pos(click_pos,
                                                                        self.heldTileData[1],
                                                                        self.heldTileData[2], angle)
                    self.needToRefreshTiles = True
                elif self.heldAISpawn is not None:
                    self.tiledLevel.add_ai_spawn_at_pos(click_pos, self.heldAISpawn)

        if self.tiledLevel.update_offset_position(self.mapPosition, all_tile_sprites):
            self.needToRefreshTiles = True

        self.allAISpawnSprites.empty()

        for aiSpawn in self.tiledLevel.aiSpawns:
            self.allAISpawnSprites.add(aiSpawn.sprite)

        self.hoveredRec = self.tiledLevel.get_tile_data_at_pos(pygame.mouse.get_pos())[0]

        screen.blit(background, (0, 0))  # draw the background
        all_tile_sprites.draw(screen)
        self.allAISpawnSprites.draw(screen)

        if self.heldTileData is not None:
            if not self.heldTileData[3]:
                pygame.draw.rect(screen, pygame.Color(255, 100, 100),
                                 self.heldTileData[0], 1)  # draw the selection rectangle
        if self.hoveredRec is not None:
            pygame.draw.rect(screen, pygame.Color(255, 225, 100), self.hoveredRec, 1)  # draw the selection rectangle
        
        pygame.draw.rect(screen, pygame.Color(60, 60, 60), hud_rect, 0)  # draw the hud
        self.all_palette_tile_sprites.draw(screen)
        if self.heldTileData is not None:
            if self.heldTileData[3]:
                pygame.draw.rect(screen, pygame.Color(255, 100, 100),
                                 self.heldTileData[0], 1)  # draw the selection rectangle

        if self.mapEditorInstructions is not None:
            self.mapEditorInstructions.draw(screen)

        pygame.display.flip()  # flip all our drawn stuff onto the screen

        return running

    @staticmethod
    def is_inside_hud(pos, hud_rect):
        if hud_rect[0] <= pos[0] and hud_rect[1] <= pos[1]:
            if hud_rect[0] + hud_rect[2] > pos[0] and hud_rect[1] + hud_rect[3] > pos[1]:
                return True
        return False

    def get_palette_tile_data_at_pos(self, click_pos):
        for tile in self.palette_tiles:
            if tile.sprite.rect[0] <= click_pos[0] and tile.sprite.rect[1] <= click_pos[1]:
                if tile.sprite.rect[0] + tile.sprite.rect[2] > click_pos[0] and\
                        tile.sprite.rect[1] + tile.sprite.rect[3] > click_pos[1]:
                    return [tile.sprite.rect, tile.tileImage, tile.tileID, True, None]
        return None

    def get_ai_spawn_data_at_pos(self, click_pos):
        for aiSpawn in self.palette_ai_spawns:
            if aiSpawn.sprite.rect[0] <= click_pos[0] and aiSpawn.sprite.rect[1] <= click_pos[1]:
                if aiSpawn.sprite.rect[0] + aiSpawn.sprite.rect[2] > click_pos[0] and\
                        aiSpawn.sprite.rect[1] + aiSpawn.sprite.rect[3] > click_pos[1]:
                    return aiSpawn
        return None
