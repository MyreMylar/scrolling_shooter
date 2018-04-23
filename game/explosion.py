import random
import pygame
from game.damage import Damage


class Explosion:
    def __init__(self, start_pos, explosion_sheet, size, damage_amount, damage_type):

        self.radius = size
        self.collideRadius = self.radius
        self.explosionSheet = explosion_sheet
        self.explosionFrames = 16
        self.explosionImages = []
        random_explosion_int = random.randrange(0, 512, 64)
        for i in range(0, self.explosionFrames):
            x_start_index = (i * 64)
            explosion_frame = self.explosionSheet.subsurface(pygame.Rect(x_start_index+1,
                                                                         random_explosion_int+1, 62, 62))
            explosion_frame = pygame.transform.scale(explosion_frame, (self.radius*2, self.radius*2))
            self.explosionImages.append(explosion_frame)
        self.sprite = pygame.sprite.Sprite()      
        self.sprite.image = self.explosionImages[0]
                
        self.sprite.rect = self.explosionImages[0].get_rect()  
        self.sprite.rect.center = start_pos

        self.position = [float(self.sprite.rect.center[0]), float(self.sprite.rect.center[1])]
        self.world_position = [float(self.sprite.rect.center[0]), float(self.sprite.rect.center[1])]
        
        self.shouldDie = False
        self.lifeTime = 0.45
        self.time = self.lifeTime
        self.frameTime = self.lifeTime/self.explosionFrames
        self.frame = 1

        self.damage = Damage(damage_amount, damage_type)
        
    def update_sprite(self, all_explosion_sprites, time_delta, time_multiplier, tiled_level):
       
        self.position[0] = self.world_position[0] - tiled_level.positionOffset[0]
        self.position[1] = self.world_position[1] - tiled_level.positionOffset[1]
        self.sprite.rect.center = self.position
        
        self.time -= time_delta * time_multiplier
        if self.time < 0.0:
            self.shouldDie = True

        if self.frame < self.explosionFrames and (self.lifeTime - self.time) > (self.frameTime * self.frame):
            self.sprite.image = self.explosionImages[self.frame]
            self.frame += 1

        all_explosion_sprites.add(self.sprite)
            
        return all_explosion_sprites

    def update_movement_and_collision(self):
        pass
