# PYMISSILE - a Missile Command clone
# (c) Mayank Agarwal
#
# an abandoned project


import sys
import random
import pygame
from pygame.locals import *
from math import hypot, sqrt


# constants
SCREENSIZE = SCREENWIDTH, SCREENHEIGHT = 1366, 768
BATTERYRADIUS = 20
BATTERYWIDTH = BATTERYRADIUS * 2
SPAWNWAIT = 4000
FPS = 60
PROJECTILEHEIGHT = SCREENHEIGHT / 6
PLANEHEIGHT = SCREENHEIGHT / 7


# RGB codes
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


# MAIN CLASS #
class Game:

    def __init__(self):
        self.start = True

    # setup game
    def setup(self):
        self.score = 0
        self.fullscreen = True  # used for toggling
        self.speed = 1  # speed of missiles
        self.time = 0
        self.missiles = []
        self.projectiles = []
        self.counterMissiles = []
        self.cities = []
        self.explosions = []
        self.planes = []
        self.bombs = []
        self.update_missiles()
        self.update_counter_missiles()
        self.add_cities()
        self.initTime = pygame.time.get_ticks()
        self.gameOver = False
        self.pause = False

    # program starts from
    def main(self):
        # init
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption('PyMissile')
        global SCREEN, CLOCK
        SCREEN = pygame.display.set_mode(SCREENSIZE, pygame.FULLSCREEN)
        CLOCK = pygame.time.Clock()
        # background = pygame.image.load("background.png")

        # pygame.mixer.Sound('Powerup3.wav').play()

        # run the game
        self.run()

    # runs the game
    def run(self):
        # joystick
        joystick = None
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

        # crosshair init
        crosshair = pygame.image.load("crosshair.png")
        crossrect = crosshair.get_rect()
        crossSpeed = 9

        done = False

        while not done:

            done = False
            over = False

            crossrect.center = SCREENWIDTH / 2, SCREENHEIGHT / 2

            self.setup()

            while not over:
                SCREEN.fill(BLACK)
                # SCREEN.blit(background, (0, 0))

                if not self.start:
                    self.display_score()  # self explanatory

                    if not self.gameOver:

                        # time management
                        if not self.pause:
                            ticks = pygame.time.get_ticks()
                            if ticks - self.initTime > 10000:
                                self.speed = int((ticks - self.initTime) / 10000)
                            if ticks - self.initTime > 1000:
                                self.time = int((ticks - self.initTime) / 1000)

                        # event handling loop
                        for event in pygame.event.get():
                            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                                pygame.quit()
                                sys.exit()
                            elif event.type == KEYUP and event.key == K_SPACE:
                                self.toggle_full_screen()
                            elif event.type == KEYUP:  # and event.key == K_p:
                                self.pause = not self.pause
                                if self.pause:
                                    ticks = pygame.time.get_ticks()
                                # print(ticks)
                            elif event.type == MOUSEMOTION:
                                mousex, mousey = event.pos
                                crossrect.center = event.pos
                            elif event.type == MOUSEBUTTONUP:
                                mousepos = mousex, mousey = event.pos
                                if not self.pause:
                                    self.add_counter_missile(crossrect.center)
                            elif event.type == JOYBUTTONDOWN:
                                if not self.pause:
                                    self.add_counter_missile(crossrect.center)

                        if not self.pause:
                            # more joystick code
                            if joystick is not None:
                                axis_x = joystick.get_axis(0)
                                axis_y = joystick.get_axis(1)

                                if abs(axis_x) < 0.01:
                                    axis_x = 0
                                if abs(axis_y) < 0.01:
                                    axis_y = 0

                                crossrect.x += crossSpeed * axis_x
                                crossrect.y += crossSpeed * axis_y

                            # crosshair positioning
                            if crossrect.left < 0:
                                crossrect.left = 0
                            if crossrect.right > SCREENWIDTH:
                                crossrect.right = SCREENWIDTH
                            if crossrect.top < 0:
                                crossrect.top = 0
                            if crossrect.bottom > SCREENHEIGHT - BATTERYWIDTH:
                                crossrect.bottom = SCREENHEIGHT - BATTERYWIDTH

                            # update missile/counterMissile list and draw them
                            self.add_missile()  # spawn a missile every two seconds
                            self.update()
                            self.draw()

                            SCREEN.blit(crosshair, (crossrect.x, crossrect.y))

                        else:
                            self.pause_screen()  # show pause screen

                    else:
                        self.game_over()  # display game over screen
                        for event in pygame.event.get():  # event handling loop
                            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                                self.check_high_score()  # check if score is highest
                                pygame.quit()
                                sys.exit()
                            elif event.type == KEYUP or event.type == JOYBUTTONDOWN:  # and event.key == K_SPACE:
                                done = False
                                over = True
                                self.check_high_score()  # check if score is highest
                else:
                    self.start_screen()

                # Redraw the screen and wait a clock tick.
                pygame.display.update()
                CLOCK.tick(FPS)

    # toggles fullscreen when spacebar pressed
    def toggle_full_screen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            SCREEN = pygame.display.set_mode(SCREENSIZE, pygame.FULLSCREEN)
        else:
            SCREEN = pygame.display.set_mode(SCREENSIZE)

    # display score in top right corner
    def display_score(self):
        font = pygame.font.SysFont("agencyfb", 28, bold=False, italic=False)
        text = font.render("SCORE "+str(self.score), 1, WHITE)
        textpos = text.get_rect()
        textpos.right = SCREENWIDTH - 2
        textpos.top = 0
        SCREEN.blit(text, textpos)

    # display game over screen
    @staticmethod
    def game_over():
        font = pygame.font.SysFont("agencyfb", 56, bold=False, italic=False)
        font2 = pygame.font.SysFont("agencyfb", 24, bold=False, italic=False)
        text1 = font.render("GAME OVER", 1, WHITE)
        text2 = font2.render("PRESS ANY KEY TO REPLAY", 1, WHITE)
        text1pos = text1.get_rect()
        text1pos.center = SCREEN.get_rect().center
        SCREEN.blit(text1, text1pos)
        text2pos = text2.get_rect()
        text2pos.center = SCREEN.get_rect().center
        text2pos.y += text1pos.height/2 + 5
        SCREEN.blit(text2, text2pos)
        # pygame.display.flip()

    # display pause screen
    @staticmethod
    def pause_screen():
        font = pygame.font.SysFont("agencyfb", 56, bold=False, italic=False)
        font2 = pygame.font.SysFont("agencyfb", 24, bold=False, italic=False)
        text1 = font.render("PAUSE", 1, WHITE)
        text2 = font2.render("PRESS ANY KEY TO RESUME", 1, WHITE)
        text1pos = text1.get_rect()
        text1pos.center = SCREEN.get_rect().center
        SCREEN.blit(text1, text1pos)
        text2pos = text2.get_rect()
        text2pos.center = SCREEN.get_rect().center
        text2pos.y += text1pos.height/2 + 5
        SCREEN.blit(text2, text2pos)
        # pygame.display.flip()

    # display start screen
    def start_screen(self):
        font = pygame.font.SysFont("agencyfb", 56, bold=False, italic=False)
        font2 = pygame.font.SysFont("agencyfb", 24, bold=False, italic=False)
        text1 = font.render("PYMISSILE", 1, WHITE)
        text2 = font2.render("PRESS ANY KEY TO START", 1, WHITE)
        text1pos = text1.get_rect()
        text1pos.center = SCREEN.get_rect().center
        SCREEN.blit(text1, text1pos)
        text2pos = text2.get_rect()
        text2pos.center = SCREEN.get_rect().center
        text2pos.y += text1pos.height/2 + 5
        SCREEN.blit(text2, text2pos)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP or event.type == MOUSEBUTTONUP or event.type == JOYBUTTONDOWN:
                self.start = False

    # updates game state by calling other methods
    def update(self):
        self.update_missiles()
        self.update_counter_missiles()
        self.update_explosions()
        self.update_cities()
        self.update_planes()
        self.update_bombs()
        self.check_collisions()
        if len(self.cities) == 0:
            self.gameOver = True

    # update state of missiles
    def update_missiles(self):
        inactive_missiles = []
        for missile in self.missiles:
            missile.update_position()
            if not missile.isActive:
                inactive_missiles.append(missile)

        for missile in inactive_missiles:
            self.missiles.remove(missile)

        inactive_projectiles = []
        for projectile in self.projectiles:
            projectile.update_position()
            if not projectile.isActive:
                inactive_projectiles.append(projectile)

        for projectile in inactive_projectiles:
            self.projectiles.remove(projectile)

    # update state of counterMissiles
    def update_counter_missiles(self):
        inactive_counterMissiles = []
        for counterMissile in self.counterMissiles:
            counterMissile.update_position()
            if not counterMissile.isActive:
                inactive_counterMissiles.append(counterMissile)
                self.add_explosion(counterMissile.endingPoint)

        for counterMissile in inactive_counterMissiles:
            self.counterMissiles.remove(counterMissile)

    # update state of bombs
    def update_bombs(self):
        inactive_bombs = []
        for bomb in self.bombs:
            bomb.update_position()
            if not bomb.isActive:
                inactive_bombs.append(bomb)

        for bomb in inactive_bombs:
            self.bombs.remove(bomb)

    # update state of planes
    def update_planes(self):
        inactive_planes = []
        for plane in self.planes:
            plane.update_position()
            if plane.drop:
                bomb = Bomb(plane.dropPoint)
                self.bombs.append(bomb)
                plane.drop = False
            if not plane.isActive:
                inactive_planes.append(plane)
                # self.add_explosion(plane.endingPoint)

        for plane in inactive_planes:
            self.planes.remove(plane)

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
        for projectile in self.projectiles:
            projectile.draw()
        for counterMissile in self.counterMissiles:
            counterMissile.draw()
        for bomb in self.bombs:
            bomb.draw()
        for city in self.cities:
            city.draw()
        for plane in self.planes:
            plane.draw()
        for explosion in self.explosions:
            explosion.draw()
        self.add_battery()

    # adds missiles and projectiles and jets to game state
    def add_missile(self):
        start = [random.randint(0, SCREENWIDTH), 0]
        end = [random.randint(0, SCREENWIDTH), SCREENHEIGHT]
        now = pygame.time.get_ticks()
        drop = self.cities[random.randrange(len(self.cities))].rect.center

        if len(self.missiles) == 0 or now - self.missiles[-1].spawntime >= SPAWNWAIT:
            if random.randrange(5) == 3:
                end = drop
            missile = Missile(start, end, self.speed)
            self.missiles.append(missile)

        if len(self.projectiles) == 0:  # or now - self.projectiles[-1].spawntime >= SPAWNWAIT:
            if random.randrange(8) == 4:
                end = drop
            projectile = Projectile((random.randrange(0, SCREENWIDTH+1, SCREENWIDTH), PROJECTILEHEIGHT), end)
            self.projectiles.append(projectile)

        if self.time % 10 == 0 and len(self.planes) == 0:
            plane = Plane(drop)
            self.planes.append(plane)

    # adds counter-missiles to game state
    def add_counter_missile(self, end):
        start = [SCREENWIDTH / 2, SCREENHEIGHT - BATTERYRADIUS]
        counterMissile = CounterMissile(start, end)
        self.counterMissiles.append(counterMissile)

    # adds cities to game state
    def add_cities(self):
        for i in range(1, 4):
            city = City(i, 'left')
            self.cities.append(city)
        for i in range(1, 4):
            city = City(i, 'right')
            self.cities.append(city)

    # adds battery (gun) to screen
    @staticmethod
    def add_battery():
        pygame.draw.circle(SCREEN, GRAY, (int(SCREENWIDTH / 2), int(SCREENHEIGHT)), BATTERYRADIUS)

    # adds explosion at crosshair position
    def add_explosion(self, position):
        explosion = Explosion(position)
        self.explosions.append(explosion)

    # destroys objects that have been hit
    def check_collisions(self):
        for explosion in self.explosions:
            for missile in self.missiles:
                if explosion.contains(missile.currentPosition):
                    missile.isActive = False
                    self.score += 2
            for projectile in self.projectiles:
                if explosion.contains(projectile.currentPosition):
                    projectile.isActive = False
                    self.score += 3
            for bomb in self.bombs:
                if explosion.contains(bomb.currentPosition):
                    bomb.isActive = False
                    self.score += 5
            for plane in self.planes:
                if explosion.contains(plane.currentPosition) or \
                        explosion.contains((plane.rect.right, PLANEHEIGHT)) or \
                        explosion.contains((plane.rect.left, PLANEHEIGHT)):
                    plane.isActive = False
                    self.score += 5
                    # print("Score " + str(self.score))
            for city in self.cities:
                if explosion.contains(city.rect.center):
                    city.isActive = False
                    # self.add_explosion((int(missile.currentPosition[0]), int(missile.currentPosition[1])))
                    self.score -= 10

        for city in self.cities:
            for missile in self.missiles:
                if city.contains(missile.currentPosition):
                    missile.isActive = False
                    self.add_explosion((int(missile.currentPosition[0]), int(missile.currentPosition[1])))
                    city.isActive = False
                    self.score -= 10
            for projectile in self.projectiles:
                if city.contains(projectile.currentPosition):
                    projectile.isActive = False
                    self.add_explosion((int(projectile.currentPosition[0]), int(projectile.currentPosition[1])))
                    city.isActive = False
                    self.score -= 10
                    # print("Score " + str(self.score))
            for bomb in self.bombs:
                if city.contains(bomb.currentPosition):
                    bomb.isActive = False
                    self.add_explosion((int(bomb.currentPosition[0]), int(bomb.currentPosition[1])))
                    city.isActive = False
                    self.score -= 10

    # checks if score is highest
    def check_high_score(self):
        file = open('high.txt', 'r')
        content = file.readlines()
        high_score = int(content[0])
        file.close()
        # print(str(high_score))
        if self.score > high_score:
            file = open('high.txt', 'w')
            file.write(str(self.score))
            file.close()
        elif self.score >= high_score:
            pass


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
        self.missileSpeed = random.randint(int(speed / 4) + 1, speed) * 0.60

    # update position method
    def update_position(self):
        if self.currentPosition[1] < self.endingPoint[1]:
            # drop the missile down 1 point
            self.currentPosition[1] += self.missileSpeed
            self.currentPosition[0] += self.deltaX * self.missileSpeed
        else:
            # we've reached the bottom of the screen...
            self.isActive = False

    # draw the missile to the screen
    def draw(self):
        if self.isActive:
            pygame.draw.aaline(SCREEN, RED, self.startingPoint, self.currentPosition)
            pygame.draw.circle(SCREEN, WHITE, (int(self.currentPosition[0]), int(self.currentPosition[1])),
                               self.missileSize)


