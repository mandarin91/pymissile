import pygame, sys, random
from pygame.locals import *
from math import hypot


# constants
SCREENSIZE = SCREENWIDTH, SCREENHEIGHT = 900, 600
BATTERYRADIUS = 20
BATTERYWIDTH = BATTERYRADIUS * 2
SPAWNWAIT = 1400
FPS = 60

#        R    G    B
GRAY = (100, 100, 100)
NAVYBLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)


# MAIN CLASS
class Game:
    def __init__(self):
        self.score = 0
        self.fullscreen = False  # used for toggling
        self.speed = 1  # speed of missiles
        self.missiles = []
        self.bombs = []
        self.cities = []
        self.explosions = []
        self.update_missiles()
        self.update_bombs()
        self.add_cities()

    def main(self):
        # init
        pygame.init()
        pygame.display.set_caption('PyMissile')
        global SCREEN
        SCREEN = pygame.display.set_mode(SCREENSIZE)
        clock = pygame.time.Clock()
        gameOver = False

        joystick = None
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

        crosshair = pygame.image.load("Crosshair.png")
        crossrect = crosshair.get_rect()
        crossrect.center = SCREENWIDTH / 2, SCREENHEIGHT / 2
        crossSpeed = 9

        mousex = 0  # used to store x coordinate of mouse event
        mousey = 0  # used to store y coordinate of mouse event

        while not gameOver:  # game loop

            SCREEN.fill(BLACK)

            self.displayscore()  # self explanatory

            ticks = pygame.time.get_ticks()
            if ticks > 10000:
                self.speed = int(ticks / 10000)

            self.add_missile()  # spawn a missile every two seconds

            for event in pygame.event.get():  # event handling loop
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
                    self.add_bomb(mousepos)
                elif event.type == JOYBUTTONDOWN:
                    self.add_bomb(crossrect.center)

            if joystick != None:
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
            self.update()
            self.draw()

            # Redraw the screen and wait a clock tick.
            SCREEN.blit(crosshair, (crossrect.x, crossrect.y))
            pygame.display.flip()
            clock.tick(FPS)

        self.gameover()

    # toggles fullscreen when spacebar pressed
    def toggleFullScreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            SCREEN = pygame.display.set_mode(SCREENSIZE, pygame.FULLSCREEN)
        else:
            SCREEN = pygame.display.set_mode(SCREENSIZE)

    def displayscore(self):
        font = pygame.font.SysFont("agencyfb", 28, bold=False, italic=False)
        text = font.render("SCORE "+str(self.score), 1, WHITE)
        textpos = text.get_rect()
        textpos.right = SCREENWIDTH - 2
        textpos.top = 0
        SCREEN.blit(text, textpos)

    def gameover(self):
        font = pygame.font.SysFont("agencyfb", 36, bold=False, italic=False)
        text1 = font.render("GAME OVER", 1, WHITE)
        text2 = font.render("SCORE " + str(self.score), 1, WHITE)
        text1pos = text1.get_rect()
        text1pos.center = SCREEN.get_rect().center
        SCREEN.blit(text1, text1pos)

    # updates game state by calling other methods
    def update(self):
        self.update_missiles()
        self.update_bombs()
        self.update_explosions()
        self.update_cities()
        self.check_collisions()
        if len(self.cities) == 0:
            gameOver = True

    # update state of missiles
    def update_missiles(self):
        inactive_missiles = []
        for missile in self.missiles:
            missile.update_position()
            if not missile.isActive:
                inactive_missiles.append(missile)

        for missile in inactive_missiles:
            self.missiles.remove(missile)

    # update state of bombs
    def update_bombs(self):
        inactive_bombs = []
        for bomb in self.bombs:
            bomb.update_position()
            if not bomb.isActive:
                inactive_bombs.append(bomb)
                self.add_explosion(bomb.endingPoint)

        for bomb in inactive_bombs:
            self.bombs.remove(bomb)

    # update state of cities
    def update_cities(self):
        inactive_cities = []
        for city in self.cities:
            if not city.isActive:
                inactive_cities.append(city)

        for city in inactive_cities:
            self.cities.remove(city)

    # update state of explosions
    def update_explosions(self):
        inactive_explosions = []
        for explosion in self.explosions:
            explosion.update()
            if not explosion.isActive:
                inactive_explosions.append(explosion)

        for explosion in inactive_explosions:
            self.explosions.remove(explosion)

    # draws game objects to screen
    def draw(self):
        for missile in self.missiles:
            missile.draw()
        for bomb in self.bombs:
            bomb.draw()
        for city in self.cities:
            city.draw()
        for explosion in self.explosions:
            explosion.draw()
        self.add_battery()

    # adds missiles to game state
    def add_missile(self):
        start = [random.randint(0, SCREENWIDTH), 0]
        end = [random.randint(0, SCREENWIDTH), SCREENHEIGHT]
        now = pygame.time.get_ticks()
        if len(self.missiles) == 0 or now - self.missiles[-1].spawntime >= SPAWNWAIT:
            missile = Missile(start, end, self.speed)
            self.missiles.append(missile)

    # adds bombs/counter-missiles to game state
    def add_bomb(self, end):
        start = [SCREENWIDTH / 2, SCREENHEIGHT - BATTERYRADIUS]
        bomb = Bomb(start, end)
        self.bombs.append(bomb)

    # adds cities to game state
    def add_cities(self):
        for i in range(1, 4):
            city = City(i, 'left')
            self.cities.append(city)
        for i in range(1, 4):
            city = City(i, 'right')
            self.cities.append(city)

    # adds battery (gun) to screen
    def add_battery(self):
        pygame.draw.circle(SCREEN, GRAY, (int(SCREENWIDTH / 2), int(SCREENHEIGHT)), BATTERYRADIUS)

    # adds explosion at crosshair position
    def add_explosion(self, position):
        explosion = Explosion(position)
        self.explosions.append(explosion)

    # destroys objects that have been hit
    def check_collisions(self):
        for missile in self.missiles:
            for explosion in self.explosions:
                if explosion.contains(missile.currentPosition):
                    missile.isActive = False
                    self.score += 1
                    # print("Score " + str(self.score))

            for city in self.cities:
                if city.contains(missile.currentPosition):
                    self.add_explosion((int(missile.currentPosition[0]), int(missile.currentPosition[1])))
                    city.isActive = False
                    self.score -= 1
                    # print("Score " + str(self.score))


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
        self.missileSpeed = random.randint(int(speed / 4) + 1, speed) * 0.70

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
            pygame.draw.circle(SCREEN, WHITE, (int(self.currentPosition[0]), int(self.currentPosition[1])),
                               self.missileSize)


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
        if endingPoint[1] < SCREENHEIGHT / 2:
            self.bombSpeed = 20
        self.bombSize = 2

    # update position method
    def update_position(self):
        if self.currentPosition[1] > self.endingPoint[1]:
            # drop the missile down 1 point
            self.currentPosition[1] -= 1 * self.bombSpeed
            self.currentPosition[0] -= self.deltaX * self.bombSpeed
        else:
            # we've reached the end point...
            self.isActive = False

    # draw the bomb to the screen
    def draw(self):
        if self.isActive:
            pygame.draw.aaline(SCREEN, YELLOW, self.startingPoint, self.currentPosition)
            pygame.draw.circle(SCREEN, YELLOW, (int(self.currentPosition[0]), int(self.currentPosition[1])),
                               self.bombSize)


