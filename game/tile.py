import random
import pygame
import copy
import math
import csv
import os

from pygame.locals import *


class AISpawn():
    def __init__(self, image, position, typeID):
        self.typeID = typeID
        self.position = [0,0]
        self.position[0] = position[0]
        self.position[1] = position[1]

        self.world_position = [0,0]
        self.world_position[0] = position[0]
        self.world_position[1] = position[1]
        self.tileImage = image
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = self.tileImage
        self.sprite.rect = self.tileImage.get_rect()
        self.sprite.rect.center = self.position

    def updateOffsetPosition(self, offset):
        self.position[0] = self.world_position[0] - offset[0]
        self.position[1] = self.world_position[1] - offset[1]
        self.sprite.rect.center = self.position

class TileData():

    def __init__(self, filePath, tileMap):
        self.filePath = filePath
        self.tileMap = tileMap
        self.tileID = os.path.splitext(os.path.basename(filePath))[0]
        self.collidable = False
        self.collideRadius = 26
        self.collisionShapes = []
        self.image_coords = (0, 0)
        self.tileImage = None

    def loadTileData(self):
        if os.path.isfile(self.filePath):
            with open(self.filePath, "r") as tileFile:
                reader = csv.reader(tileFile)
                for line in reader:
                    dataType = line[0]
                    if dataType == "isCollidable":
                        self.collidable = bool(int(line[1]))
                    elif dataType == "tileImageCoords":
                        self.image_coords = (int(line[1]), int(line[2]))
                        self.tileImage = self.tileMap[int(line[1])][int(line[2])]
                    elif dataType == "rect":
                        topLeftTileOffset = [int(line[1]), int(line[2])]
                        self.collisionShapes.append(["rect", topLeftTileOffset, pygame.Rect(int(line[1]), int(line[2]), int(line[3])-int(line[1]), int(line[4])-int(line[2]))])
                    elif dataType == "circle":
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
                       

class Tile():
    def __init__(self, position, tileAngle, tileData):
        self.groupTileData = tileData
        self.tileData = tileData.copy()
        self.world_position = [position[0],position[1]]
        self.position = [position[0],position[1]]
        self.angle = tileAngle
        self.collideRadius = self.groupTileData.collideRadius
        self.collidable = self.groupTileData.collidable
        self.tileID = self.groupTileData.tileID
        self.tileImage = pygame.transform.rotate(self.groupTileData.tileImage, self.angle)
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = self.tileImage
        self.sprite.rect = self.tileImage.get_rect()
        self.sprite.rect.center = self.position
        self.isVisible = False

    def updateCollisionShapesPosition(self):
        for shape in self.tileData.collisionShapes:
            if shape[0] == "rect":
                shape[2].left = self.sprite.rect.left + shape[1][0]
                shape[2].top = self.sprite.rect.top + shape[1][1]

    def updateOffsetPosition(self, offset, screenData):
        shouldUpdate = False
        shouldAddToVisibleTiles = False
        shouldAddToVisibleCollidableTiles = False
        self.position[0] = self.world_position[0] - offset[0]
        self.position[1] = self.world_position[1] - offset[1]
        self.sprite.rect.center = self.position
        self.updateCollisionShapesPosition()
        if self.position[0] >= -32 and self.position[0] <= screenData.screenSize[0] + 32:
                if self.position[1] >= -32 and self.position[1] <= screenData.screenSize[1] + 32:
                    if not self.isVisible:
                        shouldUpdate = True
                    self.isVisible = True
                    shouldAddToVisibleTiles = True
                    if self.collidable:
                        shouldAddToVisibleCollidableTiles = True    
                else:
                    self.isVisible = False
        else:
            self.isVisible = False
        return (shouldUpdate, shouldAddToVisibleTiles, shouldAddToVisibleCollidableTiles)
            
    def drawCollisionShapes(self, screen):
        for shape in self.tileData.collisionShapes:
            if shape[0] == "circle":
                self.drawRadiusCircle(screen, shape[1])
            elif shape[0] == "rect":
                self.drawCollisionRect(screen, shape[2])
                
    def drawCollisionRect(self, screen, rect):
        ck = (180, 100, 100)
        s = pygame.Surface((rect.width, rect.height))
        s.fill(ck)
        s.set_alpha(75)
        screen.blit(s, rect)
        
    def drawRadiusCircle(self, screen, radius):
        ck = (127, 33, 33)
        intPosition = [0,0]
        intPosition[0] = int(self.position[0]-radius)
        intPosition[1] = int(self.position[1]-radius)
        s = pygame.Surface((radius*2, radius*2))

        # first, "erase" the surface by filling it with a color and
        # setting this color as colorkey, so the surface is empty
        s.fill(ck)
        s.set_colorkey(ck)

        pygame.draw.circle(s, pygame.Color(180, 100, 100), (radius, radius), radius)

        # after drawing the circle, we can set the 
        # alpha value (transparency) of the surface
        s.set_alpha(75)
        screen.blit(s, intPosition)

    def testProjectileCollision(self, projectileRect):
        collided = False
        if (self.sprite.rect.colliderect(projectileRect)):
            for collisionShape in self.tileData.collisionShapes:
                if collisionShape[0] == "circle":
                    if self.testRectInCircle(projectileRect,collisionShape[1]):
                        collided = True
                elif collisionShape[0] == "rect":
                    if collisionShape[2].colliderect(projectileRect):
                        collided = True  
                    
                    
        return collided

    def testPointInCircle(self, point, circlePos, circleRadius):
        return (point[0] - circlePos[0])**2 + (point[1] - circlePos[1])**2 < circleRadius**2

    def testRectInCircle(self, rect, circleRadius):
        tlIn = self.testPointInCircle(rect.topleft, self.position, circleRadius) 
        trIn = self.testPointInCircle(rect.topright, self.position, circleRadius)
        blIn = self.testPointInCircle(rect.bottomleft, self.position, circleRadius)
        brIn = self.testPointInCircle(rect.bottomright, self.position, circleRadius)
        return tlIn or trIn or blIn or brIn

    def rotateTileRight(self):
        self.angle -= 90
        if self.angle < 0:
            self.angle = 270
        self.tileImage = pygame.transform.rotate(self.tileImage, -90)
        self.sprite.image = self.tileImage

    def rotateTileLeft(self):
        self.angle += 90
        if self.angle > 270:
            self.angle = 0
        self.tileImage = pygame.transform.rotate(self.tileImage, 90)
        self.sprite.image = self.tileImage
   
