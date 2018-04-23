import pygame
import random

class PickUpSpawner():
    def __init__(self, pick_ups, allPickUpSprites):
        self.pick_ups = pick_ups
        self.allPickUpSprites = allPickUpSprites
        self.health_image = pygame.image.load("images/pick_ups/health.png")
        

    def trySpawn(self, spawnPosition):
        randomRoll = random.randint(0, 100)
        if randomRoll < 25:
            self.pick_ups.append(PickUp(spawnPosition, self.health_image, "health", self.allPickUpSprites))
        
            

class PickUp():
    def __init__(self, startPos, image, typeName, allPickUpSprites):
        self.world_position = [startPos[0],startPos[1]]
        self.typeName = typeName
        self.image = image
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = self.image
        self.sprite.rect = self.image.get_rect()  
        self.sprite.rect.center = startPos

        self.position = [float(self.sprite.rect.center[0]),float(self.sprite.rect.center[1])]

        self.allPickUpSprites = allPickUpSprites
        self.allPickUpSprites.add(self.sprite)
        self.shouldDie = False

    def updateMovementAndCollision(self, player, timeDelta, tiledLevel):

        self.world_position[1] -= player.speed/3 * timeDelta
        
        self.position[0] = self.world_position[0] - tiledLevel.positionOffset[0]
        self.position[1] = self.world_position[1] - tiledLevel.positionOffset[1]
        self.sprite.rect.center = self.position
        
        if player.testPickUpCollision(self.sprite.rect):
            self.shouldDie = True
            if self.typeName == "health":
                player.addHealth(25)

            self.allPickUpSprites.remove(self.sprite)
        
