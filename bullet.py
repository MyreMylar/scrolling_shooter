import math
import random
import pygame
from pygame.locals import *

import game.projectile as ProjectileCode
import game.explosion as ExplosionCode
import game.damage as DamageCode

class Bullet(ProjectileCode.Projectile):
    def __init__(self, startPos, initialHeadingVector, damage, bulletSpeed, explosionsSpriteSheet, isAIBullet = False):

        self.isAIBullet = isAIBullet
        self.explosionsSpriteSheet = explosionsSpriteSheet
        self.imageName = "images/bullet.png"
        self.original_image = pygame.image.load(self.imageName).convert_alpha()
 
        self.sprite = pygame.sprite.Sprite()

        self.currentVector = [initialHeadingVector[0], initialHeadingVector[1]]
        #ensure bullet vector is normalised
        directionMagnitude = max(0.001, math.sqrt(self.currentVector[0] ** 2 + self.currentVector[1] ** 2))
        self.currentVector = [self.currentVector[0]/directionMagnitude, self.currentVector[1]/directionMagnitude]

        self.position = [float(startPos[0]),float(startPos[1])]
        self.world_position = [float(startPos[0]),float(startPos[1])]
        
        #calc facing angle
        facingAngle = math.atan2(-self.currentVector[0], -self.currentVector[1])*180/math.pi
        self.image = pygame.transform.rotate(self.original_image,facingAngle)
        self.sprite.image = self.image
        self.sprite.rect = self.image.get_rect()
        self.sprite.rect.center = self.position

        self.shouldDie = False

        self.bulletSpeed  = bulletSpeed
        self.damage = damage

        self.shotRange = 1024.0

    def updateSprite(self, allBulletSprites):
        allBulletSprites.add(self.sprite)
        return allBulletSprites

    def updateMovementAndCollision(self, tiledLevel, collideableTiles, players, monsters, timeDelta, newExplosions, explosions):
        if self.shotRange <= 0.0:
            self.shouldDie = True

        if not self.shouldDie:
            if not self.isAIBullet:
                for monster in monsters:
                    if monster.testProjectileCollision(self.sprite.rect):
                        monster.takeDamage(self.damage)
                        self.shouldDie = True

            else:  # is a monster bullet
                for player in players:
                    if player.testProjectileCollision(self.sprite.rect):
                        player.takeDamage(self.damage)
                        self.shouldDie = True 

            self.shotRange -= timeDelta * self.bulletSpeed
            self.world_position[0] += (self.currentVector[0] * timeDelta * self.bulletSpeed)
            self.world_position[1] += (self.currentVector[1] * timeDelta * self.bulletSpeed)
            
            self.position[0] = self.world_position[0] - tiledLevel.positionOffset[0]
            self.position[1] = self.world_position[1] - tiledLevel.positionOffset[1]

            self.sprite.rect.center = self.position


    def drawCollisionRect(self, screen):
        ck = (127, 33, 33)
        s = pygame.Surface((self.sprite.rect.width, self.sprite.rect.height))
        s.fill(ck)
        s.set_colorkey(ck)
        pygame.draw.rect(s, pygame.Color(100, 200, 100), pygame.Rect([0,0],[self.sprite.rect.width,self.sprite.rect.height]))
        s.set_alpha(160)
        screen.blit(s, [int(self.sprite.rect.left),int(self.sprite.rect.top)])



