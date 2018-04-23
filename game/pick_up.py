import pygame
import random


class PickUpSpawner:
    def __init__(self, pick_ups, all_pick_up_sprites):
        self.pick_ups = pick_ups
        self.allPickUpSprites = all_pick_up_sprites
        self.health_image = pygame.image.load("images/pick_ups/health.png")

    def try_spawn(self, spawn_position):
        random_roll = random.randint(0, 100)
        if random_roll < 25:
            self.pick_ups.append(PickUp(spawn_position, self.health_image, "health", self.allPickUpSprites))
        

class PickUp:
    def __init__(self, start_pos, image, type_name, all_pick_up_sprites):
        self.world_position = [start_pos[0], start_pos[1]]
        self.typeName = type_name
        self.image = image
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = self.image
        self.sprite.rect = self.image.get_rect()  
        self.sprite.rect.center = start_pos

        self.position = [float(self.sprite.rect.center[0]), float(self.sprite.rect.center[1])]

        self.allPickUpSprites = all_pick_up_sprites
        self.allPickUpSprites.add(self.sprite)
        self.shouldDie = False

    def update_movement_and_collision(self, player, time_delta, tiled_level):

        self.world_position[1] -= player.speed / 3 * time_delta
        
        self.position[0] = self.world_position[0] - tiled_level.positionOffset[0]
        self.position[1] = self.world_position[1] - tiled_level.positionOffset[1]
        self.sprite.rect.center = self.position
        
        if player.test_pick_up_collision(self.sprite.rect):
            self.shouldDie = True
            if self.typeName == "health":
                player.add_health(25)

            self.allPickUpSprites.remove(self.sprite)
