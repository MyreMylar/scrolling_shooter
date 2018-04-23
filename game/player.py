import math
import pygame
from pygame.locals import *

import bullet as BulletCode


class Scheme():
    def __init__(self):
        self.moveLeft = K_a
        self.moveRight = K_d
        self.fire = K_SPACE


class Player():
    def __init__(self, startPos, tiledLevel, controlScheme, explosionsSpriteSheet):
        
        self.scheme = controlScheme
        self.explosionsSpriteSheet = explosionsSpriteSheet
        self.imageName = "images/player_2.png"
        self.original_image = pygame.image.load(self.imageName).convert_alpha()
        self.image = self.original_image.copy()

        self.sprite = pygame.sprite.Sprite()
        self.testCollisionSprite =  pygame.sprite.Sprite()
        self.flashSprite = pygame.sprite.Sprite() 
        self.sprite.image = self.image        
        self.sprite.rect = self.image.get_rect()  
        self.sprite.rect.center = startPos       

        self.sprite_rot_centre_offset = [0.0, 11.0]
        self.acceleration = 200.0
        self.speed = 0.0
        self.maxSpeed = 250.0
        
        self.strafeSpeed = 0.0
        self.strafeAcceleration = 1000.0
        self.maxStrafeSpeed = 700.0

        self.totalSpeed = 0.0

        self.collideRadius = 18

        self.maxHealth = 100
        self.health = self.maxHealth
        self.shouldDie = False

        self.moveAccumulator = 0.0
       
        self.position = [float(self.sprite.rect.center[0]),float(self.sprite.rect.center[1])]
        self.playerMoveTarget = self.position
        self.distanceToMoveTarget = 0.0
        self.currentVector = [0.0, -1.0]
        self.newFacingAngle = 0

        self.screen_position = [0,0]
        self.screen_position[0] = self.position[0]
        self.screen_position[1] = self.position[1]

        self.updateScreenPosition(tiledLevel.positionOffset)

        directionMagnitude = math.sqrt(self.currentVector[0] * self.currentVector[0] + self.currentVector[1] * self.currentVector[1])
        unitDirVector = [0,0]
        if directionMagnitude > 0.0:
            unitDirVector = [self.currentVector[0]/directionMagnitude, self.currentVector[1]/directionMagnitude]
            self.newFacingAngle = math.atan2(-unitDirVector[0], -unitDirVector[1])*180/math.pi

        self.oldFacingAngle = self.newFacingAngle

        self.sprite.rect.center = self.rotPoint([self.screen_position[0], self.screen_position[1]+self.sprite_rot_centre_offset[1]], self.screen_position, -self.newFacingAngle)

        self.moveLeft = False
        self.moveRight = False

        self.perBulletDamage = 25
        
        self.playerFireTarget = [10000,10000]

        self.spriteFlashAcc = 0.0
        self.spriteFlashTime = 0.15
        self.shouldFlashSprite = False

        self.isCollided = False

        self.shouldDrawCollisionObj = False
        self.collisionObjRects = []
        self.collisionObjRect = pygame.Rect(0.0,0.0,2.0,2.0)

        self.shouldFire = False

  
    def processEvent(self, event):   
        if event.type == KEYDOWN: # key pressed
            if event.key == self.scheme.moveLeft:
                self.moveLeft = True
            if event.key == self.scheme.moveRight:
                self.moveRight = True
            if event.key == self.scheme.fire:
                self.shouldFire = True

        if event.type == KEYUP: # key released
            if event.key == self.scheme.moveLeft:
                self.moveLeft = False
            if event.key == self.scheme.moveRight:
                self.moveRight = False
        
    def getWorldPositionFromScreenPos(self, screenPos, worldOffset):
        worldPos = [0,0]
        worldPos[0] = screenPos[0] + worldOffset[0]
        worldPos[1] = screenPos[1] + worldOffset[1]

        return worldPos
    
    def updateScreenPosition(self, worldOffset):       
        self.screen_position[0] = self.position[0] - worldOffset[0]
        self.screen_position[1] = self.position[1] - worldOffset[1]

    def updateSprite(self, allSprites, timeDelta):
        allSprites.add(self.sprite)
        
        if self.shouldFlashSprite:
            self.spriteFlashAcc += timeDelta
            if self.spriteFlashAcc > self.spriteFlashTime:
                self.spriteFlashAcc = 0.0
                self.shouldFlashSprite = False
            else:
                lerpValue = self.spriteFlashAcc/self.spriteFlashTime
                flashAlpha = self.lerp(255, 0, lerpValue)
                flashImage = self.sprite.image.copy()
                flashImage.fill((0, 0, 0, flashAlpha), None, pygame.BLEND_RGBA_MULT)
                flashImage.fill((255,255,255,0), None, pygame.BLEND_RGBA_ADD)
                self.flashSprite.image = flashImage
                self.flashSprite.rect = self.flashSprite.image.get_rect()
                self.flashSprite.rect.center = self.rotPoint([self.screen_position[0], self.screen_position[1]+self.sprite_rot_centre_offset[1]], self.screen_position, -self.newFacingAngle)
                allSprites.add(self.flashSprite)
        return allSprites


    def updateMovementAndCollision(self, timeDelta, projectiles, tiledLevel, monsters, newExplosions):

        if self.health == 0:
            self.shouldDie = True
            self.speed = 0.0

        if not self.shouldDie:
            for explosion in newExplosions:
                if self.testExplosionCollision(explosion):
                    self.takeDamage(explosion.damage.amount)
                
            if self.shouldFire:
                self.shouldFire = False
                bulletDamage = 10
                bulletSpeed = 800.0
                bullet1Position = [self.position[0]+11,self.position[1]-24]
                bullet2Position = [self.position[0]-11,self.position[1]-24]
                bullet3Position = [self.position[0]+24,self.position[1]-20]
                bullet4Position = [self.position[0]-24,self.position[1]-20]
                bullet5Position = [self.position[0]+17,self.position[1]-22]
                bullet6Position = [self.position[0]-17,self.position[1]-22]
                projectiles.append(BulletCode.Bullet( bullet1Position, [0.0,-1.0], bulletDamage, bulletSpeed, self.explosionsSpriteSheet))
                projectiles.append(BulletCode.Bullet( bullet2Position, [0.0,-1.0], bulletDamage, bulletSpeed, self.explosionsSpriteSheet))
                projectiles.append(BulletCode.Bullet( bullet3Position, [0.0,-1.0], bulletDamage, bulletSpeed, self.explosionsSpriteSheet))
                projectiles.append(BulletCode.Bullet( bullet4Position, [0.0,-1.0], bulletDamage, bulletSpeed, self.explosionsSpriteSheet))
                projectiles.append(BulletCode.Bullet( bullet5Position, [0.0,-1.0], bulletDamage, bulletSpeed, self.explosionsSpriteSheet))
                projectiles.append(BulletCode.Bullet( bullet6Position, [0.0,-1.0], bulletDamage, bulletSpeed, self.explosionsSpriteSheet))
            
            
            self.speed = self.maxSpeed
            if self.moveRight or self.moveLeft:
                if self.moveRight:
                    if self.strafeSpeed > 0.0:
                        self.strafeSpeed = 0.0
                    self.strafeSpeed -= self.strafeAcceleration * timeDelta
                    if abs(self.strafeSpeed) > self.maxStrafeSpeed:
                        self.strafeSpeed = -self.maxStrafeSpeed

                elif self.moveLeft:
                    if self.strafeSpeed < 0.0:
                        self.strafeSpeed = 0.0
                    self.strafeSpeed += self.strafeAcceleration * timeDelta
                    if abs(self.strafeSpeed) > self.maxStrafeSpeed:
                        self.strafeSpeed = self.maxStrafeSpeed

            self.totalSpeed = math.sqrt(self.strafeSpeed * self.strafeSpeed + self.speed * self.speed)
                    
            self.position[0] += (self.currentVector[0] * timeDelta * self.speed + self.currentVector[1] * self.strafeSpeed * timeDelta)
            self.position[1] += (self.currentVector[1] * timeDelta * self.speed - self.currentVector[0] * self.strafeSpeed * timeDelta)

            if self.position[0] > 992:
                self.position[0] = 992
            if self.position[0] < 32:
                self.position[0] = 32
                
            self.moveAccumulator += self.totalSpeed * timeDelta
            self.updateScreenPosition(tiledLevel.positionOffset)

            self.sprite.image = pygame.transform.rotate(self.original_image, self.newFacingAngle)
            self.sprite.rect = self.sprite.image.get_rect()
            self.sprite.rect.center = self.rotPoint([self.screen_position[0], self.screen_position[1]+self.sprite_rot_centre_offset[1]], self.screen_position, -self.newFacingAngle)


    def addHealth(self, health):
        self.health += health
        if self.health > self.maxHealth:
            self.health = self.maxHealth

    def takeDamage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        self.shouldFlashSprite = True

    def testMonsterCollision(self, tempPlayerRect, monster):
        collided = False
        if (tempPlayerRect.colliderect(monster.sprite.rect)):
            collided = self.isIntersecting(monster)
        return collided
    
    def testTileCollision(self, tempPlayerRect, testScreenPosition, tile):
        collided = (False,[])
        if (tempPlayerRect.colliderect(tile.sprite.rect)):
            collided = self.isIntersectingTile(tile, testScreenPosition)
        return collided

    def testProjectileCollision(self, projectileRect):
        collided = False
        if (self.sprite.rect.colliderect(projectileRect)):
            if (self.testPointInCircle(projectileRect.topleft, self.screen_position, self.collideRadius)) or (self.testPointInCircle(projectileRect.topright, self.screen_position, self.collideRadius)) or (self.testPointInCircle(projectileRect.bottomleft, self.screen_position, self.collideRadius)) or (self.testPointInCircle(projectileRect.bottomright, self.screen_position, self.collideRadius)):
                collided = True
        return collided

    def testPickUpCollision(self, pickUpRect):
        collided = False
        if (self.sprite.rect.colliderect(pickUpRect)):
            if (self.testPointInCircle(pickUpRect.topleft, self.screen_position, self.collideRadius)) or (self.testPointInCircle(pickUpRect.topright, self.screen_position, self.collideRadius)) or (self.testPointInCircle(pickUpRect.bottomleft, self.screen_position, self.collideRadius)) or (self.testPointInCircle(pickUpRect.bottomright, self.screen_position, self.collideRadius)):
                collided = True
        return collided

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

    def testPointInCircle(self, point, circlePos, circleRadius):
        return (point[0] - circlePos[0])**2 + (point[1] - circlePos[1])**2 < circleRadius**2
    
    #tiles positions are in screen space currently
    def isIntersectingTile(self, tile, testScreenPosition):
        collided = False
        collisionPositions = []
        for collisionShape in tile.tileData.collisionShapes:
            if collisionShape[0] == "circle":
                distance = math.sqrt((testScreenPosition[0] - tile.position[0]) * (testScreenPosition[0] - tile.position[0]) + (testScreenPosition[1] - tile.position[1]) * (testScreenPosition[1] - tile.position[1]))
                if abs((self.collideRadius - collisionShape[1])) <= distance and distance <= (self.collideRadius + collisionShape[1]):
                    collided = True
                    shapeCentre = [0.0,0.0]
                    shapeCentre[0] = tile.position[0]
                    shapeCentre[1] = tile.position[1]
                    collisionPositions.append(shapeCentre)
            elif collisionShape[0] == "rect":             
                result = self.testRectInCircle(collisionShape[2], testScreenPosition, self.collideRadius)
                #result = [False,[]]
                if result[0]:
                    #print("self.screen_position: " + str(self.screen_position[0]) + ", " + str(self.screen_position[1]))
                    #print("tempPlayerRect.center: " + str(testScreenPosition[0]) + ", " + str(testScreenPosition[1]))
                    collided = True
                    
                    if len(result[1])> 0:
                        for point in result[1]:
                            collisionPositions.append(point)
                    else:
                        shapeCentre = [0.0,0.0]
                        shapeCentre[0] = collisionShape[2].centerx
                        shapeCentre[1] = collisionShape[2].centery
                        collisionPositions.append(shapeCentre)

        return (collided,collisionPositions)

    def testPointInCircle(self, point, circlePos, circleRadius):
        return (point[0] - circlePos[0])**2 + (point[1] - circlePos[1])**2 < circleRadius**2

    def testRectInCircle(self, rect, circlePosition, circleRadius):
        centreIn = self.testPointInCircle(rect.center, circlePosition, circleRadius)
        topIn = self.lineIntersectCircle( circlePosition, circleRadius, rect.topleft, rect.topright) 
        bottomIn = self.lineIntersectCircle(circlePosition, circleRadius, rect.bottomleft, rect.bottomright)
        leftIn = self.lineIntersectCircle(circlePosition, circleRadius, rect.topleft, rect.bottomleft)
        rightIn = self.lineIntersectCircle(circlePosition, circleRadius, rect.topright, rect.bottomright)
        
        collisionPoints = []
        if topIn[0]:
            collisionPoints.append(topIn[1])
        if bottomIn[0]:
            collisionPoints.append(bottomIn[1])
        if leftIn[0]:
            collisionPoints.append(leftIn[1])
        if rightIn[0]:
            collisionPoints.append(rightIn[1])
            
        return (centreIn or topIn[0] or bottomIn[0] or leftIn[0] or rightIn[0], collisionPoints)


    def lineIntersectCircle(self, circleCentre,circleRadius, lineStart,lineEnd):
        intersects = False
        circleCentreVec = pygame.math.Vector2(circleCentre)
        lineStartVec = pygame.math.Vector2(lineStart)
        lineEndVec = pygame.math.Vector2(lineEnd)
        Q = circleCentreVec             # Centre of circle
        r = circleRadius                # Radius of circle
        P1 = lineStartVec               # Start of line segment
        V = lineEndVec - P1             # Vector along line segment

        a = V.dot(V)
        b = 2 * V.dot(P1 - Q)
        c = P1.dot(P1) + Q.dot(Q) - 2 * P1.dot(Q) - r**2

        disc = b**2 - 4 * a * c
        if disc < 0:
            return (intersects, [0.0,0.0]) # False

        sqrt_disc = math.sqrt(disc)
        t1 = (-b + sqrt_disc) / (2 * a)
        t2 = (-b - sqrt_disc) / (2 * a)

        if not (0 <= t1 <= 1 or 0 <= t2 <= 1):
            return (intersects, [0.0,0.0]) # False

        t = max(0, min(1, - b / (2 * a)))
        intersects = True
        intersectionVec = P1 + t * V
        return (intersects, [intersectionVec.x,intersectionVec.y])

        
    def isIntersecting(self, c2):
        distance = math.sqrt((self.position[0] - c2.position[0]) * (self.position[0] - c2.position[0]) + (self.position[1] - c2.position[1]) * (self.position[1] - c2.position[1]));
        if abs((self.collideRadius - c2.collideRadius)) <= distance and distance <= (self.collideRadius + c2.collideRadius):
            return True
        else:
            return False


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

        if self.shouldDrawCollisionObj:
            for colObjRect in self.collisionObjRects:
                #print("Collide pos: " + str(colObjRect[0]) + ", " + str(colObjRect[1]))
                pygame.draw.rect(screen, pygame.Color(255, 0, 0), colObjRect)
    
    def distanceFromLine(self, point, line):

        x1 = line[0][0]
        y1 = line[0][1]
        x2 = line[1][0]
        y2 = line[1][1]
        x3 = point[0]
        y3 = point[1]
        
        
        px = x2-x1
        py = y2-y1

        something = px*px + py*py

        u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py

        dx = x - x3
        dy = y - y3

        # Note: If the actual distance does not matter,
        # if you only want to compare what this function
        # returns to other results of this function, you
        # can just return the squared distance instead
        # (i.e. remove the sqrt) to gain a little performance

        dist = math.sqrt(dx*dx + dy*dy)

        return dist

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

class RespawnPlayer():
    def __init__(self, player):
        self.controlScheme = player.scheme
        
        self.respawnTimer = 2.0
        self.timeToSpawn = False
        self.hasRespawned = False

    def update(self, frameTimeMS):
        self.respawnTimer -= (frameTimeMS/1000.0)
        if self.respawnTimer < 0.0:
            self.timeToSpawn = True


class PlayerScore():
    def __init__(self, screenPosition):
        self.screenPosition = screenPosition
        self.score = 0
