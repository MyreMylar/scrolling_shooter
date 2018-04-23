import math
import pygame
import random
import csv
from pygame.locals import *
from operator import attrgetter

import game.map_editor as EditorCode
import game.main_menu as MainMenuCode
import game.player as PlayerCode
import game.explosion as ExplosionCode
import game.player_health_bar as HealthBarCode
import game.tiled_level as TiledLevelCode
import game.pick_up as PickUpCode

import game.standard_monster as MonsterCode
        
class ScreenData():
    def __init__(self, hudSize, editorHudSize, screenSize):
        self.screenSize = screenSize
        self.hudDimensions = hudSize
        self.editorHudDimensions = editorHudSize
        self.playArea = [self.screenSize[0], self.screenSize[1]-self.hudDimensions[1]]

    def setEditorActive(self):
        self.playArea = [self.screenSize[0], self.screenSize[1]-self.editorHudDimensions[1]]


def spawnMonsters(monsters, allMonsterSprites, screenData, tiledLevel, explosionsSpriteSheet):
    # wave 1
    monsters.append(MonsterCode.StandardMonster("spherical", 4, [512,(128*64)-800], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))
    monsters.append(MonsterCode.StandardMonster("mechanical", 3, [576,(128*64)-864], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))
    monsters.append(MonsterCode.StandardMonster("spherical", 2, [512,(128*64)-928], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))
    monsters.append(MonsterCode.StandardMonster("mechanical", 1, [576,(128*64)-992], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))
    monsters.append(MonsterCode.StandardMonster("spherical", 0, [512,(128*64)-1056], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))

    # wave 2
    monsters.append(MonsterCode.StandardMonster("spherical", 4, [512,(128*64)-3800], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))
    monsters.append(MonsterCode.StandardMonster("mechanical", 3, [576,(128*64)-3864], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))
    monsters.append(MonsterCode.StandardMonster("spherical", 2, [512,(128*64)-3928], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))
    monsters.append(MonsterCode.StandardMonster("mechanical", 1, [576,(128*64)-3992], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))
    monsters.append(MonsterCode.StandardMonster("spherical", 0, [512,(128*64)-4056], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))

    #wave 3
    monsters.append(MonsterCode.StandardMonster("spherical", 4, [512,(128*64)-6800], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))
    monsters.append(MonsterCode.StandardMonster("mechanical", 3, [576,(128*64)-6864], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))
    monsters.append(MonsterCode.StandardMonster("spherical", 2, [512,(128*64)-6928], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))
    monsters.append(MonsterCode.StandardMonster("mechanical", 1, [576,(128*64)-6992], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))
    monsters.append(MonsterCode.StandardMonster("spherical", 0, [512,(128*64)-7056], allMonsterSprites, screenData.playArea, tiledLevel, explosionsSpriteSheet))

