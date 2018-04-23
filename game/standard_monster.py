from game.base_monster import BaseMonster


class StandardMonster(BaseMonster):

    def __init__(self, type_id, wave_order, start_pos, all_monster_sprites,
                 play_area, tiled_level, explosions_sprite_sheet):
          
        super().__init__(type_id, wave_order, start_pos, all_monster_sprites,
                         play_area, tiled_level, explosions_sprite_sheet)

        self.cashValue = 30
        self.idleMoveSpeed = self.set_average_speed(35)
        self.attackMoveSpeed = self.set_average_speed(75)
        self.moveSpeed = self.idleMoveSpeed
        self.health = 95
