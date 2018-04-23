import pygame

class WeaponAnimation():
    def __init__(self, sprite_sheet, yStart):
        self.step_left = sprite_sheet.subsurface(pygame.Rect(0, yStart, 48, 64))
        self.stand = sprite_sheet.subsurface(pygame.Rect(48, yStart, 48, 64))
        self.step_right = sprite_sheet.subsurface(pygame.Rect(96, yStart, 48, 64))


class BaseWeapon( ):
    def __init__(self, sprite_sheet, ySheetStart, explosionSpriteSheet):
        self.animSet = WeaponAnimation(sprite_sheet, ySheetStart)

        self.fireRateAcc = 0.0
        self.fireRate = 1.0
        self.canFire = True

        self.playerPosition = [0,0]
        self.currentAimVector = [0,0]
        self.explosionSpriteSheet = explosionSpriteSheet

        self.barrelForwardOffset = 32
        self.barrelSideOffset = 6

        self.ammoCount = -1

    def update(self, timeDelta, timeMultiplier, playerPosition, currentAimVector):
        if self.fireRateAcc < self.fireRate:
            self.fireRateAcc += timeDelta * timeMultiplier
        else:
            if self.ammoCount != 0:
                self.canFire = True

        self.playerPosition = playerPosition
        self.currentAimVector = currentAimVector

        # calculate the position where the projectiles should leave the weapon
        barrelXPos = self.playerPosition[0] + (self.currentAimVector[0]*self.barrelForwardOffset) - (self.currentAimVector[1]*self.barrelSideOffset)
        barrelYPos = self.playerPosition[1] + (self.currentAimVector[1]*self.barrelForwardOffset) + (self.currentAimVector[0]*self.barrelSideOffset)
        self.barrelExitPos = [barrelXPos, barrelYPos]


    def fire(self, projectiles):
        pass
