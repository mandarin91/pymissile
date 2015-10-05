import pygame, sys, random
from pygame.locals import *


# constants
SCREENSIZE = SCREENWIDTH, SCREENHEIGHT = 900, 600
BATTERYRADIUS = 20
BATTERYWIDTH = BATTERYRADIUS * 2
SPAWNWAIT = 2000
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

    def __init__(self):
        self.fullscreen = False # used for toggling
        self.speed = 1

    def main(self):
        # init
        pygame.init()
        pygame.display.set_caption('PyMissile')
        global SCREEN
        SCREEN = pygame.display.set_mode(SCREENSIZE)
        clock = pygame.time.Clock()

        joystick = None
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

        crosshair = pygame.image.load("Crosshair.png")
        crossrect = crosshair.get_rect()
        crossrect.center = SCREENWIDTH/2, SCREENHEIGHT/2
        crossSpeed = 8

        mousex = 0 # used to store x coordinate of mouse event
        mousey = 0 # used to store y coordinate of mouse event

        self.setup()

        while True: # game loop

            mouseClicked = False

            SCREEN.fill(BLACK)

            ticks = pygame.time.get_ticks()
            if ticks > 10000:
                speed = int(ticks/10000)

            self.add_missile() # spawn a missile every two seconds

            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYUP and event.key == K_SPACE:
                     self.toggleFullScreen()
                elif event.type == MOUSEMOTION:
                    mousex, mousey = event.pos
                    crossrect.center = event.pos
                elif event.type == MOUSEBUTTONUP:
                    mousepos = mousex, mousey = event.pos
                    mouseClicked = True
                    # self.add_missile()
                    self.add_bomb(mousepos)
                elif event.type == JOYBUTTONDOWN:
                    #self.add_missile()
                    self.add_bomb(crossrect.center)
                #else: #if event.type == JOYAXISMOTION:

            axis_x = joystick.get_axis(0)
            axis_y = joystick.get_axis(1)

            if abs(axis_x) < 0.01:
                axis_x = 0
            if abs(axis_y) < 0.01:
                axis_y = 0

            crossrect.x += crossSpeed * axis_x
            crossrect.y += crossSpeed * axis_y

            if crossrect.left < 0: crossrect.left = 0
            if crossrect.right > SCREENWIDTH: crossrect.right = SCREENWIDTH
            if crossrect.top < 0: crossrect.top = 0
            if crossrect.bottom > SCREENHEIGHT - BATTERYWIDTH: crossrect.bottom = SCREENHEIGHT - BATTERYWIDTH

            # update missile/bomb list and draw them
            self.update_missiles()
            self.update_bombs()
            self.draw()

            # Redraw the screen and wait a clock tick.
            SCREEN.blit(crosshair, (crossrect.x, crossrect.y))
            pygame.display.flip()
            clock.tick(FPS)

    def toggleFullScreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            SCREEN = pygame.display.set_mode(SCREENSIZE, pygame.FULLSCREEN)
        else:
            SCREEN = pygame.display.set_mode(SCREENSIZE)

    def setup(self):
        self.missiles = []
        self.bombs = []
        self.cities = []
        self.update_missiles()
        self.update_bombs()
        self.add_cities()

    def update_missiles(self):
        inactive_missiles = []
        for missile in self.missiles:
            missile.update_position()
            if not missile.isActive:
                inactive_missiles.append(missile)

        for missile in inactive_missiles:
            self.missiles.remove(missile)

    def update_bombs(self):
        inactive_bombs = []
        for bomb in self.bombs:
            bomb.update_position()
            if not bomb.isActive:
                inactive_bombs.append(bomb)

        for bomb in inactive_bombs:
            self.bombs.remove(bomb)

    def update_cities(self):
        inactive_cities = []
        for city in self.cities:
            city.update()
            if not city.isActive:
                inactive_cities.append(city)

        for city in inactive_cities:
            self.cities.remove(city)

    def draw(self):
        for missile in self.missiles:
            missile.draw()
        for bomb in self.bombs:
            bomb.draw()
        for city in self.cities:
            city.draw()
        self.add_battery()

    def add_missile(self):
        start = [random.randint(0, SCREENWIDTH), 0]
        end = [random.randint(0, SCREENWIDTH), SCREENHEIGHT]
        now = pygame.time.get_ticks()
        if len(self.missiles) == 0 or now - self.missiles[-1].spawntime >= SPAWNWAIT:
            missile = Missile(start, end, self.speed)
            self.missiles.append(missile)

    def add_bomb(self, end):
        start = [SCREENWIDTH / 2, SCREENHEIGHT - BATTERYRADIUS]
        bomb = Bomb(start, end)
        self.bombs.append(bomb)

    def add_cities(self):
        for i in range(1, 4):
            city = City(i, 'left')
            self.cities.append(city)
        for i in range(1, 4):
            city = City(i, 'right')
            self.cities.append(city)

    def add_battery(self):
        pygame.draw.circle(SCREEN, GRAY, (int(SCREENWIDTH/2), int(SCREENHEIGHT)), BATTERYRADIUS)
        #pygame.draw.arc(SCREEN, GRAY, [SCREENWIDTH/2 - BATTERYRADIUS, SCREENHEIGHT - BATTERYRADIUS, BATTERYWIDTH, BATTERYRADIUS], 0, pi, 2)