# PROJECTILE BOMB #
class Projectile:
    # constructor
    def __init__(self, startingPoint, endingPoint):
        self.startingPoint = startingPoint
        self.endingPoint = endingPoint
        self.currentPosition = [startingPoint[0], startingPoint[1]]
        self.isActive = True
        self.range = self.endingPoint[0] - self.startingPoint[0]
        self.size = 2
        self.spawntime = pygame.time.get_ticks()
        self.speedX = self.range / sqrt(2 * (SCREENHEIGHT - PROJECTILEHEIGHT) / 0.01)
        self.speedY = 0
        self.pointlist = [[int(self.currentPosition[0]), int(self.currentPosition[1])]]

    # update position method
    def update_position(self):
        if self.currentPosition[1] < self.endingPoint[1]:
            # drop the missile down
            self.speedY += 0.01
            self.currentPosition[1] += self.speedY
            self.currentPosition[0] += self.speedX
            self.pointlist.append([int(self.currentPosition[0]), int(self.currentPosition[1])])
            # print(self.pointlist)
        else:
            # we've reached the bottom of the screen...
            self.isActive = False

    # draw the missile to the screen
    def draw(self):
        if self.isActive:
            pygame.draw.aalines(SCREEN, CYAN, False, self.pointlist, 1000)
            pygame.draw.circle(SCREEN, WHITE, (int(self.currentPosition[0]), int(self.currentPosition[1])), self.size)


