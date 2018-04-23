import pygame
from pygame.locals import *


class UTTextButton:
    def __init__(self, rect, button_text, fonts, font_size):
        self.fonts = fonts
        self.buttonText = button_text
        self.rect = rect
        self.clickedButton = False
        self.isHovered = True
        self.fontSize = font_size

        self.isEnabled = True

        self.buttonColour = pygame.Color(75, 75, 75)
        self.textColour = pygame.Color(255, 255, 255)

        self.button_text_render = self.fonts[self.fontSize].render(self.buttonText, True, self.textColour)

    def handle_input_event(self, event):
        if self.isEnabled and self.is_inside(pygame.mouse.get_pos()):
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

    def was_pressed(self):
        was_pressed = self.clickedButton
        self.clickedButton = False
        return was_pressed

    def set_text(self, text):
        self.buttonText = text
        self.button_text_render = self.fonts[self.fontSize].render(self.buttonText, True, self.textColour)
    
    def update(self):
        if self.isEnabled and self.is_inside(pygame.mouse.get_pos()):
            self.isHovered = True
            self.buttonColour = pygame.Color(100, 100, 100)
        elif self.isEnabled:
            self.isHovered = False
            self.buttonColour = pygame.Color(75, 75, 75)

    def is_inside(self, screen_pos):
        is_inside = False
        if self.rect[0] <= screen_pos[0] <= self.rect[0]+self.rect[2]:
            if self.rect[1] <= screen_pos[1] <= self.rect[1]+self.rect[3]:
                is_inside = True
        return is_inside

    def draw(self, screen):
        pygame.draw.rect(screen, self.buttonColour, pygame.Rect(self.rect[0],
                                                                self.rect[1],
                                                                self.rect[2],
                                                                self.rect[3]), 0)
        screen.blit(self.button_text_render,
                    self.button_text_render.get_rect(centerx=self.rect[0] + self.rect[2] * 0.5,
                                                     centery=self.rect[1] + self.rect[3] * 0.5))