# CITY #
class City:

    # constructor
    def __init__(self, index, side):
        left, right = 0, 0
        if side == 'left':
            left, right = 0, SCREENWIDTH / 2 - BATTERYWIDTH
        else:
            left, right = SCREENWIDTH / 2 + BATTERYWIDTH, SCREENWIDTH
        self.cityImage = pygame.image.load("building.png")
        self.cityWidth, self.cityHeight = self.cityImage.get_size()
        self.rect = self.cityImage.get_rect()
        self.rect.center = [left + index * (right - left) / 3 - (right - left) / 6, SCREENHEIGHT - self.cityHeight / 2]
        self.isActive = True

    def contains(self, point):
        return self.rect.left <= point[0] <= self.rect.right and point[1] >= self.rect.center[1]

    # draws cities to screen
    def draw(self):
        SCREEN.blit(self.cityImage, (self.rect.x, self.rect.y))


# EXPLOSIONS #
class Explosion:
    def __init__(self, location, max_radius=60):
        self.location = location
        self.maxRadius = max_radius
        self.radius = 1
        self.isActive = True
        self.delta = 1

    # updates blast radius
    def update(self):
        self.radius += self.delta
        if self.radius == self.maxRadius:
            self.delta = -self.delta  # start shrinking once it reaches the max radius
        elif self.radius == 0:
            self.isActive = False

    # draws the explosion to screen
    def draw(self):
        colors = [RED, ORANGE, YELLOW, GRAY]
        i = random.randrange(0, len(colors) - 1)
        pygame.draw.circle(SCREEN, colors[i], self.location, self.radius)

    # returns whether a missile is inside the blast radius
    def contains(self, point):
        return hypot(self.location[0] - point[0], self.location[1] - point[1]) <= self.radius


Game().main()