# COUNTER MISSILE / ANTI-BALLISTIC #
class CounterMissile:
    # constructor
    def __init__(self, startingPoint, endingPoint):
        self.startingPoint = startingPoint
        self.endingPoint = endingPoint
        self.currentPosition = [startingPoint[0], startingPoint[1]]
        self.isActive = True
        self.deltaX = (self.startingPoint[0] - self.endingPoint[0]) / (self.startingPoint[1] - self.endingPoint[1])
        self.counterMissileSpeed = 10
        if endingPoint[1] < SCREENHEIGHT / 2:
            self.counterMissileSpeed = 20
        self.counterMissileSize = 2
        pygame.mixer.Sound('Shoot2.wav').play()

    # update position method
    def update_position(self):
        if self.currentPosition[1] > self.endingPoint[1]:
            # drop the missile down 1 point
            self.currentPosition[1] -= 1 * self.counterMissileSpeed
            self.currentPosition[0] -= self.deltaX * self.counterMissileSpeed
        else:
            # we've reached the end point...
            self.isActive = False

    # draw the counterMissile to the screen
    def draw(self):
        if self.isActive:
            pygame.draw.aaline(SCREEN, YELLOW, self.startingPoint, self.currentPosition)
            pygame.draw.circle(SCREEN, YELLOW, (int(self.currentPosition[0]), int(self.currentPosition[1])),
                               self.counterMissileSize)


