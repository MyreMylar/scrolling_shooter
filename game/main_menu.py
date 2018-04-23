import pygame
from pygame.locals import *
from operator import attrgetter

import game.ui_text_button as ButtonCode

class MainMenu():

    def __init__(self, fonts):
        self.showMenu = True
        self.showEditor = False

        self.isStartGameSelected = True
        self.isRunEditorSelected = False
        self.startGame = False

        self.backgroundImage = pygame.image.load("images/menu_background.png").convert()

        self.playGameButton = ButtonCode.UTTextButton([437,465,150,35], "Play Game", fonts, 1)
        self.editMapButton = ButtonCode.UTTextButton([437,515,150,35], "Edit Map", fonts, 1)


    def run(self, screen, background, fonts, screenData):
        isMainMenuAndIndex = [0,0]
        running = True
        for event in pygame.event.get():
            self.playGameButton.handleInputEvent(event)
            self.editMapButton.handleInputEvent(event)
            
            if event.type == QUIT:
                running = False

        self.playGameButton.update()
        self.editMapButton.update()
        

        if self.playGameButton.wasPressed():
            self.startGame = True
            self.showMenu = False

        if self.editMapButton.wasPressed():
            self.showEditor = True
            self.showMenu = False
                    
        screen.blit(self.backgroundImage, (0, 0)) # draw the background
        
        mainMenuTitleString = "MAXIMUM GUNISHMENT"
        mainMenuTitleTextRender = fonts[2].render(mainMenuTitleString, True, pygame.Color(255, 255, 255))
        screen.blit(mainMenuTitleTextRender, mainMenuTitleTextRender.get_rect(centerx=screenData.screenSize[0]*0.5, centery=128))

        self.playGameButton.draw(screen)
        self.editMapButton.draw(screen)
       
        if self.showEditor:
            isMainMenuAndIndex[0] = 2

        elif self.startGame:
            isMainMenuAndIndex[0] = 1
        else:
            isMainMenuAndIndex[0] = 0

        if not running:
            isMainMenuAndIndex[0] = 3
            
            

        return isMainMenuAndIndex
