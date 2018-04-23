import random
import game.base_monster as BaseMonsterCode


class StandardMonster(BaseMonsterCode.BaseMonster):

     def __init__(self, typeID, waveOrder, startPos, allMonsterSprites, playArea, tiledLevel, explosionsSpriteSheet):
          
          super().__init__(typeID, waveOrder, startPos, allMonsterSprites, playArea, tiledLevel, explosionsSpriteSheet)

          self.cashValue = 30
          self.idleMoveSpeed = self.setAverageSpeed(35)
          self.attackMoveSpeed = self.setAverageSpeed(75)
          self.moveSpeed = self.idleMoveSpeed
          self.health = 95