# BOMB #
class Bomb:
    # constructor
    def __init__(self, dropPoint):
        self.startingPoint = [dropPoint[0], PLANEHEIGHT]
        self.endingPoint = dropPoint
        self.currentPosition = [self.startingPoint[0], self.startingPoint[1]]
        self.isActive = True
        # self.deltaX = (self.endingPoint[0] - self.startingPoint[0]) / self.endingPoint[1]
        self.bombSize = 5
        self.spawntime = pygame.time.get_ticks()
        self.bombSpeed = 1  # random.randint(int(speed / 4) + 1, speed) * 0.70

    # update position method
    def update_position(self):
        if self.currentPosition[1] < self.endingPoint[1]:
            # drop the bomb down 1 point
            self.bombSpeed += 0.05
            self.currentPosition[1] += self.bombSpeed
        else:
            # we've reached the bottom of the screen...
            self.isActive = False

    # draw the bomb to the screen
    def draw(self):
        if self.isActive:
            # pygame.draw.aaline(SCREEN, ORANGE, self.startingPoint, self.currentPosition)
            pygame.draw.circle(SCREEN, RED, (int(self.currentPosition[0]), int(self.currentPosition[1])), self.bombSize)


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
        pygame.mixer.Sound('Explosion5.wav').play()

    # updates blast radius
    def update(self):
        self.radius += self.delta
        if self.radius == self.maxRadius:
            self.delta = -self.delta  # start shrinking once it reaches the max radius
        elif self.radius == 0:
            self.isActive = False

    # draws the explosion to screen
    def draw(self):
        colors = [RED, ORANGE, YELLOW]
        i = random.randrange(len(colors))
        pygame.draw.circle(SCREEN, colors[i], self.location, self.radius)

    # returns whether a missile is inside the blast radius
    def contains(self, point):
        return hypot(self.location[0] - point[0], self.location[1] - point[1]) <= self.radius


