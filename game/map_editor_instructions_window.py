import pygame
from pygame.locals import *

import game.ui_text_button as ButtonCode

class MapEditorInstructionsWindow():
    def __init__(self, windowRect, fonts):
        self.windowRect = windowRect
        self.fonts = fonts
        self.backGroundColour = pygame.Color(25, 25, 25)
        self.textColour = pygame.Color(255, 255, 255)
        
        self.windowTitleStr = "Instructions"

        self.shouldExit = False

        self.doneButton = ButtonCode.UTTextButton([self.windowRect[0]+(self.windowRect[2]/2) +45,self.windowRect[1]+ self.windowRect[3]-30,70,20], "Done", fonts, 0)

        self.instructionsText1 = "Arrow keys to scroll map"
        self.instructionsText2 = "Left mouse click to select tile"
        self.instructionsText3 = "Right mouse click to place tile"
        self.instructionsText4 = "'>' and '<' to rotate selected tile"
        self.instructionsText5 = "F5 to save map"

        self.instructionsText6 = " Challenge 1 "
        self.instructionsText7 = "-------------"
        self.instructionsText8 = "Create a new island on the map and save it."

        self.windowXCentre = self.windowRect[0]+self.windowRect[2]*0.5

        self.instructionsTextRender1 = self.fonts[0].render(self.instructionsText1, True, self.textColour)
        self.instructionsTextRender2 = self.fonts[0].render(self.instructionsText2, True, self.textColour)
        self.instructionsTextRender3 = self.fonts[0].render(self.instructionsText3, True, self.textColour)
        self.instructionsTextRender4 = self.fonts[0].render(self.instructionsText4, True, self.textColour)
        self.instructionsTextRender5 = self.fonts[0].render(self.instructionsText5, True, self.textColour)

        self.instructionsTextRender6 = self.fonts[0].render(self.instructionsText6, True, self.textColour)
        self.instructionsTextRender7 = self.fonts[0].render(self.instructionsText7, True, self.textColour)
        self.instructionsTextRender8 = self.fonts[0].render(self.instructionsText8, True, self.textColour)
        
        
    def handleInputEvent(self, event):

        self.doneButton.handleInputEvent(event)

    def update(self):
        self.doneButton.update()

        if self.doneButton.wasPressed():
            self.shouldExit = True    

    def isInside(self, screenPos):
        isInside = False
        if screenPos[0] >= self.windowRect[0] and screenPos[0] <= self.windowRect[0] + self.windowRect[2]:
            if screenPos[1] >= self.windowRect[1] and screenPos[1] <= self.windowRect[1] + self.windowRect[3]:
                isInside = True
        return isInside

    def draw(self, screen):
        pygame.draw.rect(screen, self.backGroundColour, pygame.Rect(self.windowRect[0], self.windowRect[1], self.windowRect[2], self.windowRect[3]), 0)

        self.titleTextrender = self.fonts[1].render(self.windowTitleStr, True, self.textColour)
        screen.blit(self.titleTextrender, self.titleTextrender.get_rect(centerx=self.windowRect[0]+self.windowRect[2]*0.5, centery=self.windowRect[1] +24))

        screen.blit(self.instructionsTextRender1, self.instructionsTextRender1.get_rect(centerx=self.windowXCentre, centery=self.windowRect[1] +50))
        screen.blit(self.instructionsTextRender2, self.instructionsTextRender2.get_rect(centerx=self.windowXCentre, centery=self.windowRect[1] +64))
        screen.blit(self.instructionsTextRender3, self.instructionsTextRender3.get_rect(centerx=self.windowXCentre, centery=self.windowRect[1] +78))
        screen.blit(self.instructionsTextRender4, self.instructionsTextRender4.get_rect(centerx=self.windowXCentre, centery=self.windowRect[1] +92))
        screen.blit(self.instructionsTextRender5, self.instructionsTextRender5.get_rect(centerx=self.windowXCentre, centery=self.windowRect[1] +106))

        screen.blit(self.instructionsTextRender6, self.instructionsTextRender6.get_rect(centerx=self.windowXCentre, centery=self.windowRect[1] +134))
        screen.blit(self.instructionsTextRender7, self.instructionsTextRender7.get_rect(centerx=self.windowXCentre, centery=self.windowRect[1] +148))

        screen.blit(self.instructionsTextRender8, self.instructionsTextRender8.get_rect(centerx=self.windowXCentre, centery=self.windowRect[1] +176))


        
        
   
        self.doneButton.draw(screen)
