import math
import random
import pygame
from pygame.locals import *

import game.damage as DamageCode

class Explosion():
    def __init__(self, startPos, explosionSheet, size, damageAmount, damageType):

        self.radius = size
        self.collideRadius = self.radius
        self.explosionSheet = explosionSheet
        self.explosionFrames = 16
        self.explosionImages = []
        randomExplosionInt = random.randrange(0,512,64)
        for i in range(0, self.explosionFrames):
            xStartIndex = (i * 64)
            explosionFrame = self.explosionSheet.subsurface(pygame.Rect(xStartIndex+1, randomExplosionInt+1, 62, 62))
            explosionFrame = pygame.transform.scale(explosionFrame,(self.radius*2, self.radius*2))
            self.explosionImages.append(explosionFrame)
        self.sprite = pygame.sprite.Sprite()      
        self.sprite.image = self.explosionImages[0]
                
        self.sprite.rect = self.explosionImages[0].get_rect()  
        self.sprite.rect.center = startPos

        self.position = [float(self.sprite.rect.center[0]),float(self.sprite.rect.center[1])]
        self.world_position = [float(self.sprite.rect.center[0]),float(self.sprite.rect.center[1])]
        
        self.shouldDie = False
        self.lifeTime = 0.45
        self.time = self.lifeTime
        self.frameTime = self.lifeTime/self.explosionFrames
        self.frame = 1

        self.damage = DamageCode.Damage(damageAmount, damageType)
        
    def updateSprite(self, allExplosionSprites, timeDelta, timeMultiplier, tiledLevel):
       
        self.position[0] = self.world_position[0] - tiledLevel.positionOffset[0]
        self.position[1] = self.world_position[1] - tiledLevel.positionOffset[1]
        self.sprite.rect.center = self.position
        
        self.time -= timeDelta * timeMultiplier
        if self.time < 0.0:
            self.shouldDie = True

        if self.frame < self.explosionFrames and (self.lifeTime - self.time) > (self.frameTime * self.frame):
            self.sprite.image = self.explosionImages[self.frame]
            self.frame += 1

        allExplosionSprites.add(self.sprite)
            
        return allExplosionSprites
    

    def updateMovementAndCollision(self):
        pass

