# -----------------------------------
# Scroll down for the challenges!
# -----------------------------------

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
                # ---------------------------------------------
                # Challenge 1 - APPROX 4 LINES OF CODE
                # ---------------------------------------------
                #
                # Create a collision loop for the player's
                # bullets here to replace the 'pass' command below.
                #
                # It needs to do three things -
                #
                # 1. Check if this bullet's sprite rectangle
                #    collides with all the monsters.
                #
                # 2. Kill the bullet if it does hit a monster.
                #
                # 3. Do some damage to a monster if we hit it.
                #
                # HINTS
                # -------
                #
                # - Use a for loop to loop through all the monsters.
                # - There is a function in the monster class
                #   called 'test_projectile_collision' that will test
                #   if a bullet has hit a particular monster.
                # - You can find the bullet sprite's rectangle
                #   at: self.sprite.rect
                # - There is also a function on the monster class
                #   called 'take_damage' that will apply damage
                #   to a monster and trigger the correct visual
                #   effects.
                # - There is a class variable at self.damage that
                #   contains the amount of damage a bullet should do.
                # - Killing a bullet is just matter of setting
                #   it's class variable called 'shouldDie' to
                #   True.
                # - if you get stuck, have a look below at the loop
                #   for monster's bullets hitting the player for
                #   ideas
                # ----------------------------------------------
                pass

                # ---------------------------------------------------------------
                # Challenge 2 - part 1
                # ---------------------
                #
                # The collision detection used in this game is fairly
                # basic. The 'test_projectile_collision' function used in
                # challenge 1 does two things:
                #
                # 1. It first tests if axis aligned rectangles surrounding
                #    the bullet and the monster overlap. Axis aligned rectangles
                #    are simply ones where the sides are horizontal and vertical
                #    rather than rotated. This type of shape is very quick to
                #    test for overlaps and by using one that fully contains our
                #    sprites, no matter how they are rotated we can be sure we
                #    won't miss any genuine collisions.
                #
                # 2. Then, because using only axis aligned rectangles is not very accurate
                #    to the shape of our sprites, we do a second overlap test
                #    on only those sprites that we found to be colliding in the
                #    first test. This time we do a 'circle with axis aligned rectangle'
                #    overlap test with the monsters represented by circles, and the
                #    bullets still represented by axis aligned rectangles. This test is
                #    slower to perform but more accurate to the actual shapes of some
                #    of our monster sprites. If we only did the second test on all of our
                #    monsters the code would still be just as accurate, but it would run
                #    more slowly as we wouldn't be quickly eliminating most monsters from
                #    taking the slower, more accurate test.
                #
                #
                # Your second challenge is to think of some ideas for how you might
                # improve the collision detection used in this game to better
                # meet the three goals originally outlined on the worksheet.
                #
                # To help you think I've added some code to visualise the collision
                # shapes used in this game. Head over to the 'scrolling_shooter'
                # code file and scroll down to the rendering part of the game loop to
                # find and activate this code.
                #
                # I will wander the room to quiz you on your thoughts!
                # -------------------------------------------------------------------
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
