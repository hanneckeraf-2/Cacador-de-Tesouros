#!/usr/bin/python
# -*- coding: utf-8 -*-
import pygame

from code.Const import TILE_SIZE, WORLD_TILES, PLAYER_MOVE_DELAY
from code.Entity import Entity

CHAR_W = TILE_SIZE
CHAR_H = TILE_SIZE


class Player(Entity):
    def __init__(self, tile_x: int, tile_y: int):
        super().__init__('Player')
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.direction = 'down'
        self.anim_frame = 0
        self.move_cooldown = 0
        self.lives = 3
        self.gold = 0
        self.keys = 0

        def _load(path):
            return pygame.transform.smoothscale(
                pygame.image.load(path).convert_alpha(), (CHAR_W, CHAR_H)
            )

        self.sprites = {
            'up':    [_load('./asset/personagem-up1.png'),    _load('./asset/personagem-up2.png')],
            'down':  [_load('./asset/personagem-down1.png'),  _load('./asset/personagem-down2.png')],
            'left':  [_load('./asset/personagem-left1.png'),  _load('./asset/personagem-left2.png')],
            'right': [_load('./asset/personagem-right1.png'), _load('./asset/personagem-right2.png')],
        }
        self.surf = self.sprites[self.direction][self.anim_frame]

    def move(self, blocked: set = None):
        pressed = pygame.key.get_pressed()
        new_dir = None
        if pressed[pygame.K_UP]:
            new_dir = 'up'
        elif pressed[pygame.K_DOWN]:
            new_dir = 'down'
        elif pressed[pygame.K_LEFT]:
            new_dir = 'left'
        elif pressed[pygame.K_RIGHT]:
            new_dir = 'right'

        if new_dir is None:
            if self.move_cooldown > 0:
                self.move_cooldown -= 1
            return

        # Always update facing direction, even when blocked or in cooldown
        direction_changed = new_dir != self.direction
        if direction_changed:
            self.direction = new_dir
            self.anim_frame = 0
            self.surf = self.sprites[self.direction][self.anim_frame]

        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        nx, ny = self.tile_x, self.tile_y
        if new_dir == 'up':
            ny -= 1
        elif new_dir == 'down':
            ny += 1
        elif new_dir == 'left':
            nx -= 1
        elif new_dir == 'right':
            nx += 1

        if not (0 <= nx < WORLD_TILES and 1 <= ny <= WORLD_TILES - 2):
            return
        if blocked and (nx, ny) in blocked:
            return

        self.tile_x, self.tile_y = nx, ny
        self.move_cooldown = PLAYER_MOVE_DELAY

        # Only toggle animation frame when continuing in the same direction
        if not direction_changed:
            self.anim_frame = 1 - self.anim_frame
            self.surf = self.sprites[self.direction][self.anim_frame]

    def get_screen_pos(self, cam_x: int, cam_y: int) -> tuple:
        sx = self.tile_x * TILE_SIZE - cam_x
        sy = self.tile_y * TILE_SIZE - cam_y
        return sx, sy
