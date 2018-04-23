import math
import pygame
from pygame.locals import *

from bullet import Bullet


class ControlScheme:
    def __init__(self):
        self.moveLeft = K_a
        self.moveRight = K_d
        self.fire = K_SPACE


class Player:
    def __init__(self, start_pos, tiled_level, control_scheme, explosions_sprite_sheet):
        
        self.scheme = control_scheme
        self.explosionsSpriteSheet = explosions_sprite_sheet
        self.imageName = "images/player_2.png"
        self.original_image = pygame.image.load(self.imageName).convert_alpha()
        self.image = self.original_image.copy()

        self.sprite = pygame.sprite.Sprite()
        self.testCollisionSprite = pygame.sprite.Sprite()
        self.flashSprite = pygame.sprite.Sprite() 
        self.sprite.image = self.image        
        self.sprite.rect = self.image.get_rect()  
        self.sprite.rect.center = start_pos

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
       
        self.position = [float(self.sprite.rect.center[0]), float(self.sprite.rect.center[1])]
        self.playerMoveTarget = self.position
        self.distanceToMoveTarget = 0.0
        self.currentVector = [0.0, -1.0]
        self.newFacingAngle = 0

        self.screen_position = [self.position[0], self.position[1]]

        self.update_screen_position(tiled_level.positionOffset)

        direction_magnitude = math.sqrt(self.currentVector[0] ** 2 + self.currentVector[1] ** 2)
        if direction_magnitude > 0.0:
            unit_dir_vector = [self.currentVector[0]/direction_magnitude, self.currentVector[1]/direction_magnitude]
            self.newFacingAngle = math.atan2(-unit_dir_vector[0], -unit_dir_vector[1])*180/math.pi

        self.oldFacingAngle = self.newFacingAngle

        self.sprite.rect.center = self.rot_point([self.screen_position[0],
                                                  self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                                 self.screen_position, -self.newFacingAngle)

        self.moveLeft = False
        self.moveRight = False

        self.perBulletDamage = 25
        
        self.playerFireTarget = [10000, 10000]

        self.spriteFlashAcc = 0.0
        self.spriteFlashTime = 0.15
        self.shouldFlashSprite = False

        self.isCollided = False

        self.shouldDrawCollisionObj = False
        self.collisionObjRects = []
        self.collisionObjRect = pygame.Rect(0.0, 0.0, 2.0, 2.0)

        self.shouldFire = False

    def process_event(self, event):
        if event.type == KEYDOWN:  # key pressed
            if event.key == self.scheme.moveLeft:
                self.moveLeft = True
            if event.key == self.scheme.moveRight:
                self.moveRight = True
            if event.key == self.scheme.fire:
                self.shouldFire = True

        if event.type == KEYUP:  # key released
            if event.key == self.scheme.moveLeft:
                self.moveLeft = False
            if event.key == self.scheme.moveRight:
                self.moveRight = False
        
    @staticmethod
    def get_world_position_from_screen_pos(screen_pos, world_offset):
        world_pos = [screen_pos[0] + world_offset[0], screen_pos[1] + world_offset[1]]
        return world_pos
    
    def update_screen_position(self, world_offset):
        self.screen_position[0] = self.position[0] - world_offset[0]
        self.screen_position[1] = self.position[1] - world_offset[1]

    def update_sprite(self, all_sprites, time_delta):
        all_sprites.add(self.sprite)
        
        if self.shouldFlashSprite:
            self.spriteFlashAcc += time_delta
            if self.spriteFlashAcc > self.spriteFlashTime:
                self.spriteFlashAcc = 0.0
                self.shouldFlashSprite = False
            else:
                lerp_value = self.spriteFlashAcc/self.spriteFlashTime
                flash_alpha = self.lerp(255, 0, lerp_value)
                flash_image = self.sprite.image.copy()
                flash_image.fill((0, 0, 0, flash_alpha), None, pygame.BLEND_RGBA_MULT)
                flash_image.fill((255, 255, 255, 0), None, pygame.BLEND_RGBA_ADD)
                self.flashSprite.image = flash_image
                self.flashSprite.rect = self.flashSprite.image.get_rect()
                cp = self.rot_point([self.screen_position[0],
                                     self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                    self.screen_position, -self.newFacingAngle)
                self.flashSprite.rect.center = cp
                all_sprites.add(self.flashSprite)
        return all_sprites

    def update_movement_and_collision(self, time_delta, projectiles, tiled_level, new_explosions):
        if self.health == 0:
            self.shouldDie = True
            self.speed = 0.0

        if not self.shouldDie:
            for explosion in new_explosions:
                if self.test_explosion_collision(explosion):
                    self.take_damage(explosion.damage.amount)
                
            if self.shouldFire:
                self.shouldFire = False
                bullet_damage = 10
                bullet_speed = 800.0
                bullet1_position = [self.position[0]+11, self.position[1]-24]
                bullet2_position = [self.position[0]-11, self.position[1]-24]
                bullet3_position = [self.position[0]+24, self.position[1]-20]
                bullet4_position = [self.position[0]-24, self.position[1]-20]
                bullet5_position = [self.position[0]+17, self.position[1]-22]
                bullet6_position = [self.position[0]-17, self.position[1]-22]
                projectiles.append(Bullet(bullet1_position, [0.0, -1.0], bullet_damage,
                                          bullet_speed, self.explosionsSpriteSheet))
                projectiles.append(Bullet(bullet2_position, [0.0, -1.0], bullet_damage,
                                          bullet_speed, self.explosionsSpriteSheet))
                projectiles.append(Bullet(bullet3_position, [0.0, -1.0], bullet_damage,
                                          bullet_speed, self.explosionsSpriteSheet))
                projectiles.append(Bullet(bullet4_position, [0.0, -1.0], bullet_damage,
                                          bullet_speed, self.explosionsSpriteSheet))
                projectiles.append(Bullet(bullet5_position, [0.0, -1.0], bullet_damage,
                                          bullet_speed, self.explosionsSpriteSheet))
                projectiles.append(Bullet(bullet6_position, [0.0, -1.0], bullet_damage,
                                          bullet_speed, self.explosionsSpriteSheet))

            self.speed = self.maxSpeed
            if self.moveRight or self.moveLeft:
                if self.moveRight:
                    if self.strafeSpeed > 0.0:
                        self.strafeSpeed = 0.0
                    self.strafeSpeed -= self.strafeAcceleration * time_delta
                    if abs(self.strafeSpeed) > self.maxStrafeSpeed:
                        self.strafeSpeed = -self.maxStrafeSpeed

                elif self.moveLeft:
                    if self.strafeSpeed < 0.0:
                        self.strafeSpeed = 0.0
                    self.strafeSpeed += self.strafeAcceleration * time_delta
                    if abs(self.strafeSpeed) > self.maxStrafeSpeed:
                        self.strafeSpeed = self.maxStrafeSpeed

            self.totalSpeed = math.sqrt(self.strafeSpeed * self.strafeSpeed + self.speed * self.speed)
                    
            self.position[0] += (self.currentVector[0] * time_delta * self.speed
                                 + self.currentVector[1] * self.strafeSpeed * time_delta)
            self.position[1] += (self.currentVector[1] * time_delta * self.speed
                                 - self.currentVector[0] * self.strafeSpeed * time_delta)

            if self.position[0] > 992:
                self.position[0] = 992
            if self.position[0] < 32:
                self.position[0] = 32
                
            self.moveAccumulator += self.totalSpeed * time_delta
            self.update_screen_position(tiled_level.positionOffset)

            self.sprite.image = pygame.transform.rotate(self.original_image, self.newFacingAngle)
            self.sprite.rect = self.sprite.image.get_rect()
            self.sprite.rect.center = self.rot_point([self.screen_position[0],
                                                      self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                                     self.screen_position, -self.newFacingAngle)

    def add_health(self, health):
        self.health += health
        if self.health > self.maxHealth:
            self.health = self.maxHealth

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        self.shouldFlashSprite = True

    def test_monster_collision(self, temp_player_rect, monster):
        collided = False
        if temp_player_rect.colliderect(monster.sprite.rect):
            collided = self.is_intersecting(monster)
        return collided
    
    def test_tile_collision(self, temp_player_rect, test_screen_position, tile):
        collided = (False, [])
        if temp_player_rect.colliderect(tile.sprite.rect):
            collided = self.is_intersecting_tile(tile, test_screen_position)
        return collided

    def test_projectile_collision(self, projectile_rect):
        collided = False
        if self.sprite.rect.colliderect(projectile_rect):
            if (self.test_point_in_circle(projectile_rect.topleft, self.screen_position, self.collideRadius)) or\
                    (self.test_point_in_circle(projectile_rect.topright, self.screen_position, self.collideRadius)) or\
                    (self.test_point_in_circle(projectile_rect.bottomleft, self.screen_position, self.collideRadius)) or\
                    (self.test_point_in_circle(projectile_rect.bottomright, self.screen_position, self.collideRadius)):
                collided = True
        return collided

    def test_pick_up_collision(self, pick_up_rect):
        collided = False
        if self.sprite.rect.colliderect(pick_up_rect):
            tl_collision = self.test_point_in_circle(pick_up_rect.topleft,
                                                     self.screen_position,
                                                     self.collideRadius)
            tr_collision = self.test_point_in_circle(pick_up_rect.topright,
                                                     self.screen_position,
                                                     self.collideRadius)
            bl_collision = self.test_point_in_circle(pick_up_rect.topleft,
                                                     self.screen_position,
                                                     self.collideRadius)
            br_collision = self.test_point_in_circle(pick_up_rect.topright,
                                                     self.screen_position,
                                                     self.collideRadius)
            if tl_collision or tr_collision or bl_collision or br_collision:
                collided = True
        return collided

    def test_explosion_collision(self, explosion):
        collided = False
        if self.sprite.rect.colliderect(explosion.sprite.rect):
            collided = self.is_explosion_intersecting(explosion) or self.is_circle_inside(explosion)
        return collided
    
    def is_explosion_intersecting(self, c2):
        distance = math.sqrt((self.screen_position[0] - c2.position[0]) ** 2 +
                             (self.screen_position[1] - c2.position[1]) ** 2)
        if abs((self.collideRadius - c2.collideRadius)) <= distance <= (self.collideRadius + c2.collideRadius):
            return True
        else:
            return False

    def is_circle_inside(self, c2):
        distance = math.sqrt((self.screen_position[0] - c2.position[0]) ** 2 +
                             (self.screen_position[1] - c2.position[1]) ** 2)
        if self.collideRadius < c2.collideRadius:
            is_inside = distance + self.collideRadius <= c2.collideRadius
        else:
            is_inside = distance + c2.collideRadius <= self.collideRadius
        return is_inside

    @staticmethod
    def test_point_in_circle(point, circle_pos, circle_radius):
        return (point[0] - circle_pos[0]) ** 2 + (point[1] - circle_pos[1]) ** 2 < circle_radius ** 2
    
    # tiles positions are in screen space currently
    def is_intersecting_tile(self, tile, test_screen_position):
        collided = False
        collision_positions = []
        for collisionShape in tile.tileData.collisionShapes:
            if collisionShape[0] == "circle":
                distance = math.sqrt((test_screen_position[0] - tile.position[0]) ** 2 +
                                     (test_screen_position[1] - tile.position[1]) ** 2)
                if abs((self.collideRadius - collisionShape[1])) <= distance <=\
                        (self.collideRadius + collisionShape[1]):
                    collided = True
                    shape_centre = [0.0, 0.0]
                    shape_centre[0] = tile.position[0]
                    shape_centre[1] = tile.position[1]
                    collision_positions.append(shape_centre)
            elif collisionShape[0] == "rect":             
                result = self.test_rect_in_circle(collisionShape[2], test_screen_position, self.collideRadius)
                if result[0]:
                    collided = True
                    
                    if len(result[1]) > 0:
                        for point in result[1]:
                            collision_positions.append(point)
                    else:
                        shape_centre = [0.0, 0.0]
                        shape_centre[0] = collisionShape[2].centerx
                        shape_centre[1] = collisionShape[2].centery
                        collision_positions.append(shape_centre)

        return collided, collision_positions

    def test_rect_in_circle(self, rect, circle_position, circle_radius):
        centre_in = self.test_point_in_circle(rect.center, circle_position, circle_radius)
        top_in = self.line_intersect_circle(circle_position, circle_radius, rect.topleft, rect.topright)
        bottom_in = self.line_intersect_circle(circle_position, circle_radius, rect.bottomleft, rect.bottomright)
        left_in = self.line_intersect_circle(circle_position, circle_radius, rect.topleft, rect.bottomleft)
        right_in = self.line_intersect_circle(circle_position, circle_radius, rect.topright, rect.bottomright)
        
        collision_points = []
        if top_in[0]:
            collision_points.append(top_in[1])
        if bottom_in[0]:
            collision_points.append(bottom_in[1])
        if left_in[0]:
            collision_points.append(left_in[1])
        if right_in[0]:
            collision_points.append(right_in[1])
            
        return centre_in or top_in[0] or bottom_in[0] or left_in[0] or right_in[0], collision_points

    @staticmethod
    def line_intersect_circle(circle_centre, circle_radius, line_start, line_end):
        intersects = False
        circle_centre_vec = pygame.math.Vector2(circle_centre)
        line_start_vec = pygame.math.Vector2(line_start)
        line_end_vec = pygame.math.Vector2(line_end)
        q = circle_centre_vec             # Centre of circle
        r = circle_radius                 # Radius of circle
        p1 = line_start_vec               # Start of line segment
        v = line_end_vec - p1             # Vector along line segment

        a = v.dot(v)
        b = 2 * v.dot(p1 - q)
        c = p1.dot(p1) + q.dot(q) - 2 * p1.dot(q) - r**2

        disc = b**2 - 4 * a * c
        if disc < 0:
            return intersects, [0.0, 0.0]  # False

        sqrt_disc = math.sqrt(disc)
        t1 = (-b + sqrt_disc) / (2 * a)
        t2 = (-b - sqrt_disc) / (2 * a)

        if not (0 <= t1 <= 1 or 0 <= t2 <= 1):
            return intersects, [0.0, 0.0]  # False

        t = max(0, min(1, - b / (2 * a)))
        intersects = True
        intersection_vec = p1 + t * v
        return intersects, [intersection_vec.x, intersection_vec.y]

    def is_intersecting(self, c2):
        distance = math.sqrt((self.position[0] - c2.position[0]) * (self.position[0] - c2.position[0]) + (self.position[1] - c2.position[1]) * (self.position[1] - c2.position[1]));
        if abs((self.collideRadius - c2.collideRadius)) <= distance <= (self.collideRadius + c2.collideRadius):
            return True
        else:
            return False

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

        if self.shouldDrawCollisionObj:
            for colObjRect in self.collisionObjRects:
                pygame.draw.rect(screen, pygame.Color(255, 0, 0), colObjRect)
    
    @staticmethod
    def distance_from_line(point, line):

        x1 = line[0][0]
        y1 = line[0][1]
        x2 = line[1][0]
        y2 = line[1][1]
        x3 = point[0]
        y3 = point[1]

        px = x2-x1
        py = y2-y1

        something = px*px + py*py

        u = ((x3 - x1) * px + (y3 - y1) * py) / float(something)

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


class RespawnPlayer:
    def __init__(self, player):
        self.controlScheme = player.scheme
        
        self.respawnTimer = 2.0
        self.timeToSpawn = False
        self.hasRespawned = False

    def update(self, frame_time_ms):
        self.respawnTimer -= (frame_time_ms / 1000.0)
        if self.respawnTimer < 0.0:
            self.timeToSpawn = True


class PlayerScore:
    def __init__(self, screen_position):
        self.screenPosition = screen_position
        self.score = 0
