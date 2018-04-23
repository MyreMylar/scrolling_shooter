import pygame
import copy
import csv
import os


class AISpawn:
    def __init__(self, image, position, type_id):
        self.typeID = type_id
        self.position = [0, 0]
        self.position[0] = position[0]
        self.position[1] = position[1]

        self.world_position = [0, 0]
        self.world_position[0] = position[0]
        self.world_position[1] = position[1]
        self.tileImage = image
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = self.tileImage
        self.sprite.rect = self.tileImage.get_rect()
        self.sprite.rect.center = self.position

    def update_offset_position(self, offset):
        self.position[0] = self.world_position[0] - offset[0]
        self.position[1] = self.world_position[1] - offset[1]
        self.sprite.rect.center = self.position


class TileData:

    def __init__(self, file_path, tile_map):
        self.filePath = file_path
        self.tileMap = tile_map
        self.tileID = os.path.splitext(os.path.basename(file_path))[0]
        self.collidable = False
        self.collideRadius = 26
        self.collisionShapes = []
        self.image_coords = (0, 0)
        self.tileImage = None

    def load_tile_data(self):
        if os.path.isfile(self.filePath):
            with open(self.filePath, "r") as tileFile:
                reader = csv.reader(tileFile)
                for line in reader:
                    data_type = line[0]
                    if data_type == "isCollidable":
                        self.collidable = bool(int(line[1]))
                    elif data_type == "tileImageCoords":
                        self.image_coords = (int(line[1]), int(line[2]))
                        self.tileImage = self.tileMap[int(line[1])][int(line[2])]
                    elif data_type == "rect":
                        top_left_tile_offset = [int(line[1]), int(line[2])]
                        self.collisionShapes.append(["rect", top_left_tile_offset,
                                                     pygame.Rect(int(line[1]),
                                                                 int(line[2]),
                                                                 int(line[3])-int(line[1]),
                                                                 int(line[4])-int(line[2]))])
                    elif data_type == "circle":
                        self.collisionShapes.append(["circle", int(line[1])])
                        self.collideRadius = int(line[1])

    def copy(self):
        tile_data_copy = TileData(self.filePath,  self.tileMap)
        tile_data_copy.tileID = copy.deepcopy(self.tileID)
        tile_data_copy.collidable = copy.deepcopy(self.collidable)
        tile_data_copy.collideRadius = copy.deepcopy(self.collideRadius)
        tile_data_copy.collisionShapes = copy.deepcopy(self.collisionShapes)
        self.tileImage = self.tileMap[self.image_coords[0]][self.image_coords[1]]
        return tile_data_copy
                       

class Tile:
    def __init__(self, position, tile_angle, tile_data):
        self.groupTileData = tile_data
        self.tileData = tile_data.copy()
        self.world_position = [position[0], position[1]]
        self.position = [position[0], position[1]]
        self.angle = tile_angle
        self.collideRadius = self.groupTileData.collideRadius
        self.collidable = self.groupTileData.collidable
        self.tileID = self.groupTileData.tileID
        self.tileImage = pygame.transform.rotate(self.groupTileData.tileImage, self.angle)
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = self.tileImage
        self.sprite.rect = self.tileImage.get_rect()
        self.sprite.rect.center = self.position
        self.isVisible = False

    def update_collision_shapes_position(self):
        for shape in self.tileData.collisionShapes:
            if shape[0] == "rect":
                shape[2].left = self.sprite.rect.left + shape[1][0]
                shape[2].top = self.sprite.rect.top + shape[1][1]

    def update_offset_position(self, offset, screen_data):
        should_update = False
        should_add_to_visible_tiles = False
        should_add_to_visible_collidable_tiles = False
        self.position[0] = self.world_position[0] - offset[0]
        self.position[1] = self.world_position[1] - offset[1]
        self.sprite.rect.center = self.position
        self.update_collision_shapes_position()
        if -32 <= self.position[0] <= screen_data.screenSize[0] + 32:
                if -32 <= self.position[1] <= screen_data.screenSize[1] + 32:
                    if not self.isVisible:
                        should_update = True
                    self.isVisible = True
                    should_add_to_visible_tiles = True
                    if self.collidable:
                        should_add_to_visible_collidable_tiles = True
                else:
                    self.isVisible = False
        else:
            self.isVisible = False
        return should_update, should_add_to_visible_tiles, should_add_to_visible_collidable_tiles
            
    def draw_collision_shapes(self, screen):
        for shape in self.tileData.collisionShapes:
            if shape[0] == "circle":
                self.draw_radius_circle(screen, shape[1])
            elif shape[0] == "rect":
                self.draw_collision_rect(screen, shape[2])
                
    @staticmethod
    def draw_collision_rect(screen, rect):
        ck = (180, 100, 100)
        s = pygame.Surface((rect.width, rect.height))
        s.fill(ck)
        s.set_alpha(75)
        screen.blit(s, rect)
        
    def draw_radius_circle(self, screen, radius):
        ck = (127, 33, 33)
        int_position = [0, 0]
        int_position[0] = int(self.position[0]-radius)
        int_position[1] = int(self.position[1]-radius)
        s = pygame.Surface((radius*2, radius*2))

        # first, "erase" the surface by filling it with a color and
        # setting this color as colorkey, so the surface is empty
        s.fill(ck)
        s.set_colorkey(ck)

        pygame.draw.circle(s, pygame.Color(180, 100, 100), (radius, radius), radius)

        # after drawing the circle, we can set the 
        # alpha value (transparency) of the surface
        s.set_alpha(75)
        screen.blit(s, int_position)

    def test_projectile_collision(self, projectile_rect):
        collided = False
        if self.sprite.rect.colliderect(projectile_rect):
            for collisionShape in self.tileData.collisionShapes:
                if collisionShape[0] == "circle":
                    if self.test_rect_in_circle(projectile_rect, collisionShape[1]):
                        collided = True
                elif collisionShape[0] == "rect":
                    if collisionShape[2].colliderect(projectile_rect):
                        collided = True
        return collided

    @staticmethod
    def test_point_in_circle(point, circle_pos, circle_radius):
        return (point[0] - circle_pos[0]) ** 2 + (point[1] - circle_pos[1]) ** 2 < circle_radius ** 2

    def test_rect_in_circle(self, rect, circle_radius):
        tl_in = self.test_point_in_circle(rect.topleft, self.position, circle_radius)
        tr_in = self.test_point_in_circle(rect.topright, self.position, circle_radius)
        bl_in = self.test_point_in_circle(rect.bottomleft, self.position, circle_radius)
        br_in = self.test_point_in_circle(rect.bottomright, self.position, circle_radius)
        return tl_in or tr_in or bl_in or br_in

    def rotate_tile_right(self):
        self.angle -= 90
        if self.angle < 0:
            self.angle = 270
        self.tileImage = pygame.transform.rotate(self.tileImage, -90)
        self.sprite.image = self.tileImage

    def rotate_tile_left(self):
        self.angle += 90
        if self.angle > 270:
            self.angle = 0
        self.tileImage = pygame.transform.rotate(self.tileImage, 90)
        self.sprite.image = self.tileImage
