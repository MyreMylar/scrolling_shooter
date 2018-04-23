import pygame


class WeaponAnimation:
    def __init__(self, sprite_sheet, y_start):
        self.step_left = sprite_sheet.subsurface(pygame.Rect(0, y_start, 48, 64))
        self.stand = sprite_sheet.subsurface(pygame.Rect(48, y_start, 48, 64))
        self.step_right = sprite_sheet.subsurface(pygame.Rect(96, y_start, 48, 64))


class BaseWeapon:
    def __init__(self, sprite_sheet, y_sheet_start, explosion_sprite_sheet):
        self.animSet = WeaponAnimation(sprite_sheet, y_sheet_start)

        self.fireRateAcc = 0.0
        self.fireRate = 1.0
        self.canFire = True

        self.playerPosition = [0, 0]
        self.currentAimVector = [0, 0]
        self.explosionSpriteSheet = explosion_sprite_sheet

        self.barrelForwardOffset = 32
        self.barrelSideOffset = 6
        self.barrelExitPos = [0, 0]

        self.ammoCount = -1

    def update(self, time_delta, time_multiplier, player_position, current_aim_vector):
        if self.fireRateAcc < self.fireRate:
            self.fireRateAcc += time_delta * time_multiplier
        else:
            if self.ammoCount != 0:
                self.canFire = True

        self.playerPosition = player_position
        self.currentAimVector = current_aim_vector

        # calculate the position where the projectiles should leave the weapon
        x_offset = (self.currentAimVector[0]*self.barrelForwardOffset) -\
                   (self.currentAimVector[1]*self.barrelSideOffset)
        y_offset = (self.currentAimVector[1]*self.barrelForwardOffset) +\
                   (self.currentAimVector[0]*self.barrelSideOffset)
        barrel_x_pos = self.playerPosition[0] + x_offset
        barrel_y_pos = self.playerPosition[1] + y_offset
        self.barrelExitPos = [barrel_x_pos, barrel_y_pos]

    def fire(self, projectiles):
        pass