def main():

    #some colours
    BLACK = (  0,   0,   0)
    RED = (  255,   0,   0)
    BLUE = (  50,   50,   200)
    
    pygame.init()
    pygame.key.set_repeat()
    xScreenSize = 1024
    yScreenSize = 600
    screenData = ScreenData([xScreenSize, 0], [xScreenSize, 184], [xScreenSize, yScreenSize])
    screen = pygame.display.set_mode(screenData.screenSize)
    pygame.display.set_caption('Maximum Gunishment')
    background = pygame.Surface(screen.get_size())
    background = background.convert() 
    background.fill((95, 140, 95))

    playerSprites = pygame.sprite.OrderedUpdates()
    allTileSprites = pygame.sprite.Group()
    allMonsterSprites = pygame.sprite.OrderedUpdates()
    allPickUpSprites = pygame.sprite.Group()
    allExplosionSprites = pygame.sprite.Group()
    allProjectileSprites = pygame.sprite.Group()
    hud_sprites = pygame.sprite.Group()

    fonts = []
    smallFont = pygame.font.Font(None, 16)
    smallFontScreenSpaceLineHeight = 20.0/yScreenSize
    font = pygame.font.Font("data/BOD_PSTC.TTF", 32)
    largeFont = pygame.font.Font("data/BOD_PSTC.TTF", 150)

    fonts.append(smallFont)
    fonts.append(font)
    fonts.append(largeFont)
    
    explosionsSpriteSheet = pygame.image.load("images/explosions.png").convert_alpha()

    allUIWindows = []
    players = []
    monsters = []
    pick_ups = []
    projectiles = []
    explosions = []
    newExplosions = []
    
    tiledLevel = TiledLevelCode.TiledLevel([16,128], allTileSprites, allMonsterSprites, monsters, screenData, explosionsSpriteSheet)

    tiledLevel.loadTiles()
    tiledLevel.resetGuards()
    mainMenu = MainMenuCode.MainMenu(fonts)
    
    hudRect = pygame.Rect(0, screenData.screenSize[1] - screenData.hudDimensions[1], screenData.hudDimensions[0], screenData.hudDimensions[1])

    editorhudRect = pygame.Rect(0, screenData.screenSize[1] - screenData.editorHudDimensions[1], screenData.editorHudDimensions[0], screenData.editorHudDimensions[1])
    editor = EditorCode.MapEditor(tiledLevel, editorhudRect, fonts)
    
    healthBar = HealthBarCode.HealthBar( [900, 25], 100, 16) 


    pickUpSpawner = PickUpCode.PickUpSpawner(pick_ups, allPickUpSprites)
    
    clock = pygame.time.Clock()        
    timePassed = 0.0

    timeMultiplier = 1.0
    running = True
    
    isMainMenu = True
    isEditor = False
    
    isGameOver = False
    restartGame = False
    winMessage = ""

    spawnMonsters(monsters, allMonsterSprites, screenData, tiledLevel, explosionsSpriteSheet)
    
    while running:
        frameTime = clock.tick()
        timeDelta = frameTime/1000.0

        if isMainMenu:
            isMainMenuAndIndex = mainMenu.run(screen, background, fonts, screenData)
            if isMainMenuAndIndex[0] == 0:
                isMainMenu = True
            elif isMainMenuAndIndex[0] == 1:
                isMainMenu = False
            elif isMainMenuAndIndex[0] == 2:
                isMainMenu = False
                isEditor = True
            elif isMainMenuAndIndex[0] == 3:
                running = False
            selectedCharacterIndex = isMainMenuAndIndex[1]
            if not isMainMenu and not isEditor:
                #spawn player
                defaultScheme = PlayerCode.Scheme()
                player = PlayerCode.Player(tiledLevel.findPlayerStart(), tiledLevel, defaultScheme, explosionsSpriteSheet)
                players.append(player)
                         
        elif isEditor:
            screenData.setEditorActive()
            running = editor.run(screen, background, allTileSprites, editorhudRect, timeDelta)
            
            
        else:
 
            if restartGame:
                restartGame = False

                #clear all stuff
                players[:] = []
                monsters[:] = []
                pick_ups[:] = []
                projectiles[:] = []
                explosions[:] = []
                newExplosions[:] = []
                allMonsterSprites.empty()
                allPickUpSprites.empty()

                isGameOver = False
                
                tiledLevel.resetGuards()
                defaultScheme = PlayerCode.Scheme()
                player = PlayerCode.Player(tiledLevel.findPlayerStart(), tiledLevel, defaultScheme, explosionsSpriteSheet)
                players.append(player)

                spawnMonsters(monsters, allMonsterSprites, screenData, tiledLevel, explosionsSpriteSheet)
                  
            elif isGameOver:
                pass
            else:
                pass

            if player.health <= 0:
                isGameOver = True
                winMessage = "You have been defeated!"
            if player.position[1] < 0 and  player.health > 0 :
                isGameOver = True
                winMessage = "You are victorious!"

            allProjectileSprites.empty()    
            allExplosionSprites.empty()
            playerSprites.empty()
                   
            #handle UI and inout events
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if isGameOver:
                        if event.key == K_y:
                            restartGame = True
                        
                            
                for player in players:
                    player.processEvent(event)

            if player != None:
                healthBar.update(player.health, player.maxHealth)

            offsetPosition = [player.position[0], player.position[1]-268 ] #+568
            needToRefreshTiles = tiledLevel.updateOffsetPosition(offsetPosition, allTileSprites)

            for pick_up in pick_ups:
                pick_up.updateMovementAndCollision(player, timeDelta, tiledLevel)
            pick_ups[:] = [pick_up for pick_up in pick_ups if not pick_up.shouldDie]

            for player in players:
                player.updateMovementAndCollision(timeDelta, projectiles, tiledLevel, monsters, newExplosions)
                playerSprites = player.updateSprite(playerSprites,timeDelta)
                timeMultiplier = 1.0
            players[:] = [player for player in players if not player.shouldDie]

            for monster in monsters:
                monster.updateMovementAndCollision(timeDelta, timeMultiplier, screenData, player, newExplosions, tiledLevel, monsters, projectiles, pickUpSpawner)
                monster.updateSprite(timeDelta, timeMultiplier)
            monsters[:] = [monster for monster in monsters if not monster.shouldDie]
            newExplosions[:] = []

            for projectile in projectiles:
                projectile.updateMovementAndCollision( tiledLevel, tiledLevel.collidableTiles, players, monsters, timeDelta, newExplosions, explosions)
                allProjectileSprites = projectile.updateSprite(allProjectileSprites)
            projectiles[:] = [projectile for projectile in projectiles if not projectile.shouldDie]

            for explosion in explosions:
                allExplosionSprites = explosion.updateSprite(allExplosionSprites, timeDelta, timeMultiplier, tiledLevel)
            explosions[:] = [explosion for explosion in explosions if not explosion.shouldDie]
            
            screen.blit(background, (0, 0)) # draw the background

            allTileSprites.draw(screen)
            allPickUpSprites.draw(screen)
            allMonsterSprites.draw(screen)
            playerSprites.draw(screen)
            allExplosionSprites.draw(screen)
            allProjectileSprites.draw(screen)

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
            # player.drawCollisionRadiusCircle(screen)
            # for monster in monsters:
            #     monster.drawCollisionRadiusCircle(screen)
            
            # # RECTANGLES
            # player.drawCollisionRect(screen)
            # for monster in monsters:
            #     monster.drawCollisionRect(screen)
            #
            # for bullet in projectiles:
            #     bullet.drawCollisionRect(screen)
            
            healthBar.draw(screen, smallFont)

            if timeDelta > 0.0:
                FPSString = "FPS: " + "{:.2f}".format(1.0/timeDelta)
                FPSTextRender = font.render(FPSString, True, pygame.Color(255, 255, 255))
                screen.blit(FPSTextRender, FPSTextRender.get_rect(centerx=screenData.hudDimensions[0]*0.1, centery=screenData.screenSize[1]-(screenData.screenSize[1]*0.95)))
            
            if isGameOver:
                winMessageTextRender = largeFont.render(winMessage.upper(), True, pygame.Color(255, 255, 255))
                winMessageTextRenderRect = winMessageTextRender.get_rect(centerx=xScreenSize/2, centery=(yScreenSize/2)-128)
                playAgainTextRender = font.render("Play Again? Press 'Y' to restart".upper(), True, pygame.Color(255, 255, 255))
                playAgainTextRenderRect = playAgainTextRender.get_rect(centerx=xScreenSize/2, centery=(yScreenSize/2))
                screen.blit(winMessageTextRender, winMessageTextRenderRect)
                screen.blit(playAgainTextRender, playAgainTextRenderRect)

            
        pygame.display.flip() # flip all our drawn stuff onto the screen

    pygame.quit() # exited game loop so quit pygame

if __name__ == '__main__': main()
