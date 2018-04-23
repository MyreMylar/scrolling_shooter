import pygame
from pygame.locals import *

from game.map_editor import MapEditor
from game.main_menu import MainMenu
from game.player import Player, ControlScheme

from game.player_health_bar import HealthBar
from game.tiled_level import TiledLevel
from game.pick_up import PickUpSpawner

from game.standard_monster import StandardMonster


class ScreenData:
    def __init__(self, hud_size, editor_hud_size, screen_size):
        self.screenSize = screen_size
        self.hudDimensions = hud_size
        self.editorHudDimensions = editor_hud_size
        self.playArea = [self.screenSize[0], self.screenSize[1]-self.hudDimensions[1]]

    def set_editor_active(self):
        self.playArea = [self.screenSize[0], self.screenSize[1]-self.editorHudDimensions[1]]


def spawn_monsters(monsters, all_monster_sprites, screen_data, tiled_level, explosions_sprite_sheet):
    # wave 1
    monsters.append(StandardMonster("spherical", 4,
                                    [512, (128*64)-800], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))
    monsters.append(StandardMonster("mechanical", 3,
                                    [576, (128*64)-864], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))
    monsters.append(StandardMonster("spherical", 2,
                                    [512, (128*64)-928], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))
    monsters.append(StandardMonster("mechanical", 1,
                                    [576, (128*64)-992], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))
    monsters.append(StandardMonster("spherical", 0,
                                    [512, (128*64)-1056], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))

    # wave 2
    monsters.append(StandardMonster("spherical", 4,
                                    [512, (128*64)-3800], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))
    monsters.append(StandardMonster("mechanical", 3,
                                    [576, (128*64)-3864], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))
    monsters.append(StandardMonster("spherical", 2,
                                    [512, (128*64)-3928], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))
    monsters.append(StandardMonster("mechanical", 1,
                                    [576, (128*64)-3992], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))
    monsters.append(StandardMonster("spherical", 0,
                                    [512, (128*64)-4056], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))

    # wave 3
    monsters.append(StandardMonster("spherical", 4,
                                    [512, (128*64)-6800], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))
    monsters.append(StandardMonster("mechanical", 3,
                                    [576, (128*64)-6864], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))
    monsters.append(StandardMonster("spherical", 2,
                                    [512, (128*64)-6928], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))
    monsters.append(StandardMonster("mechanical", 1,
                                    [576, (128*64)-6992], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))
    monsters.append(StandardMonster("spherical", 0,
                                    [512, (128*64)-7056], all_monster_sprites, screen_data.playArea,
                                    tiled_level, explosions_sprite_sheet))


