import pygame, sys, random
from pygame.locals import *


# constants
SCREENWIDTH = 1000
SCREENHEIGHT = 600
FPS = 60

#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)
BLACK    = (  0,   0,   0)


# MAIN CLASS
class Game:

    def main(self):
        # init
        global FPSCLOCK, SCREEN
        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        pygame.display.set_caption('PyMissile')

        mousex = 0 # used to store x coordinate of mouse event
        mousey = 0 # used to store y coordinate of mouse event

        self.setup()

        while True: # game loop

            mouseClicked = False

            SCREEN.fill(BLACK)

            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    mousex, mousey = event.pos
                elif event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    mouseClicked = True
                    self.add_missile() # add missile if clicked

            # update missile list and draw them
            self.allObjects.update()
            self.allObjects.draw(SCREEN)

            # Redraw the screen and wait a clock tick.
            pygame.display.flip()
            FPSCLOCK.tick(FPS)

    def setup(self):
        self.allObjects = pygame.sprite.Group()
        self.allMissiles = pygame.sprite.Group()

    # def update_missiles(self):
    #     inactive_missiles = []
    #     for missile in self.missiles:
    #         missile.update_position()
    #         if not missile.isActive:
    #             inactive_missiles.append(missile)
    #
    #     for missile in inactive_missiles:
    #         self.missiles.remove(missile)

    # def draw(self):
    #     for missile in self.missiles:
    #         missile.draw()

    def add_missile(self):
        start = [random.randint(0, SCREENWIDTH), 0]
        end = [random.randint(0, SCREENWIDTH), SCREENHEIGHT]
        missile = Missile(start, end)
        self.allObjects.add(missile)
        self.allMissiles.add(missile)


# ------- #
# MISSILE #
# ------- #
class Missile(pygame.sprite.Sprite):

    # constructor
    def __init__(self, start, end):
        super().__init__()
        self.startingPoint = start
        self.endingPoint = end
        self.deltaX = (end[0] - start[0]) / end[1]
        self.missileSpeed = 0.75 * random.randint(1, 3)
        self.missileSize = 4

        # Set the background color and set it to be transparent
        self.image = pygame.Surface([self.missileSize, self.missileSize])
        self.image.fill(WHITE)
        #self.image.set_colorkey(WHITE)

        # rect of the Missile
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = start

        # # Draw the missile
        # pygame.draw.aaline(SCREEN, RED, self.startingPoint, (self.rect.x, self.rect.y))
        # pygame.draw.ellipse(self.image, RED, [self.rect.x, self.rect.y, self.missileSize, self.missileSize])

    # update position method
    def update(self):
        if self.rect.y < self.endingPoint[1]:
            # drop the missile down 1 point
            self.rect.y += 1 * self.missileSpeed
            self.rect.x += self.deltaX * self.missileSpeed
            # # Draw the missile
            # pygame.draw.aaline(SCREEN, RED, self.startingPoint, (self.rect.x, self.rect.y))
            # pygame.draw.ellipse(self.image, WHITE, [self.rect.x, self.rect.y, self.missileSize, self.missileSize])



Game().main()