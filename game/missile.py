import math
import random
import pygame
from pygame.locals import *

import game.projectile as ProjectileCode
import game.explosion as ExplosionCode
import game.damage as DamageCode

class Missile(ProjectileCode.Projectile):
    def __init__(self, startPos, initialHeadingVector, damage, explosionsSpriteSheet, isAIBullet = False):

        self.isAIBullet = isAIBullet
        self.explosionsSpriteSheet = explosionsSpriteSheet
        self.imageName = "images/missile.png"
        self.original_image = pygame.image.load(self.imageName).convert_alpha()
        self.image = self.original_image.copy()
        self.sprite = pygame.sprite.Sprite()
       
        self.sprite.rect = self.image.get_rect()  
        self.sprite.rect.center = startPos

        self.currentVector = [initialHeadingVector[0], initialHeadingVector[1]]

        self.position = [float(self.sprite.rect.center[0]),float(self.sprite.rect.center[1])]
        self.world_position = [float(self.sprite.rect.center[0]),float(self.sprite.rect.center[1])]
        self.sprite.image = self.image

        self.shouldDie = False

        self.bulletSpeed  = 225.0
        self.damage = damage

        self.shotRange = 1024

        self.timeToHomeIn = False
        self.homingTimeAcc = 0.0
        self.homingTime = 0.2
        self.homingRadius = 256

        #print("Firing missile")

    def updateSprite(self, allBulletSprites):
        self.sprite.image = self.image
        allBulletSprites.add(self.sprite)
        return allBulletSprites

    def updateMovementAndCollision(self, tiledLevel, collideableTiles, players, monsters, timeDelta, timeMultiplier, newExplosions, explosions):
        if self.isAIBullet:
            for player in players:
                if player.testProjectileCollision(self.sprite.rect):
                    self.shouldDie = True
        else:
            for monster in monsters:
                if monster.testProjectileCollision(self.sprite.rect):
                    self.shouldDie = True
        for tile in collideableTiles:
            if tile.testProjectileCollision(self.sprite.rect):
                self.shouldDie = True

        #if self.isAIBullet:       
##        if self.homingTimeAcc < self.homingTime:
##            self.homingTimeAcc += timeDelta
##        else:
##            self.timeToHomeIn = True
##            
##        if self.timeToHomeIn:
##            self.homingTimeAcc = 0.0
##            self.timeToHomeIn = False
##            closestMonsterInRadius, closestMonsterDistance = self.getClosestMonsterInRadius(monsters)
##            if closestMonsterInRadius != None:
##                self.currentVector = self.calculateAimingVector(closestMonsterInRadius, closestMonsterDistance)
##                self.shotRange = closestMonsterDistance

        self.shotRange -= timeDelta * timeMultiplier * self.bulletSpeed
        self.world_position[0] += (self.currentVector[0] * timeDelta * timeMultiplier * self.bulletSpeed)
        self.world_position[1] += (self.currentVector[1] * timeDelta * timeMultiplier * self.bulletSpeed)
        
        self.position[0] = self.world_position[0] - tiledLevel.positionOffset[0]
        self.position[1] = self.world_position[1] - tiledLevel.positionOffset[1]
        self.sprite.rect.center = self.position

        if self.shotRange <= 0.0:
            self.shouldDie = True

        #calc facing angle
        directionMagnitude = math.sqrt(self.currentVector[0] * self.currentVector[0] + self.currentVector[1] * self.currentVector[1])
        unitDirVector = [0,0]
        if directionMagnitude > 0.0:
            unitDirVector = [self.currentVector[0]/directionMagnitude, self.currentVector[1]/directionMagnitude]
        facingAngle = math.atan2(-unitDirVector[0], -unitDirVector[1])*180/math.pi

        bullet_centrePosition = self.sprite.rect.center
        self.image = pygame.transform.rotate(self.original_image,facingAngle)
        self.sprite.rect = self.image.get_rect()
        self.sprite.rect.center = bullet_centrePosition

        if self.shouldDie:
            #print("exploding")
            newExplosion = ExplosionCode.Explosion(self.world_position, self.explosionsSpriteSheet, 96, self.damage, DamageCode.DamageType.MISSILE)
            newExplosions.append(newExplosion)
            explosions.append(newExplosion)

    def getClosestMonsterInRadius(self, monsters):
        closestMonsterDistance = 100000.0
        closestMonsterInRadius = None
        for monster in monsters:
            xDist = self.position[0] - monster.position[0]
            yDist = self.position[1] - monster.position[1]
            totalDist = math.sqrt((xDist * xDist) + (yDist * yDist))
            if totalDist < self.homingRadius:
                if totalDist < closestMonsterDistance:
                    closestMonsterDistance = totalDist
                    closestMonsterInRadius = monster
        return closestMonsterInRadius, closestMonsterDistance

    def calculateAimingVector(self, target, distance ):
        xDirection = target.position[0] - self.position[0]
        yDirection = target.position[1] - self.position[1]
        return [xDirection/distance, yDirection/distance]


