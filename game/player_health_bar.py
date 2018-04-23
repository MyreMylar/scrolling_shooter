import math
import random
import pygame
from pygame.locals import *

class HealthBar():
    def __init__(self, startPos, width, height):
        
        self.width = width
        self.height = height

        self.position = [startPos[0],startPos[1]]

        self.baseRect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        self.powerRect = pygame.Rect(self.position[0]+1, self.position[1]+1, 1, self.height-2)

    def update(self, health, maxHealth ):
        healthPercentage = health/maxHealth
        if healthPercentage < 0.0:
            healthPercentage = 0.0
        healthWidth = self.lerp(0.0,self.width-2.0, healthPercentage)        
        self.healthRect = pygame.Rect(self.position[0]+1, self.position[1]+1, int(healthWidth), self.height-2)

    def draw(self, screen, smallFont ):
        healthLabelTextRender = smallFont.render("Health:", True, pygame.Color(255, 255, 255))
        textRect = healthLabelTextRender.get_rect()
        screen.blit(healthLabelTextRender, healthLabelTextRender.get_rect(centerx=self.position[0]-textRect.width+12, centery=self.position[1]+textRect.height-3))
        pygame.draw.rect(screen, pygame.Color(0, 0, 0), self.baseRect, 0)
        pygame.draw.rect(screen, pygame.Color(100, 0, 0), self.healthRect, 0)

    def lerp(self, A, B, C):
        return (C * B) + ((1.0-C) * A)
    



