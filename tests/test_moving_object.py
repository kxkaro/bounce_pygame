import pygame
from unittest import TestCase, mock

from silnik import image
from silnik.rendering.point import Point

from bounce.gameboard import GameBoard
from bounce.game_object import GameObject
from bounce.moving_object import MovingObject
from bounce import image_paths

class TestMovingObject(TestCase):
    """
    Base TestCase to share the setup logic and data
    """
    def setUp(self):
        size = width, height = (1280, 720)
        screen = pygame.display.set_mode(size)  # FIXME: decouple GameObject from pygame.display
        img = image.Image.load(image_paths.PLAYER_MAIN)  # some image is needed to construct an GameObject
        
        self.object = MovingObject(img)
        self.base_rect = self.object.rect

    def make_wall(self, x=0, y=0):
        img = image.Image.create(self.base_rect.clone())
        return GameObject(
            img,
            x=x + self.base_rect.width,
            y=y + self.base_rect.height)

class TestMove(TestMovingObject):
    def setUp(self):
        super().setUp()
        self.object.v_x = 100

    def test_updates_x_position(self):
        distance = self.object.v_x * 1.1  # > self.v_x
        wall_right = self.make_wall(x=distance)
        
        gameboard = GameBoard([wall_right], [], [], [])

        self.object.move_x(gameboard)
        self.assertEqual(
            self.object.rect.x,
            self.object.v_x)

    def test_calls_handler_on_collision(self):
        distance = self.object.v_x * 0.1  # < self.v_x
        wall_right = self.make_wall(x=distance)
        
        gameboard = GameBoard([wall_right], [], [], [])

        expected_direction = 'R'
        expected_location = Point(
            self.base_rect.width + distance - 1,
            0)

        with mock.patch.object(self.object, 'on_collision') as mock_collision:
            self.object.move_x(gameboard)
            mock_collision.assert_called_once_with(
                direction=expected_direction,
                location=expected_location)