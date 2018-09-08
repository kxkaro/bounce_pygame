import pygame
from pygame.locals import *
from .game_object import *

from silnik import image
from silnik.rendering.shape import Polygon, rectangle
from silnik.rendering.point import Point

from .constants import *
from . import image_paths


class Player(pygame.sprite.Sprite):

    # these parameters are used to decrease velocity when decelerating
    DRAG = 0.9
    ZERO = 0.01

    # gravity parameter used for relating jumping velocity to main velocity G * v
    G = 0  # set to 0 for now -> update to a positive value after implementing horizontal walls
    
    # elasticity parameter used to decrease velocity when hitting the ground
    ELASTICITY = 0.8

    # factor used to calculate max jump height, used to multiply player's speed unit
    LEAP_FORCE = 5

    def __init__(self, speed_unit=1):
        super().__init__()

        self.speed_unit = speed_unit

        self.image = image.Image.load(image_paths.PLAYER_MAIN)
        self.rect = self.image.shape

        # acceleration, velocity, mass - used for acceleration and deceleration. 
        # separate velocities for movement on x axis (right/left) and y axis (jump)
        self.v_x = 0
        self.v_y = - self.speed_unit/3
        self.m = 4

        # initial direction - to the left
        self.direction = 'L'


    def is_mid_air(self):
        return self.v_y != 0

    def is_jumping(self):
        return self.v_y < 0

    def is_falling(self):
        return self.v_y > 0

    def is_crashed(self):
        return (self.rect.left < 50 or self.rect.right > 600)

    def is_mid_x(self):
        return self.is_moving_left() or self.is_moving_right()

    def is_moving_right(self):
        return self.v_x > 0

    def is_moving_left(self):
        return self.v_x < 0


    # handle user input
    def move(self, screen, event, gameboard):
        
        keystate = pygame.key.get_pressed()

        if not self.is_mid_x():

            ## here need to change to also use the dictionary CONTROLS - tbd later
            #if (keystate[K_RIGHT] or keystate[K_d]):

            if event.type == pygame.KEYDOWN:

                if event.key in CONTROLS["G_RIGHT"]:
                    self.direction = 'R'
                    self.v_x = self.speed_unit

                if event.key in CONTROLS["G_LEFT"]:
                    self.direction = 'L'
                    self.v_x = - self.speed_unit


            # fall to the right/left if obstacle's end is reached
            # FIXME: commented out because `gameboard` implementation is not yet ready
            if self.direction == 'R' and  not gameboard.is_colliding_wall_right(self):
                self.v_x = self.speed_unit

            if self.direction == 'L' and not gameboard.is_colliding_wall_left(self):
                self.v_x = - self.speed_unit


        # call movement functions after handling user input
        self.call_movement_functions(gameboard)

    
    def call_movement_functions(self, gameboard):
        
        self.move_x(gameboard)
        self.move_y(gameboard)
        self.handle_images()


    def move_x(self, gameboard):
        # find x position of the closest obstacle edges on the right and left side of the player
        limit_right = gameboard.limit_right(self)
        limit_left = gameboard.limit_left(self)

        # stop movement if collision on either side of the player takes place
        if self.is_moving_right() and self.v_x > limit_right:
            wall = self.rect.right + limit_right
            self.stop_movement_x(wall - self.rect.width)
        
        elif self.is_moving_left() and self.v_x < limit_left:
            wall = self.rect.left + limit_left
            self.stop_movement_x(wall)
        
        else:
            # Free movement -> update the position based on the speed
            self.rect.x += self.v_x

    def move_y(self, gameboard):
        limit = gameboard.limit_under(self)

        # Calculate y-acceleration (gravity pull)
        a = self.m * self.G

        # Update y-speed with new acceleration
        self.v_y += a

        will_hit_floor = self.v_y > limit

        if will_hit_floor:
            floor = self.rect.bottom + limit
            self.stop_movement_y(floor)
        else:
            # Update y-position
            self.rect.y += self.v_y

    def jump(self):
        self.v_y = -self.speed_unit * self.LEAP_FORCE

    def stop_movement_x(self, x):
        self.rect.x = x
        self.v_x = 0

    def stop_movement_y(self, y):
        self.rect.bottom = y
        self.v_y = 0

    def handle_images(self):

        #if self.is_mid_x():
        if self.is_crashed():
            img = image_paths.PLAYER_CRASH
        
        elif self.is_moving_right():
            img = image_paths.PLAYER_MOVE_RIGHT

        elif self.is_moving_left():
            img = image_paths.PLAYER_MOVE_LEFT

        else:
            img = image_paths.PLAYER_MAIN
        
        self.image = image.Image.load(img)

     
    def append_bullet(self, event, gameboard, width = 5):

        if event.type == pygame.KEYDOWN:

            if event.key in CONTROLS["G_SHOOT"]:
                gameboard.bullets.append(self.create_bullet(
                    (width, width * 1.5),
                    x = (self.rect.left + self.rect.right) / 2 - width / 2,
                    y = self.rect.top))

    def create_bullet(self, size, x, y):
        shape = rectangle(Point(0, 0), Point(*size))
        return GameObject(
            image = image.Image.create(shape, color = Colors.MAGENTA ),
            x = x,
            y = y)

    def move_bullets(self, gameboard, bullet_speed):
        for bullet in gameboard.bullets:
            bullet.rect.y -= bullet_speed