# PLANES #
class Plane:
    # constructor
    def __init__(self, dropPoint):
        if dropPoint[0] < SCREENWIDTH / 2:
            self.startingPoint = [0, PLANEHEIGHT]
        else:
            self.startingPoint = [SCREENWIDTH, PLANEHEIGHT]
        if self.startingPoint[0] == 0:
            self.endingPoint = (SCREENWIDTH, PLANEHEIGHT)
            self.deltaX = 1
            self.image = pygame.image.load("plane.png")
        else:
            self.endingPoint = (0, PLANEHEIGHT)
            self.deltaX = -1
            self.image = pygame.image.load("planeFlipped.png")
        self.currentPosition = self.startingPoint
        self.dropPoint = dropPoint
        self.isActive = True
        self.drop = False
        self.spawnTime = pygame.time.get_ticks()
        self.rect = self.image.get_rect()
        # self.missileSpeed = random.randint(int(speed / 4) + 1, speed) * 0.70

    # update position method
    def update_position(self):
        if self.currentPosition[0] != self.endingPoint[0]:
            self.currentPosition[0] += self.deltaX
            self.rect.center = self.currentPosition
        else:
            # we've reached the end of the screen...
            self.isActive = False

        if self.rect.right == self.dropPoint[0]:
            self.drop = True

    # draw the plane to the screen
    def draw(self):
        if self.isActive:
            SCREEN.blit(self.image, (self.rect.x, self.rect.y))


Game().main()
