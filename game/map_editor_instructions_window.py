import pygame
from game.ui_text_button import UTTextButton


class MapEditorInstructionsWindow:
    def __init__(self, window_rect, fonts):
        self.windowRect = window_rect
        self.fonts = fonts
        self.backGroundColour = pygame.Color(25, 25, 25)
        self.textColour = pygame.Color(255, 255, 255)
        
        self.windowTitleStr = "Instructions"

        self.shouldExit = False

        self.doneButton = UTTextButton([self.windowRect[0] + (self.windowRect[2]/2) + 45,
                                        self.windowRect[1] + self.windowRect[3]-30, 70, 20], "Done", fonts, 0)

        self.instructionsText1 = "Arrow keys to scroll map"
        self.instructionsText2 = "Left mouse click to select tile"
        self.instructionsText3 = "Right mouse click to place tile"
        self.instructionsText4 = "'>' and '<' to rotate selected tile"
        self.instructionsText5 = "F5 to save map"

        self.instructionsText6 = " Challenge 1 "
        self.instructionsText7 = "-------------"
        self.instructionsText8 = "Create a new island on the map and save it."

        self.windowXCentre = self.windowRect[0]+self.windowRect[2]*0.5

        self.title_text_render = None

        self.instructionsTextRender1 = self.fonts[0].render(self.instructionsText1, True, self.textColour)
        self.instructionsTextRender2 = self.fonts[0].render(self.instructionsText2, True, self.textColour)
        self.instructionsTextRender3 = self.fonts[0].render(self.instructionsText3, True, self.textColour)
        self.instructionsTextRender4 = self.fonts[0].render(self.instructionsText4, True, self.textColour)
        self.instructionsTextRender5 = self.fonts[0].render(self.instructionsText5, True, self.textColour)

        self.instructionsTextRender6 = self.fonts[0].render(self.instructionsText6, True, self.textColour)
        self.instructionsTextRender7 = self.fonts[0].render(self.instructionsText7, True, self.textColour)
        self.instructionsTextRender8 = self.fonts[0].render(self.instructionsText8, True, self.textColour)

    def handle_input_event(self, event):
        self.doneButton.handle_input_event(event)

    def update(self):
        self.doneButton.update()

        if self.doneButton.was_pressed():
            self.shouldExit = True    

    def is_inside(self, screen_pos):
        is_inside = False
        if self.windowRect[0] <= screen_pos[0] <= self.windowRect[0] + self.windowRect[2]:
            if self.windowRect[1] <= screen_pos[1] <= self.windowRect[1] + self.windowRect[3]:
                is_inside = True
        return is_inside

    def draw(self, screen):
        pygame.draw.rect(screen, self.backGroundColour,
                         pygame.Rect(self.windowRect[0],
                                     self.windowRect[1],
                                     self.windowRect[2],
                                     self.windowRect[3]), 0)

        self.title_text_render = self.fonts[1].render(self.windowTitleStr, True, self.textColour)
        screen.blit(self.title_text_render,
                    self.title_text_render.get_rect(centerx=self.windowRect[0] + self.windowRect[2] * 0.5,
                                                    centery=self.windowRect[1] + 24))

        screen.blit(self.instructionsTextRender1,
                    self.instructionsTextRender1.get_rect(centerx=self.windowXCentre,
                                                          centery=self.windowRect[1] + 50))
        screen.blit(self.instructionsTextRender2,
                    self.instructionsTextRender2.get_rect(centerx=self.windowXCentre,
                                                          centery=self.windowRect[1] + 64))
        screen.blit(self.instructionsTextRender3,
                    self.instructionsTextRender3.get_rect(centerx=self.windowXCentre,
                                                          centery=self.windowRect[1] + 78))
        screen.blit(self.instructionsTextRender4,
                    self.instructionsTextRender4.get_rect(centerx=self.windowXCentre,
                                                          centery=self.windowRect[1] + 92))
        screen.blit(self.instructionsTextRender5,
                    self.instructionsTextRender5.get_rect(centerx=self.windowXCentre,
                                                          centery=self.windowRect[1] + 106))

        screen.blit(self.instructionsTextRender6,
                    self.instructionsTextRender6.get_rect(centerx=self.windowXCentre,
                                                          centery=self.windowRect[1] + 134))
        screen.blit(self.instructionsTextRender7,
                    self.instructionsTextRender7.get_rect(centerx=self.windowXCentre,
                                                          centery=self.windowRect[1] + 148))

        screen.blit(self.instructionsTextRender8,
                    self.instructionsTextRender8.get_rect(centerx=self.windowXCentre,
                                                          centery=self.windowRect[1] + 176))

        self.doneButton.draw(screen)
