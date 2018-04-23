import pygame
from pygame.locals import *

class UTTextButton():
    def __init__(self, rect, buttonText, fonts, fontSize):
        self.fonts = fonts
        self.buttonText = buttonText
        self.rect = rect
        self.clickedButton = False
        self.isHovered = True
        self.fontSize = fontSize

        self.isEnabled = True

        self.buttonColour = pygame.Color(75, 75, 75)
        self.textColour = pygame.Color(255, 255, 255)

        self.buttonTextrender = self.fonts[self.fontSize].render(self.buttonText, True, self.textColour)

    def handleInputEvent(self, event):
        if self.isEnabled and self.isInside(pygame.mouse.get_pos()):
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.clickedButton = True
                    
    def disable(self):
        self.isEnabled = False
        self.buttonColour = pygame.Color(50, 50, 50)
        self.textColour = pygame.Color(0, 0, 0)

    def enable(self):
        self.isEnabled = True
        self.buttonColour = pygame.Color(75, 75, 75)
        self.textColour = pygame.Color(255, 255, 255)
        
    
    def wasPressed(self):
        wasPressed = self.clickedButton
        self.clickedButton = False
        return wasPressed

    def setText(self, text):
        self.buttonText = text
        self.buttonTextrender = self.fonts[self.fontSize].render(self.buttonText, True, self.textColour)
    
    def update(self):
        if self.isEnabled and self.isInside(pygame.mouse.get_pos()):
            self.isHovered = True
            self.buttonColour = pygame.Color(100, 100, 100)
        elif self.isEnabled:
            self.isHovered = False
            self.buttonColour = pygame.Color(75, 75, 75)
            

    def isInside(self, screenPos):
        isInside = False
        if screenPos[0] >= self.rect[0] and screenPos[0] <= self.rect[0]+self.rect[2]:
            if screenPos[1] >= self.rect[1] and screenPos[1] <= self.rect[1]+self.rect[3]:
                isInside = True
        return isInside

    def draw(self, screen):
        pygame.draw.rect(screen, self.buttonColour, pygame.Rect(self.rect[0],self.rect[1],self.rect[2], self.rect[3]), 0)     
        screen.blit(self.buttonTextrender, self.buttonTextrender.get_rect(centerx=self.rect[0] + self.rect[2]*0.5, centery=self.rect[1] + self.rect[3]*0.5))
