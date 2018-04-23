import math
import random
import pygame
from pygame.locals import *

import game.pick_up as PickUpCode
import bullet as BulletCode
import game.missile as MissileCode

class MonsterPath():
    def __init__(self):
        self.startWaypoint = [0,0]
        self.waypoints = []
        self.waypointRadius = 32

class BaseMonster():
    def __init__(self, typeID, waveOrder, startPos, allMonsterSprites, playArea, tiledLevel, explosionsSpriteSheet):

        self.id = typeID
        self.waveOrder = waveOrder
        self.startPos = startPos
        self.playArea = playArea
        self.tiledLevel = tiledLevel
        self.explosionsSpriteSheet = explosionsSpriteSheet

        if self.id == "spherical":
            self.imageName = "images/alien_1.png"
            self.original_image = pygame.image.load(self.imageName).convert_alpha()
            self.attackTimeDelay = 1.0
            self.botherPlayerTime = 10.0
            self.bulletSpeed = 300.0
            self.perBulletDamage = 20
        elif self.id == "mechanical":
            self.imageName = "images/alien_2.png"
            self.original_image = pygame.image.load(self.imageName).convert_alpha()
            self.attackTimeDelay = 0.5
            self.botherPlayerTime = 10.0
            self.bulletSpeed = 600.0
            self.perBulletDamage = 10
            
        self.image = self.original_image.copy()
        self.sprite = pygame.sprite.Sprite()
        self.flashSprite = pygame.sprite.Sprite() 
        self.testCollisionSprite = pygame.sprite.Sprite()

        self.sprite_rot_centre_offset = [0.0, 0.0]
                       
        self.sprite.rect = self.image.get_rect()

        self.sprite.rect.center = self.startPos

        self.position = [float(self.sprite.rect.center[0]),float(self.sprite.rect.center[1])]

        self.screen_position = [0,0]
        self.screen_position[0] = self.position[0]
        self.screen_position[1] = self.position[1]

        self.updateScreenPosition(self.tiledLevel.positionOffset)
        
        self.sprite.image = self.image

        self.changeDirectionTime = 5.0
        self.changeDirectionAccumulator = 0.0

        self.currentVector = [0.0, 1.0]

        self.rotateSprite()
    
        self.shouldDie = False
        
        self.spriteNeedsUpdate = True
        self.allMonsterSprites = allMonsterSprites
        self.allMonsterSprites.add(self.sprite)

        self.health = 100

        self.slowDownPercentage = 1.0
        self.collideRadius = 27

        self.isWanderingAimlessly = True
        self.randomTargetChangeTime = random.uniform(3.0,15.0)
        self.randomTargetChangeAcc = 0.0

        self.timeToHomeInOnPlayer = False
        self.monsterHomeOnTargetTime = random.uniform(0.3,1.5)
        self.monsterHomeOnTargetAcc = 0.0

        self.isTimeToStartAttack = True
        self.attackTimeAcc = 0.0
        

        self.isAttacking = False
        self.shouldDoAttackDamage = False
        self.attackAnimAcc = 0.0
        self.attackAnimTotalTime = 0.8

        
        

        self.barrelExitPos = [0.0,0.0]
        self.barrelForwardOffset = 32
        self.barrelSideOffset = 6

        self.spriteFlashAcc = 0.0
        self.spriteFlashTime = 0.15
        self.shouldFlashSprite = False
        self.activeFlashSprite = False

        self.botherTimeAcc = 0.0
        self.fleeing = False
        self.fleeSpeed = 800.0

        self.dodgeSpeed = 300.0

        vecList = [-1,1]
        self.dodgeVector = [float(random.choice(vecList)),0.0]

        self.randomDodgeChangeAcc = 0.0
        self.randomDodgeChangeTime = 0.5

    def updateSprite(self, timeDelta, timeMultiplier):
        if self.spriteNeedsUpdate:
            self.spriteNeedsUpdate = False
            self.sprite.image = self.image

        if self.shouldFlashSprite and not self.shouldDie:
            self.spriteFlashAcc += timeDelta * timeMultiplier
            if self.spriteFlashAcc > self.spriteFlashTime:
                self.spriteFlashAcc = 0.0
                self.shouldFlashSprite = False
                if self.activeFlashSprite:
                    self.allMonsterSprites.remove(self.flashSprite)
                    self.activeFlashSprite = False
            else:
                lerpValue = self.spriteFlashAcc/self.spriteFlashTime
                flashAlpha = self.lerp(255, 0, lerpValue)
                flashImage = self.sprite.image.copy()
                flashImage.fill((0, 0, 0, flashAlpha), None, pygame.BLEND_RGBA_MULT)
                flashImage.fill((255,255,255,0), None, pygame.BLEND_RGBA_ADD)
                self.flashSprite.image = flashImage
                self.flashSprite.rect = self.flashSprite.image.get_rect()
                self.flashSprite.rect.center = self.rotPoint([self.screen_position[0], self.screen_position[1]+self.sprite_rot_centre_offset[1]], self.screen_position, -self.oldFacingAngle)
                if not self.activeFlashSprite:
                    self.allMonsterSprites.add(self.flashSprite)
                    self.activeFlashSprite = True

    def takeDamage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        self.shouldFlashSprite = True

    def updateMovementAndCollision(self, timeDelta, timeMultiplier, screenData, player, newExplosions, tiledLevel, monsters, projectiles, pickUpSpawner):

        for explosion in newExplosions:
            if self.testExplosionCollision(explosion):
                self.takeDamage(explosion.damage.amount) 
        if self.health <= 0:
            self.shouldDie = True

        #idle AI state
        if self.isWanderingAimlessly and not player.shouldDie:
            xDist = float(player.position[0]) -  float(self.position[0])
            yDist =  float(player.position[1]) -  float(self.position[1])
            distanceToPlayer = math.sqrt((xDist * xDist) + (yDist * yDist))
            
            if tiledLevel.isPositionOnScreen(self.position):
                self.isWanderingAimlessly = False
            elif self.randomTargetChangeAcc < self.randomTargetChangeTime:
                self.randomTargetChangeAcc += timeDelta
            

        if self.fleeing:
            self.currentVector = [0.0, 1.0]
            self.position[0] += self.fleeSpeed * timeDelta * self.currentVector[0]
            self.position[1] += self.fleeSpeed * timeDelta * self.currentVector[1]
        #preparing to shoot AI state
        if not self.isWanderingAimlessly and not self.fleeing and not player.shouldDie :

            wavePosition = [self.position[0],self.position[1] -(64 * self.waveOrder) -32]
            if tiledLevel.isPositionOnScreen(wavePosition):
                self.matchPlayerVector = [0.0, -1.0]
                self.position[1] += player.speed * timeDelta * self.matchPlayerVector[1]

            self.position[0] += self.dodgeSpeed * timeDelta * self.dodgeVector[0]
            self.position[1] += self.dodgeSpeed * timeDelta * self.dodgeVector[1]

            if self.randomDodgeChangeAcc < self.randomDodgeChangeTime:
                self.randomDodgeChangeAcc += timeDelta
            else:
                self.randomDodgeChangeAcc = 0.0
                self.randomDodgeChangeTime = float(random.uniform(5,10))/20.0
                vecList = [-1,1]
                self.dodgeVector = [float(random.choice(vecList)),0.0]
                
            if self.position[0] < 32:
                self.position[0] = 32.0
            if self.position[0] > 992:
                self.position[0] = 992.0

            if self.id == "spherical":
                xDist = float(player.position[0]) -  float(self.position[0])
                yDist =  float(player.position[1]) -  float(self.position[1])
                distanceToPlayer = math.sqrt((xDist * xDist) + (yDist * yDist))

                if distanceToPlayer > 0.0:
                    self.currentVector = [xDist/distanceToPlayer, yDist/distanceToPlayer]

                self.rotateSprite()
            else:
                self.currentVector = [0.0, 1.0]

            if self.botherTimeAcc > self.botherPlayerTime:
                self.fleeing = True
            else:
                self.botherTimeAcc += timeDelta


            if self.attackTimeAcc < self.attackTimeDelay:
                self.attackTimeAcc += timeDelta * timeMultiplier
            else:
                if tiledLevel.isPositionOnScreen(self.position):
                    self.attackTimeAcc = random.random()/10.0 # add a small random amount to the reload delay
                    self.isTimeToStartAttack = True
                
            if self.isTimeToStartAttack:
                self.isTimeToStartAttack = False
                self.isAttacking = True
                if self.id == "spherical":
                    projectiles.append(BulletCode.Bullet( self.position, self.currentVector, self.perBulletDamage, self.bulletSpeed, self.explosionsSpriteSheet, True))
                if self.id == "mechanical":
                    bullet1Pos = [self.position[0]+20,self.position[1]]
                    bullet2Pos = [self.position[0]-20,self.position[1]]
                    projectiles.append(BulletCode.Bullet( bullet1Pos, self.currentVector, self.perBulletDamage, self.bulletSpeed, self.explosionsSpriteSheet, True))
                    projectiles.append(BulletCode.Bullet( bullet2Pos, self.currentVector, self.perBulletDamage, self.bulletSpeed, self.explosionsSpriteSheet, True))
                
        #shooting/reloading
        if self.isAttacking:
            self.attackAnimAcc += timeDelta * timeMultiplier
            if self.attackAnimAcc > self.attackAnimTotalTime:
                self.attackAnimAcc = 0.0
                self.isAttacking = False
            

        self.updateScreenPosition(self.tiledLevel.positionOffset)
        self.sprite.rect.center = self.screen_position

        if self.shouldDie:
            self.allMonsterSprites.remove(self.sprite)
            if self.activeFlashSprite:
                self.allMonsterSprites.remove(self.flashSprite)
                self.activeFlashSprite = False
            self.tryPickUpSpawn(pickUpSpawner)

    def updateScreenPosition(self, worldOffset):
        self.screen_position[0] = self.position[0] - worldOffset[0]
        self.screen_position[1] = self.position[1] - worldOffset[1]
            
    def getRandomPointInRadiusOfPoint(self, point, radius):
        r = 0
        t = 2*math.pi*random.random()
        u = random.random() + random.random()
        if u > 1:
            r = 2-u
        else:
            r = u
        return [point[0] + radius*r*math.cos(t), point[1] + radius*r*math.sin(t)]

    
    
    def testPointInExplosion(self, point, explosion):
        return (point[0] - explosion.position[0])**2 + (point[1] - explosion.position[1])**2 < explosion.radius**2

    def testProjectileCollision(self, projectileRect):
        collided = False
        if (self.sprite.rect.colliderect(projectileRect)):
            if (self.testPointInCircle(projectileRect.topleft, self.screen_position, self.collideRadius)) or (self.testPointInCircle(projectileRect.topright, self.screen_position, self.collideRadius)) or (self.testPointInCircle(projectileRect.bottomleft, self.screen_position, self.collideRadius)) or (self.testPointInCircle(projectileRect.bottomright, self.screen_position, self.collideRadius)):
                collided = True
        return collided

    def testPointInCircle(self, point, circlePos, circleRadius):
        return (point[0] - circlePos[0])**2 + (point[1] - circlePos[1])**2 < circleRadius**2
    
    def testMonsterCollision(self, tempPlayerRect, monster):
        collided = False
        if (tempPlayerRect.colliderect(monster.sprite.rect)):
            collided = self.isIntersecting(monster)
        return collided
    
    def testTileCollision(self, tempPlayerRect, tile):
        collided = False
        if (tempPlayerRect.colliderect(tile.sprite.rect)):
            collided = self.isIntersectingTile(tile)
        return collided

    #tiles positions are in screen space currently
    def isIntersectingTile(self, c2):
        distance = math.sqrt((self.screen_position[0] - c2.position[0]) * (self.screen_position[0] - c2.position[0]) + (self.screen_position[1] - c2.position[1]) * (self.screen_position[1] - c2.position[1]))
        if abs((self.collideRadius - c2.collideRadius)) <= distance and distance <= (self.collideRadius + c2.collideRadius):
            return True
        else:
            return False

    def isIntersecting(self, c2):
        distance = math.sqrt((self.position[0] - c2.position[0]) * (self.position[0] - c2.position[0]) + (self.position[1] - c2.position[1]) * (self.position[1] - c2.position[1]))
        if abs((self.collideRadius - c2.collideRadius)) <= distance and distance <= (self.collideRadius + c2.collideRadius):
            return True
        else:
            return False

    def testExplosionCollision(self, explosion):
        collided = False
        if (self.sprite.rect.colliderect(explosion.sprite.rect)):
            collided = self.isExplosionIntersecting(explosion) or self.isCircleInside(explosion)
        return collided
    
    def isExplosionIntersecting(self, c2):
        distance = math.sqrt((self.screen_position[0] - c2.position[0]) * (self.screen_position[0] - c2.position[0]) + (self.screen_position[1] - c2.position[1]) * (self.screen_position[1] - c2.position[1]))
        if abs((self.collideRadius - c2.collideRadius)) <= distance and distance <= (self.collideRadius + c2.collideRadius):
            return True
        else:
            return False

    def isCircleInside(self, c2):
        isInside = False
        distance = math.sqrt((self.screen_position[0] - c2.position[0]) * (self.screen_position[0] - c2.position[0]) + (self.screen_position[1] - c2.position[1]) * (self.screen_position[1] - c2.position[1]))
        if self.collideRadius < c2.collideRadius:
            isInside = distance + self.collideRadius <= c2.collideRadius
        else:
            isInside = distance + c2.collideRadius <= self.collideRadius
        return isInside
    
        
    def setAverageSpeed(self, averageSpeed):
        self.moveSpeed = random.randint(int(averageSpeed * 0.75), int(averageSpeed * 1.25))
        return self.moveSpeed


    def getRandomPointOnScreen(self):
        randomX = random.randint(32, self.playArea[0]-32)
        randomY = random.randint(32, self.playArea[1]-32)
        return [randomX, randomY]

    def rotateSprite(self):
        directionMagnitude = math.sqrt(self.currentVector[0] * self.currentVector[0] + self.currentVector[1] * self.currentVector[1])
        unitDirVector = [0,0]
        if directionMagnitude > 0.0:
            unitDirVector = [self.currentVector[0]/directionMagnitude, self.currentVector[1]/directionMagnitude]
            self.oldFacingAngle = math.atan2(-unitDirVector[0], -unitDirVector[1])*180/math.pi
            monster_centrePosition = self.sprite.rect.center
            self.image = pygame.transform.rotate(self.original_image, self.oldFacingAngle)
            self.sprite.image = self.image
            self.sprite.rect = self.image.get_rect()
            self.sprite.rect.center = monster_centrePosition


    def tryPickUpSpawn(self, pickupSpawner):
        pickupSpawner.trySpawn(self.position)


    def rotPoint(self, point, axis, ang):
        """ Orbit. calcs the new loc for a point that rotates a given num of degrees around an axis point,
        +clockwise, -anticlockwise -> tuple x,y
        """
        ang -= 90
        x, y = point[0] - axis[0], point[1] - axis[1]
        radius = math.sqrt(x*x + y*y) # get the distance between points

        RAng = math.radians(ang)       # convert ang to radians.

        h = axis[0] + ( radius * math.cos(RAng) )
        v = axis[1] + ( radius * math.sin(RAng) )

        return [h, v]

    def lerp(self, A, B, C):
        return (C * B) + ((1.0-C) * A)


    def drawCollisionRect(self, screen):
        ck = (127, 33, 33)
        s = pygame.Surface((self.sprite.rect.width, self.sprite.rect.height))
        s.fill(ck)
        s.set_colorkey(ck)
        pygame.draw.rect(s, pygame.Color(100, 255, 100), pygame.Rect([0,0],[self.sprite.rect.width,self.sprite.rect.height]))
        s.set_alpha(60)
        screen.blit(s, [int(self.sprite.rect.left),int(self.sprite.rect.top)])
        
    def drawCollisionRadiusCircle(self, screen):
        ck = (127, 33, 33)
        size = 25
        intPosition = [0,0]
        intPosition[0] = int(self.screen_position[0]-self.collideRadius)
        intPosition[1] = int(self.screen_position[1]-self.collideRadius)
        s = pygame.Surface((self.collideRadius*2, self.collideRadius*2))

        # first, "erase" the surface by filling it with a color and
        # setting this color as colorkey, so the surface is empty
        s.fill(ck)
        s.set_colorkey(ck)

        pygame.draw.circle(s, pygame.Color(100, 100, 255), (self.collideRadius, self.collideRadius), self.collideRadius)

        # after drawing the circle, we can set the 
        # alpha value (transparency) of the surface
        s.set_alpha(100)
        screen.blit(s, intPosition)

        
    
        
    