# MISSILE #
class Missile:

    # constructor
    def __init__(self, startingPoint, endingPoint, speed):
        self.startingPoint = startingPoint
        self.endingPoint = endingPoint
        self.currentPosition = [startingPoint[0], startingPoint[1]]
        self.isActive = True
        self.deltaX = (self.endingPoint[0] - self.startingPoint[0]) / self.endingPoint[1]
        self.missileSize = 2
        self.spawntime = pygame.time.get_ticks()
        self.missileSpeed = random.randint(1, speed) * 0.70

    # update position method
    def update_position(self):
        if self.currentPosition[1] < self.endingPoint[1]:
            # drop the missile down 1 point
            self.currentPosition[1] += 1 * self.missileSpeed
            self.currentPosition[0] += self.deltaX * self.missileSpeed
        else:
            # we've reached the bottom of the screen...
            self.isActive = False

    # draw the missile to the screen
    def draw(self):
        if self.isActive:
            pygame.draw.aaline(SCREEN, ORANGE, self.startingPoint, self.currentPosition)
            pygame.draw.circle(SCREEN, WHITE, (int(self.currentPosition[0]), int(self.currentPosition[1])), self.missileSize)


# BOMB #
class Bomb:

    # constructor
    def __init__(self, startingPoint, endingPoint):
        self.startingPoint = startingPoint
        self.endingPoint = endingPoint
        self.currentPosition = [startingPoint[0], startingPoint[1]]
        self.isActive = True
        self.deltaX = (self.startingPoint[0] - self.endingPoint[0]) / (self.startingPoint[1] - self.endingPoint[1])
        self.bombSpeed = 10
        self.bombSize = 2

    # update position method
    def update_position(self):
        if self.currentPosition[1] > self.endingPoint[1]:
            # drop the missile down 1 point
            self.currentPosition[1] -= 1 * self.bombSpeed
            self.currentPosition[0] -= self.deltaX * self.bombSpeed
        else:
            # we've reached the bottom of the screen...
            self.isActive = False

    # draw the bomb to the screen
    def draw(self):
        if self.isActive:
            pygame.draw.aaline(SCREEN, YELLOW, self.startingPoint, self.currentPosition)
            pygame.draw.circle(SCREEN, YELLOW, (int(self.currentPosition[0]), int(self.currentPosition[1])), self.bombSize)


# CITY #
class City:

    cityWidth = 50
    cityHeight = 30

    # constructor
    def __init__(self, index, side):
        left, right = 0, 0
        if side == 'left':
            left, right = 0, SCREENWIDTH/2 - BATTERYWIDTH
        else:
            left, right = SCREENWIDTH/2 + BATTERYWIDTH, SCREENWIDTH
        self.city = pygame.Surface((self.cityWidth, self.cityHeight))
        self.city.fill(WHITE)
        self.rect = self.city.get_rect()
        self.rect.center = left + index * (right-left)/3 - (right-left)/6, SCREENHEIGHT - self.cityHeight / 2
        self.isActive = True

    def draw(self):
        SCREEN.blit(self.city, (self.rect.x, self.rect.y))

Game().main()