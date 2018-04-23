import math
import random
import pygame
from bullet import Bullet


class MonsterPath:
    def __init__(self):
        self.startWaypoint = [0, 0]
        self.waypoints = []
        self.waypointRadius = 32


class BaseMonster:
    def __init__(self, type_id, wave_order, start_pos, all_monster_sprites,
                 play_area, tiled_level, explosions_sprite_sheet):

        self.id = type_id
        self.waveOrder = wave_order
        self.startPos = start_pos
        self.playArea = play_area
        self.tiledLevel = tiled_level
        self.explosionsSpriteSheet = explosions_sprite_sheet

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

        self.sprite_rot_offset = [0.0, 0.0]
                       
        self.sprite.rect = self.image.get_rect()

        self.sprite.rect.center = self.startPos

        self.position = [float(self.sprite.rect.center[0]), float(self.sprite.rect.center[1])]

        self.screen_position = [0, 0]
        self.screen_position[0] = self.position[0]
        self.screen_position[1] = self.position[1]

        self.update_screen_position(self.tiledLevel.positionOffset)
        
        self.sprite.image = self.image

        self.changeDirectionTime = 5.0
        self.changeDirectionAccumulator = 0.0

        self.currentVector = [0.0, 1.0]

        self.rotate_sprite()
    
        self.shouldDie = False
        
        self.spriteNeedsUpdate = True
        self.allMonsterSprites = all_monster_sprites
        self.allMonsterSprites.add(self.sprite)

        self.health = 100

        self.slowDownPercentage = 1.0
        self.collideRadius = 27

        self.isWanderingAimlessly = True
        self.randomTargetChangeTime = random.uniform(3.0, 15.0)
        self.randomTargetChangeAcc = 0.0

        self.timeToHomeInOnPlayer = False
        self.monsterHomeOnTargetTime = random.uniform(0.3, 1.5)
        self.monsterHomeOnTargetAcc = 0.0

        self.isTimeToStartAttack = True
        self.attackTimeAcc = 0.0

        self.isAttacking = False
        self.shouldDoAttackDamage = False
        self.attackAnimAcc = 0.0
        self.attackAnimTotalTime = 0.8

        self.barrelExitPos = [0.0, 0.0]
        self.barrelForwardOffset = 32
        self.barrelSideOffset = 6

        self.spriteFlashAcc = 0.0
        self.spriteFlashTime = 0.15
        self.shouldFlashSprite = False
        self.activeFlashSprite = False

        self.botherTimeAcc = 0.0
        self.fleeing = False
        self.fleeSpeed = 800.0

        self.moveSpeed = 300.0
        self.dodgeSpeed = 300.0

        vec_list = [-1, 1]
        self.dodgeVector = [float(random.choice(vec_list)), 0.0]

        self.randomDodgeChangeAcc = 0.0
        self.randomDodgeChangeTime = 0.5

        self.match_player_vector = [0.0, 0.0]

        self.oldFacingAngle = 0.0

    def update_sprite(self, time_delta, time_multiplier):
        if self.spriteNeedsUpdate:
            self.spriteNeedsUpdate = False
            self.sprite.image = self.image

        if self.shouldFlashSprite and not self.shouldDie:
            self.spriteFlashAcc += time_delta * time_multiplier
            if self.spriteFlashAcc > self.spriteFlashTime:
                self.spriteFlashAcc = 0.0
                self.shouldFlashSprite = False
                if self.activeFlashSprite:
                    self.allMonsterSprites.remove(self.flashSprite)
                    self.activeFlashSprite = False
            else:
                lerp_value = self.spriteFlashAcc/self.spriteFlashTime
                flash_alpha = self.lerp(255, 0, lerp_value)
                flash_image = self.sprite.image.copy()
                flash_image.fill((0, 0, 0, flash_alpha), None, pygame.BLEND_RGBA_MULT)
                flash_image.fill((255, 255, 255, 0), None, pygame.BLEND_RGBA_ADD)
                self.flashSprite.image = flash_image
                self.flashSprite.rect = self.flashSprite.image.get_rect()
                self.flashSprite.rect.center = self.rot_point([self.screen_position[0],
                                                               self.screen_position[1] + self.sprite_rot_offset[1]],
                                                              self.screen_position, -self.oldFacingAngle)
                if not self.activeFlashSprite:
                    self.allMonsterSprites.add(self.flashSprite)
                    self.activeFlashSprite = True

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        self.shouldFlashSprite = True

    def update_movement_and_collision(self, time_delta, time_multiplier, player,
                                      new_explosions, tiled_level, projectiles, pick_up_spawner):

        for explosion in new_explosions:
            if self.test_explosion_collision(explosion):
                self.take_damage(explosion.damage.amount)
        if self.health <= 0:
            self.shouldDie = True

        # idle AI state
        if self.isWanderingAimlessly and not player.shouldDie:
            if tiled_level.is_position_on_screen(self.position):
                self.isWanderingAimlessly = False
            elif self.randomTargetChangeAcc < self.randomTargetChangeTime:
                self.randomTargetChangeAcc += time_delta

        if self.fleeing:
            self.currentVector = [0.0, 1.0]
            self.position[0] += self.fleeSpeed * time_delta * self.currentVector[0]
            self.position[1] += self.fleeSpeed * time_delta * self.currentVector[1]
        # preparing to shoot AI state
        if not self.isWanderingAimlessly and not self.fleeing and not player.shouldDie:

            wave_position = [self.position[0], self.position[1] - (64 * self.waveOrder) - 32]
            if tiled_level.is_position_on_screen(wave_position):
                self.match_player_vector = [0.0, -1.0]
                self.position[1] += player.speed * time_delta * self.match_player_vector[1]

            self.position[0] += self.dodgeSpeed * time_delta * self.dodgeVector[0]
            self.position[1] += self.dodgeSpeed * time_delta * self.dodgeVector[1]

            if self.randomDodgeChangeAcc < self.randomDodgeChangeTime:
                self.randomDodgeChangeAcc += time_delta
            else:
                self.randomDodgeChangeAcc = 0.0
                self.randomDodgeChangeTime = float(random.uniform(5, 10))/20.0
                vec_list = [-1, 1]
                self.dodgeVector = [float(random.choice(vec_list)), 0.0]
                
            if self.position[0] < 32:
                self.position[0] = 32.0
            if self.position[0] > 992:
                self.position[0] = 992.0

            if self.id == "spherical":
                x_dist = float(player.position[0]) - float(self.position[0])
                y_dist = float(player.position[1]) - float(self.position[1])
                distance_to_player = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))

                if distance_to_player > 0.0:
                    self.currentVector = [x_dist/distance_to_player, y_dist/distance_to_player]

                self.rotate_sprite()
            else:
                self.currentVector = [0.0, 1.0]

            if self.botherTimeAcc > self.botherPlayerTime:
                self.fleeing = True
            else:
                self.botherTimeAcc += time_delta

            if self.attackTimeAcc < self.attackTimeDelay:
                self.attackTimeAcc += time_delta * time_multiplier
            else:
                if tiled_level.is_position_on_screen(self.position):
                    self.attackTimeAcc = random.random()/10.0  # add a small random amount to the reload delay
                    self.isTimeToStartAttack = True
                
            if self.isTimeToStartAttack:
                self.isTimeToStartAttack = False
                self.isAttacking = True
                if self.id == "spherical":
                    projectiles.append(Bullet(self.position, self.currentVector, self.perBulletDamage,
                                              self.bulletSpeed, self.explosionsSpriteSheet, True))
                if self.id == "mechanical":
                    bullet1_pos = [self.position[0]+20, self.position[1]]
                    bullet2_pos = [self.position[0]-20, self.position[1]]
                    projectiles.append(Bullet(bullet1_pos, self.currentVector, self.perBulletDamage,
                                              self.bulletSpeed, self.explosionsSpriteSheet, True))
                    projectiles.append(Bullet(bullet2_pos, self.currentVector, self.perBulletDamage,
                                              self.bulletSpeed, self.explosionsSpriteSheet, True))
                
        # shooting/reloading
        if self.isAttacking:
            self.attackAnimAcc += time_delta * time_multiplier
            if self.attackAnimAcc > self.attackAnimTotalTime:
                self.attackAnimAcc = 0.0
                self.isAttacking = False

        self.update_screen_position(self.tiledLevel.positionOffset)
        self.sprite.rect.center = self.screen_position

        if self.shouldDie:
            self.allMonsterSprites.remove(self.sprite)
            if self.activeFlashSprite:
                self.allMonsterSprites.remove(self.flashSprite)
                self.activeFlashSprite = False
            self.try_pick_up_spawn(pick_up_spawner)

    def update_screen_position(self, world_offset):
        self.screen_position[0] = self.position[0] - world_offset[0]
        self.screen_position[1] = self.position[1] - world_offset[1]
            
    @staticmethod
    def get_random_point_in_radius_of_point(point, radius):
        t = 2*math.pi*random.random()
        u = random.random() + random.random()
        if u > 1:
            r = 2-u
        else:
            r = u
        return [point[0] + radius*r*math.cos(t), point[1] + radius*r*math.sin(t)]

    @staticmethod
    def test_point_in_explosion(point, explosion):
        return (point[0] - explosion.position[0])**2 + (point[1] - explosion.position[1])**2 < explosion.radius**2

    def test_projectile_collision(self, projectile_rect):
        collided = False
        if self.sprite.rect.colliderect(projectile_rect):
            tl_collision = self.test_point_in_circle(projectile_rect.topleft,
                                                     self.screen_position,
                                                     self.collideRadius)
            tr_collision = self.test_point_in_circle(projectile_rect.topright,
                                                     self.screen_position,
                                                     self.collideRadius)
            bl_collision = self.test_point_in_circle(projectile_rect.topleft,
                                                     self.screen_position,
                                                     self.collideRadius)
            br_collision = self.test_point_in_circle(projectile_rect.topright,
                                                     self.screen_position,
                                                     self.collideRadius)
            if tl_collision or tr_collision or bl_collision or br_collision:
                collided = True
        return collided

    @staticmethod
    def test_point_in_circle(point, circle_pos, circle_radius):
        return (point[0] - circle_pos[0]) ** 2 + (point[1] - circle_pos[1]) ** 2 < circle_radius ** 2
    
    def test_monster_collision(self, temp_player_rect, monster):
        collided = False
        if temp_player_rect.colliderect(monster.sprite.rect):
            collided = self.is_intersecting(monster)
        return collided
    
    def test_tile_collision(self, temp_player_rect, tile):
        collided = False
        if temp_player_rect.colliderect(tile.sprite.rect):
            collided = self.is_intersecting_tile(tile)
        return collided

    # tiles positions are in screen space currently
    def is_intersecting_tile(self, c2):
        x_dist = self.screen_position[0] - c2.position[0]
        y_dist = self.screen_position[1] - c2.position[1]
        distance = math.sqrt(x_dist ** 2 + y_dist ** 2)
        if abs((self.collideRadius - c2.collideRadius)) <= distance <= (self.collideRadius + c2.collideRadius):
            return True
        else:
            return False

    def is_intersecting(self, c2):
        x_dist = self.screen_position[0] - c2.position[0]
        y_dist = self.screen_position[1] - c2.position[1]
        distance = math.sqrt(x_dist ** 2 + y_dist ** 2)
        if abs((self.collideRadius - c2.collideRadius)) <= distance <= (self.collideRadius + c2.collideRadius):
            return True
        else:
            return False

    def test_explosion_collision(self, explosion):
        collided = False
        if self.sprite.rect.colliderect(explosion.sprite.rect):
            collided = self.is_explosion_intersecting(explosion) or self.is_circle_inside(explosion)
        return collided
    
    def is_explosion_intersecting(self, c2):
        x_dist = self.screen_position[0] - c2.position[0]
        y_dist = self.screen_position[1] - c2.position[1]
        distance = math.sqrt(x_dist ** 2 + y_dist ** 2)
        if abs((self.collideRadius - c2.collideRadius)) <= distance <= (self.collideRadius + c2.collideRadius):
            return True
        else:
            return False

    def is_circle_inside(self, c2):
        x_dist = self.screen_position[0] - c2.position[0]
        y_dist = self.screen_position[1] - c2.position[1]
        distance = math.sqrt(x_dist ** 2 + y_dist ** 2)
        if self.collideRadius < c2.collideRadius:
            is_inside = distance + self.collideRadius <= c2.collideRadius
        else:
            is_inside = distance + c2.collideRadius <= self.collideRadius
        return is_inside

    def set_average_speed(self, average_speed):
        self.moveSpeed = random.randint(int(average_speed * 0.75), int(average_speed * 1.25))
        return self.moveSpeed

    def get_random_point_on_screen(self):
        random_x = random.randint(32, self.playArea[0]-32)
        random_y = random.randint(32, self.playArea[1]-32)
        return [random_x, random_y]

    def rotate_sprite(self):
        direction_magnitude = math.sqrt(self.currentVector[0] ** 2 + self.currentVector[1] ** 2)
        if direction_magnitude > 0.0:
            unit_dir_vector = [self.currentVector[0]/direction_magnitude, self.currentVector[1]/direction_magnitude]
            self.oldFacingAngle = math.atan2(-unit_dir_vector[0], -unit_dir_vector[1])*180/math.pi
            monster_centre_position = self.sprite.rect.center
            self.image = pygame.transform.rotate(self.original_image, self.oldFacingAngle)
            self.sprite.image = self.image
            self.sprite.rect = self.image.get_rect()
            self.sprite.rect.center = monster_centre_position

    def try_pick_up_spawn(self, pickup_spawner):
        pickup_spawner.try_spawn(self.position)

    @staticmethod
    def rot_point(point, axis, ang):
        """ Orbit. calculates the new loc for a point that rotates a given num of degrees around an axis point,
        +clockwise, -anticlockwise -> tuple x,y
        """
        ang -= 90
        x, y = point[0] - axis[0], point[1] - axis[1]
        radius = math.sqrt(x*x + y*y)  # get the distance between points

        r_ang = math.radians(ang)      # convert ang to radians.

        h = axis[0] + (radius * math.cos(r_ang))
        v = axis[1] + (radius * math.sin(r_ang))

        return [h, v]

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0 - c) * a)

    def draw_collision_rect(self, screen):
        ck = (127, 33, 33)
        s = pygame.Surface((self.sprite.rect.width, self.sprite.rect.height))
        s.fill(ck)
        s.set_colorkey(ck)
        pygame.draw.rect(s, pygame.Color(100, 255, 100),
                         pygame.Rect([0, 0], [self.sprite.rect.width, self.sprite.rect.height]))
        s.set_alpha(60)
        screen.blit(s, [int(self.sprite.rect.left), int(self.sprite.rect.top)])
        
    def draw_collision_radius_circle(self, screen):
        ck = (127, 33, 33)
        int_position = [0, 0]
        int_position[0] = int(self.screen_position[0]-self.collideRadius)
        int_position[1] = int(self.screen_position[1]-self.collideRadius)
        s = pygame.Surface((self.collideRadius*2, self.collideRadius*2))

        # first, "erase" the surface by filling it with a color and
        # setting this color as colorkey, so the surface is empty
        s.fill(ck)
        s.set_colorkey(ck)

        pygame.draw.circle(s, pygame.Color(100, 100, 255), (self.collideRadius, self.collideRadius), self.collideRadius)

        # after drawing the circle, we can set the 
        # alpha value (transparency) of the surface
        s.set_alpha(100)
        screen.blit(s, int_position)
