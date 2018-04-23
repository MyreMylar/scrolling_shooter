import math
import pygame

from game.projectile import Projectile
from game.explosion import Explosion
from game.damage import DamageType


class Missile(Projectile):
    def __init__(self, start_pos, initial_heading_vector, damage, explosions_sprite_sheet, is_ai_bullet=False):

        self.isAIBullet = is_ai_bullet
        self.explosionsSpriteSheet = explosions_sprite_sheet
        self.imageName = "images/missile.png"
        self.original_image = pygame.image.load(self.imageName).convert_alpha()
        self.image = self.original_image.copy()
        self.sprite = pygame.sprite.Sprite()
       
        self.sprite.rect = self.image.get_rect()  
        self.sprite.rect.center = start_pos

        self.currentVector = [initial_heading_vector[0], initial_heading_vector[1]]

        self.position = [float(self.sprite.rect.center[0]), float(self.sprite.rect.center[1])]
        self.world_position = [float(self.sprite.rect.center[0]), float(self.sprite.rect.center[1])]
        self.sprite.image = self.image

        self.shouldDie = False

        self.bulletSpeed = 225.0
        self.damage = damage

        self.shotRange = 1024

        self.timeToHomeIn = False
        self.homingTimeAcc = 0.0
        self.homingTime = 0.2
        self.homingRadius = 256

    def update_sprite(self, all_bullet_sprites):
        self.sprite.image = self.image
        all_bullet_sprites.add(self.sprite)
        return all_bullet_sprites

    def update_movement_and_collision(self, tiled_level, collideable_tiles, players, monsters,
                                      time_delta, new_explosions, explosions):
        if self.isAIBullet:
            for player in players:
                if player.test_projectile_collision(self.sprite.rect):
                    self.shouldDie = True
        else:
            for monster in monsters:
                if monster.test_projectile_collision(self.sprite.rect):
                    self.shouldDie = True
        for tile in collideable_tiles:
            if tile.test_projectile_collision(self.sprite.rect):
                self.shouldDie = True

        self.shotRange -= time_delta * self.bulletSpeed
        self.world_position[0] += (self.currentVector[0] * time_delta * self.bulletSpeed)
        self.world_position[1] += (self.currentVector[1] * time_delta * self.bulletSpeed)
        
        self.position[0] = self.world_position[0] - tiled_level.positionOffset[0]
        self.position[1] = self.world_position[1] - tiled_level.positionOffset[1]
        self.sprite.rect.center = self.position

        if self.shotRange <= 0.0:
            self.shouldDie = True

        # calc facing angle
        direction_magnitude = math.sqrt(self.currentVector[0] ** 2 + self.currentVector[1] ** 2)
        unit_dir_vector = [0, 0]
        if direction_magnitude > 0.0:
            unit_dir_vector = [self.currentVector[0]/direction_magnitude, self.currentVector[1]/direction_magnitude]
        facing_angle = math.atan2(-unit_dir_vector[0], -unit_dir_vector[1])*180/math.pi

        bullet_centre_position = self.sprite.rect.center
        self.image = pygame.transform.rotate(self.original_image, facing_angle)
        self.sprite.rect = self.image.get_rect()
        self.sprite.rect.center = bullet_centre_position

        if self.shouldDie:
            new_explosion = Explosion(self.world_position, self.explosionsSpriteSheet,
                                      96, self.damage, DamageType.MISSILE)
            new_explosions.append(new_explosion)
            explosions.append(new_explosion)

    def get_closest_monster_in_radius(self, monsters):
        closest_monster_distance = 100000.0
        closest_monster_in_radius = None
        for monster in monsters:
            x_dist = self.position[0] - monster.position[0]
            y_dist = self.position[1] - monster.position[1]
            total_dist = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))
            if total_dist < self.homingRadius:
                if total_dist < closest_monster_distance:
                    closest_monster_distance = total_dist
                    closest_monster_in_radius = monster
        return closest_monster_in_radius, closest_monster_distance

    def calculate_aiming_vector(self, target, distance):
        x_direction = target.position[0] - self.position[0]
        y_direction = target.position[1] - self.position[1]
        return [x_direction/distance, y_direction/distance]
