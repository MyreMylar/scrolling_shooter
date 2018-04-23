import math
from game.tile import *


class TiledLevel:
    def __init__(self, level_tile_size, all_monster_sprites,
                 monsters, screen_data, explosions_sprite_sheet):

        self.initialScreenOffset = [0, 0]
        self.positionOffset = [0, 0]
        self.currentCentrePosition = [100000000, 111111111111]

        self.fileName = "data/level.csv"
        self.explosionsSpriteSheet = explosions_sprite_sheet
        
        self.screenData = screen_data

        self.tile_map = self.load_tile_table("images/tiles/tile_map.png", 64, 64, False)

        self.allMonsterSprites = all_monster_sprites
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

        self.levelTileSize = level_tile_size
        self.levelPixelSize = [self.levelTileSize[0]*64, self.levelTileSize[1]*64]

        for tileX in range(0, self.levelTileSize[0]):
            column = []
            for tileY in range(0, self.levelTileSize[1]):
                column.append(None)
            self.tileGrid.append(column)
            
        self.initialOffset = True

        self.allTileData = {}
        tile_data_files = [file for file in os.listdir("data/tiles/")
                           if os.path.isfile(os.path.join("data/tiles/", file))]

        self.defaultTile = None
        for fileName in tile_data_files:
            new_tile_data = TileData(os.path.join("data/tiles/", fileName), self.tile_map)
            new_tile_data.load_tile_data()
            self.allTileData[new_tile_data.tileID] = new_tile_data
            if self.defaultTile is None:
                self.defaultTile = new_tile_data

        self.playerStart = None

    def clear_level_to_default_tile(self):
        for x in range(0, self.levelTileSize[0]):
            for y in range(0, self.levelTileSize[1]):
                x_centre = 32 + (x * 64)
                y_centre = 32 + (y * 64)
                default_tile = Tile([x_centre, y_centre], 0, self.defaultTile)
                self.tiles.append(default_tile)
                self.walkable_tiles.append(default_tile)
        
    def reset_guards(self):
        pass

    def is_position_on_screen(self, world_position):
        is_onscreen = False
        if world_position[0] > self.positionOffset[0] and world_position[1] > self.positionOffset[1]:
            if world_position[0] < self.positionOffset[0] + self.screenData.playArea[0] and\
                    world_position[1] < self.positionOffset[1] + self.screenData.playArea[1]:
                is_onscreen = True
        return is_onscreen
    
    def update_offset_position(self, centre_position, all_tile_sprites):
        should_update = False
        self.currentCentrePosition = centre_position
        x_offset = int(self.currentCentrePosition[0] - self.initialScreenOffset[0])
        y_offset = int(self.currentCentrePosition[1] - self.initialScreenOffset[1])

        if x_offset <= 0:
            x_offset = 0
        if x_offset >= int(self.levelPixelSize[0] - self.screenData.playArea[0]):
            x_offset = int(self.levelPixelSize[0] - self.screenData.playArea[0])

        if y_offset <= 0:
            y_offset = 0
        if y_offset >= int(self.levelPixelSize[1] - self.screenData.playArea[1]):
            y_offset = int(self.levelPixelSize[1] - self.screenData.playArea[1])
            
        if self.initialOffset or not (x_offset == self.positionOffset[0] and y_offset == self.positionOffset[1]):
            if self.initialOffset:
                self.initialOffset = False
            self.positionOffset = [x_offset, y_offset]

            screen_tile_width = int(self.screenData.playArea[0]/64) + 1
            screen_tile_height = int(self.screenData.playArea[1]/64) + 2

            old_zero_tile_x = self.zeroTileX
            old_zero_tile_y = self.zeroTileY

            self.zeroTileX = int(x_offset/64)
            self.zeroTileY = int(y_offset/64)

            if self.zeroTileX != old_zero_tile_x or self.zeroTileY != old_zero_tile_y:
                all_tile_sprites.empty()
                self.endTileX = self.zeroTileX + screen_tile_width
                self.endTileY = self.zeroTileY + screen_tile_height

                if self.endTileX >= len(self.tileGrid):
                    self.endTileX = len(self.tileGrid)
                if self.endTileY >= len(self.tileGrid[0]):
                    self.endTileY = len(self.tileGrid[0])
                
                for tileX in range(self.zeroTileX, self.endTileX):
                    for tileY in range(self.zeroTileY, self.endTileY):
                        tile = self.tileGrid[tileX][tileY]
                        if tile is None:
                            print("No tile at grid: " + str(tileX) + ", " + str(tileY))
                        else:
                            tile.update_offset_position(self.positionOffset, self.screenData)
                            all_tile_sprites.add(tile.sprite)
            else:
                for tileX in range(self.zeroTileX, self.endTileX):
                    for tileY in range(self.zeroTileY, self.endTileY):
                        tile = self.tileGrid[tileX][tileY]
                        tile.update_offset_position(self.positionOffset, self.screenData)

            for spawn in self.aiSpawns:
                spawn.update_offset_position(self.positionOffset)

        return should_update

    def check_update_visible_tiles(self):
        pass
    
    def find_player_start(self):
        player_start = [0, 0]
        shortest_distance = 100000
        world_centre = [self.levelPixelSize[0]/2, self.levelPixelSize[1]/2]
        start_position = [world_centre[0], self.levelPixelSize[1]]  # world_centre
        screen_centre = [self.screenData.playArea[0]/2, self.screenData.playArea[1]/2]
        for tile in self.walkable_tiles:
            x_dist = float(start_position[0]) - float(tile.world_position[0])
            y_dist = float(start_position[1]) - float(tile.world_position[1])
            distance = math.sqrt((x_dist ** 2) + (y_dist ** 2))
            if distance < shortest_distance:
                shortest_distance = distance
                
                player_start[0] = tile.world_position[0]
                player_start[1] = tile.world_position[1]

        self.playerStart = player_start
        
        self.initialScreenOffset[0] = screen_centre[0]
        self.initialScreenOffset[1] = screen_centre[1]
        
        self.currentCentrePosition = player_start
        x_offset = int(self.currentCentrePosition[0] - self.initialScreenOffset[0])
        y_offset = int(self.currentCentrePosition[1] - self.initialScreenOffset[1])

        if x_offset <= 0:
            x_offset = 0
        if x_offset >= int(self.levelPixelSize[0] - self.screenData.playArea[0]):
            x_offset = int(self.levelPixelSize[0] - self.screenData.playArea[0])

        if y_offset <= 0:
            y_offset = 0
        if y_offset >= int(self.levelPixelSize[1] - self.screenData.playArea[1]):
            y_offset = int(self.levelPixelSize[1] - self.screenData.playArea[1])
            
        self.positionOffset = [x_offset, y_offset]
        self.initialOffset = True

        return player_start

    @staticmethod
    def load_tile_table(filename, width, height, use_transparency):
        if use_transparency:
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

    def get_tile_data_at_pos(self, click_pos):
        for tile in self.tiles:
            if tile.sprite.rect[0] <= click_pos[0] and tile.sprite.rect[1] <= click_pos[1]:
                if tile.sprite.rect[0] + tile.sprite.rect[2] > click_pos[0] and\
                        tile.sprite.rect[1] + tile.sprite.rect[3] > click_pos[1]:
                    return [tile.sprite.rect, tile.tileImage, tile.tileID, False, tile]
        return [pygame.Rect(0, 0, 0, 0), None, "", False, None]

    def set_tile_at_pos(self, click_pos, tile_id, tile_angle):
        tile_to_set = None
        for tile in self.tiles:
            if tile.sprite.rect[0] <= click_pos[0] and tile.sprite.rect[1] <= click_pos[1]:
                if tile.sprite.rect[0] + tile.sprite.rect[2] > click_pos[0] and\
                        tile.sprite.rect[1] + tile.sprite.rect[3] > click_pos[1]:
                    tile_to_set = tile
                    break
        if tile_to_set is not None:
            if tile_to_set.collidable:
                self.collidableTiles.remove(tile_to_set)
            else:
                self.walkable_tiles.remove(tile_to_set)
                
            new_tile = Tile(tile_to_set.world_position, tile_angle, self.allTileData[tile_id])
            new_tile.position = tile_to_set.position
                    
            self.tiles.remove(tile_to_set)
            self.tiles.append(new_tile)

            self.tileGrid[int((new_tile.world_position[0]-32)/64)][int((new_tile.world_position[1]-32)/64)] = new_tile

            if new_tile.collidable:
                self.collidableTiles.append(new_tile)
            else:
                self.walkable_tiles.append(new_tile)

            self.check_update_visible_tiles()

    def save_tiles(self):
        with open(self.fileName, "w", newline='') as tileFile:
            writer = csv.writer(tileFile)
            for tile in self.tiles:
                writer.writerow(["tile", tile.tileID, str(tile.world_position[0]),
                                 str(tile.world_position[1]), str(tile.angle)])

            for aiSpawn in self.aiSpawns:
                writer.writerow(["aiSpawn", aiSpawn.typeID, str(aiSpawn.world_position[0]),
                                 str(aiSpawn.world_position[1])])

    def load_tiles(self):
        if os.path.isfile(self.fileName):
            self.tiles[:] = []
            self.collidableTiles[:] = []
            self.walkable_tiles[:] = []
            
            with open(self.fileName, "r") as tileFile:
                reader = csv.reader(tileFile)
                for line in reader:
                    line_type = line[0]
                    
                    if line_type == "tile":
                        tile_id = line[1]
                        tile_x_pos = int(line[2])
                        tile_y_pos = int(line[3])
                        tile_angle = int(line[4])
                        loaded_tile = Tile([tile_x_pos, tile_y_pos], tile_angle, self.allTileData[tile_id])
                        self.tiles.append(loaded_tile)

                        x_index = int((tile_x_pos-32)/64)
                        y_index = int((tile_y_pos-32)/64)
                        self.tileGrid[x_index][y_index] = loaded_tile

                        if loaded_tile.collidable:
                            self.collidableTiles.append(loaded_tile)
                        else:
                            self.walkable_tiles.append(loaded_tile)
                            
                    elif line_type == "aiSpawn":
                        type_id = line[1]
                        tile_x_pos = int(line[2])
                        tile_y_pos = int(line[3])
                        new_ai_spawn = AISpawn(self.guardsSpriteMap[0][1], [tile_x_pos,tile_y_pos],type_id)
                        self.aiSpawns.append(new_ai_spawn)
        else:
            self.clear_level_to_default_tile()

    def add_ai_spawn_at_pos(self, click_pos, ai_spawn):
        tile_to_set = None
        for tile in self.tiles:
            if tile.sprite.rect[0] <= click_pos[0] and tile.sprite.rect[1] <= click_pos[1]:
                if tile.sprite.rect[0] + tile.sprite.rect[2] > click_pos[0] and \
                        tile.sprite.rect[1] + tile.sprite.rect[3] > click_pos[1]:
                    tile_to_set = tile
        already_placed = False
        if tile_to_set is not None:
            for spawn in self.aiSpawns:
                if spawn.world_position[0] == tile_to_set.world_position[0] and\
                        spawn.world_position[1] == tile_to_set.world_position[1]:
                    already_placed = True

            if not already_placed:
                new_ai_spawn = AISpawn(ai_spawn.tileImage, tile_to_set.world_position, ai_spawn.typeID)
                new_ai_spawn.update_offset_position(self.positionOffset)
                self.aiSpawns.append(new_ai_spawn)
