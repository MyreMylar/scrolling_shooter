import math
import pygame

from game.projectile import Projectile


class Bullet(Projectile):
    def __init__(self, start_pos, initial_heading_vector, damage,
                 bullet_speed, explosions_sprite_sheet, is_ai_bullet=False):

        self.isAIBullet = is_ai_bullet
        self.explosionsSpriteSheet = explosions_sprite_sheet
        self.imageName = "images/bullet.png"
        self.original_image = pygame.image.load(self.imageName).convert_alpha()
 
        self.sprite = pygame.sprite.Sprite()

        self.currentVector = [initial_heading_vector[0], initial_heading_vector[1]]
        # ensure bullet vector is normalised
        direction_magnitude = max(0.001, math.sqrt(self.currentVector[0] ** 2 + self.currentVector[1] ** 2))
        self.currentVector = [self.currentVector[0]/direction_magnitude, self.currentVector[1]/direction_magnitude]

        self.position = [float(start_pos[0]), float(start_pos[1])]
        self.world_position = [float(start_pos[0]), float(start_pos[1])]
        
        # calc facing angle
        facing_angle = math.atan2(-self.currentVector[0], -self.currentVector[1])*180/math.pi
        self.image = pygame.transform.rotate(self.original_image, facing_angle)
        self.sprite.image = self.image
        self.sprite.rect = self.image.get_rect()
        self.sprite.rect.center = self.position

        self.shouldDie = False

        self.bulletSpeed = bullet_speed
        self.damage = damage

        self.shotRange = 1024.0

    def update_sprite(self, all_bullet_sprites):
        all_bullet_sprites.add(self.sprite)
        return all_bullet_sprites

    def update_movement_and_collision(self, tiled_level, collideable_tiles, players,
                                      monsters, time_delta, new_explosions, explosions):
        if self.shotRange <= 0.0:
            self.shouldDie = True

        if not self.shouldDie:
            if not self.isAIBullet:
                for monster in monsters:
                    if monster.test_projectile_collision(self.sprite.rect):
                        monster.take_damage(self.damage)
                        self.shouldDie = True

            else:  # is a monster bullet
                for player in players:
                    if player.test_projectile_collision(self.sprite.rect):
                        player.take_damage(self.damage)
                        self.shouldDie = True 

            self.shotRange -= time_delta * self.bulletSpeed
            self.world_position[0] += (self.currentVector[0] * time_delta * self.bulletSpeed)
            self.world_position[1] += (self.currentVector[1] * time_delta * self.bulletSpeed)
            
            self.position[0] = self.world_position[0] - tiled_level.positionOffset[0]
            self.position[1] = self.world_position[1] - tiled_level.positionOffset[1]

            self.sprite.rect.center = self.position

    def draw_collision_rect(self, screen):
        ck = (127, 33, 33)
        s = pygame.Surface((self.sprite.rect.width, self.sprite.rect.height))
        s.fill(ck)
        s.set_colorkey(ck)
        pygame.draw.rect(s, pygame.Color(100, 200, 100), pygame.Rect([0, 0], [self.sprite.rect.width,
                                                                              self.sprite.rect.height]))
        s.set_alpha(160)
        screen.blit(s, [int(self.sprite.rect.left), int(self.sprite.rect.top)])