def main():

    pygame.init()
    pygame.key.set_repeat()
    x_screen_size = 1024
    y_screen_size = 600
    screen_data = ScreenData([x_screen_size, 0], [x_screen_size, 184], [x_screen_size, y_screen_size])
    screen = pygame.display.set_mode(screen_data.screenSize)
    pygame.display.set_caption('Maximum Gunishment')
    background = pygame.Surface(screen.get_size())
    background = background.convert() 
    background.fill((95, 140, 95))

    player_sprites = pygame.sprite.OrderedUpdates()
    all_tile_sprites = pygame.sprite.Group()
    all_monster_sprites = pygame.sprite.OrderedUpdates()
    all_pick_up_sprites = pygame.sprite.Group()
    all_explosion_sprites = pygame.sprite.Group()
    all_projectile_sprites = pygame.sprite.Group()

    fonts = []
    small_font = pygame.font.Font(None, 16)
    font = pygame.font.Font("data/BOD_PSTC.TTF", 32)
    large_font = pygame.font.Font("data/BOD_PSTC.TTF", 150)

    fonts.append(small_font)
    fonts.append(font)
    fonts.append(large_font)
    
    explosions_sprite_sheet = pygame.image.load("images/explosions.png").convert_alpha()

    players = []
    monsters = []
    pick_ups = []
    projectiles = []
    explosions = []
    new_explosions = []
    
    tiled_level = TiledLevel([16, 128], all_monster_sprites,
                             monsters, screen_data, explosions_sprite_sheet)

    tiled_level.load_tiles()
    tiled_level.reset_guards()
    main_menu = MainMenu(fonts)

    editor_hud_rect = pygame.Rect(0, screen_data.screenSize[1] - screen_data.editorHudDimensions[1],
                                  screen_data.editorHudDimensions[0], screen_data.editorHudDimensions[1])
    editor = MapEditor(tiled_level, editor_hud_rect, fonts)
    
    health_bar = HealthBar([900, 25], 100, 16)

    pick_up_spawner = PickUpSpawner(pick_ups, all_pick_up_sprites)

    player = None
    
    clock = pygame.time.Clock()

    time_multiplier = 1.0
    running = True
    
    is_main_menu = True
    is_editor = False
    
    is_game_over = False
    restart_game = False
    win_message = ""

    spawn_monsters(monsters, all_monster_sprites, screen_data, tiled_level, explosions_sprite_sheet)
    
    while running:
        frame_time = clock.tick()
        time_delta = frame_time/1000.0

        if is_main_menu:
            is_main_menu_and_index = main_menu.run(screen, fonts, screen_data)
            if is_main_menu_and_index[0] == 0:
                is_main_menu = True
            elif is_main_menu_and_index[0] == 1:
                is_main_menu = False
            elif is_main_menu_and_index[0] == 2:
                is_main_menu = False
                is_editor = True
            elif is_main_menu_and_index[0] == 3:
                running = False
            if not is_main_menu and not is_editor:
                # spawn player
                default_scheme = ControlScheme()
                player = Player(tiled_level.find_player_start(), tiled_level,
                                default_scheme, explosions_sprite_sheet)
                players.append(player)
                         
        elif is_editor:
            screen_data.set_editor_active()
            running = editor.run(screen, background, all_tile_sprites, editor_hud_rect, time_delta)

        else:
 
            if restart_game:
                restart_game = False

                # clear all stuff
                players[:] = []
                monsters[:] = []
                pick_ups[:] = []
                projectiles[:] = []
                explosions[:] = []
                new_explosions[:] = []
                all_monster_sprites.empty()
                all_pick_up_sprites.empty()

                is_game_over = False
                
                tiled_level.reset_guards()
                default_scheme = ControlScheme()
                player = Player(tiled_level.find_player_start(),
                                tiled_level, default_scheme, explosions_sprite_sheet)
                players.append(player)

                spawn_monsters(monsters, all_monster_sprites, screen_data, tiled_level, explosions_sprite_sheet)
                  
            elif is_game_over:
                pass
            else:
                pass

            if player is not None:
                if player.health <= 0:
                    is_game_over = True
                    win_message = "You have been defeated!"
                if player.position[1] < 0 < player.health:
                    is_game_over = True
                    win_message = "You are victorious!"

            all_projectile_sprites.empty()
            all_explosion_sprites.empty()
            player_sprites.empty()
                   
            # handle UI and inout events
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if is_game_over:
                        if event.key == K_y:
                            restart_game = True

                for player in players:
                    player.process_event(event)

            if player is not None:
                health_bar.update(player.health, player.maxHealth)

            offset_position = [player.position[0], player.position[1]-268]
            tiled_level.update_offset_position(offset_position, all_tile_sprites)

            for pick_up in pick_ups:
                pick_up.update_movement_and_collision(player, time_delta, tiled_level)
            pick_ups[:] = [pick_up for pick_up in pick_ups if not pick_up.shouldDie]

            for player in players:
                player.update_movement_and_collision(time_delta, projectiles, tiled_level, new_explosions)
                player_sprites = player.update_sprite(player_sprites, time_delta)
                time_multiplier = 1.0
            players[:] = [player for player in players if not player.shouldDie]

            for monster in monsters:
                monster.update_movement_and_collision(time_delta, time_multiplier, player, new_explosions,
                                                      tiled_level, projectiles, pick_up_spawner)
                monster.update_sprite(time_delta, time_multiplier)
            monsters[:] = [monster for monster in monsters if not monster.shouldDie]
            new_explosions[:] = []

            for projectile in projectiles:
                projectile.update_movement_and_collision(tiled_level, tiled_level.collidableTiles,
                                                         players, monsters, time_delta, new_explosions, explosions)
                all_projectile_sprites = projectile.update_sprite(all_projectile_sprites)
            projectiles[:] = [projectile for projectile in projectiles if not projectile.shouldDie]

            for explosion in explosions:
                all_explosion_sprites = explosion.update_sprite(all_explosion_sprites, time_delta,
                                                                time_multiplier, tiled_level)
            explosions[:] = [explosion for explosion in explosions if not explosion.shouldDie]
            
            screen.blit(background, (0, 0))  # draw the background

            all_tile_sprites.draw(screen)
            all_pick_up_sprites.draw(screen)
            all_monster_sprites.draw(screen)
            player_sprites.draw(screen)
            all_explosion_sprites.draw(screen)
            all_projectile_sprites.draw(screen)

            # ----------------------------------------
            # Challenge 2 - part 2
            # ----------------------
            #
            # Uncomment one group of either CIRCLES
            # or RECTANGLES below at a time
            # to visualise the collision shapes used
            # in the game.
            # ----------------------------------------
            # # CIRCLES
            # player.draw_collision_radius_circle(screen)
            # for monster in monsters:
            #     monster.draw_collision_radius_circle(screen)

            # # RECTANGLES
            # player.draw_collision_rect(screen)
            # for monster in monsters:
            #     monster.draw_collision_rect(screen)
            #
            # for bullet in projectiles:
            #     bullet.draw_collision_rect(screen)

            health_bar.draw(screen, small_font)

            if time_delta > 0.0:
                fps_string = "FPS: " + "{:.2f}".format(1.0/time_delta)
                fps_text_render = font.render(fps_string, True, pygame.Color(255, 255, 255))
                screen.blit(
                    fps_text_render,
                    fps_text_render.get_rect(centerx=screen_data.hudDimensions[0]*0.1,
                                             centery=screen_data.screenSize[1]-(screen_data.screenSize[1]*0.95)))
            
            if is_game_over:
                win_message_text_render = large_font.render(win_message.upper(),
                                                            True, pygame.Color(255, 255, 255))
                win_message_text_render_rect = win_message_text_render.get_rect(centerx=x_screen_size/2,
                                                                                centery=(y_screen_size/2)-128)
                play_again_text_render = font.render("Play Again? Press 'Y' to restart".upper(),
                                                     True, pygame.Color(255, 255, 255))
                play_again_text_render_rect = play_again_text_render.get_rect(centerx=x_screen_size/2,
                                                                              centery=(y_screen_size/2))
                screen.blit(win_message_text_render, win_message_text_render_rect)
                screen.blit(play_again_text_render, play_again_text_render_rect)

        pygame.display.flip()  # flip all our drawn stuff onto the screen

    pygame.quit()  # exited game loop so quit pygame


if __name__ == '__main__':
    main()
