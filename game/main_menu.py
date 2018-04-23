import pygame
from pygame.locals import *
from game.ui_text_button import UTTextButton


class MainMenu:

    def __init__(self, fonts):
        self.showMenu = True
        self.showEditor = False

        self.isStartGameSelected = True
        self.isRunEditorSelected = False
        self.startGame = False

        self.backgroundImage = pygame.image.load("images/menu_background.png").convert()

        self.playGameButton = UTTextButton([437, 465, 150, 35], "Play Game", fonts, 1)
        self.editMapButton = UTTextButton([437, 515, 150, 35], "Edit Map", fonts, 1)

    def run(self, screen, fonts, screen_data):
        is_main_menu_and_index = [0, 0]
        running = True
        for event in pygame.event.get():
            self.playGameButton.handle_input_event(event)
            self.editMapButton.handle_input_event(event)
            
            if event.type == QUIT:
                running = False

        self.playGameButton.update()
        self.editMapButton.update()

        if self.playGameButton.was_pressed():
            self.startGame = True
            self.showMenu = False

        if self.editMapButton.was_pressed():
            self.showEditor = True
            self.showMenu = False
                    
        screen.blit(self.backgroundImage, (0, 0))  # draw the background
        
        main_menu_title_string = "MAXIMUM GUNISHMENT"
        main_menu_title_text_render = fonts[2].render(main_menu_title_string, True, pygame.Color(255, 255, 255))
        screen.blit(main_menu_title_text_render,
                    main_menu_title_text_render.get_rect(centerx=screen_data.screenSize[0] * 0.5, centery=128))

        self.playGameButton.draw(screen)
        self.editMapButton.draw(screen)
       
        if self.showEditor:
            is_main_menu_and_index[0] = 2

        elif self.startGame:
            is_main_menu_and_index[0] = 1
        else:
            is_main_menu_and_index[0] = 0

        if not running:
            is_main_menu_and_index[0] = 3

        return is_main_menu_and_index
