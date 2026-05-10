#!/usr/bin/python
# -*- coding: utf-8 -*-
import random

import pygame

from code.Const import TILE_SIZE, WORLD_TILES
from code.Entity import Entity

ENEMY_COUNT = 3
ENEMY_MOVE_INTERVAL = 60  # frames (1 segundo a 60 FPS)
CHASE_DISTANCE = 5


class Inimigo(Entity):
    def __init__(self, tile_x: int, tile_y: int):
        super().__init__('Inimigo')
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.direction = 'down'
        self.anim_frame = 0
        self.move_timer = 0
        self.threat_timer = 0

        def _load(path):
            return pygame.transform.smoothscale(
                pygame.image.load(path).convert_alpha(), (TILE_SIZE, TILE_SIZE)
            )

        down1 = _load('./asset/inimigo-down1.png')
        self.sprites = {
            'up':    [_load('./asset/inimigo-up1.png'),    _load('./asset/inimigo-up2.png')],
            'down':  [down1, down1],
            'left':  [_load('./asset/inimigo-left1.png'),  _load('./asset/inimigo-left2.png')],
            'right': [_load('./asset/inimigo-right1.png'), _load('./asset/inimigo-right2.png')],
        }
        self.surf = self.sprites[self.direction][self.anim_frame]

    def move(self, player_tile: tuple[int, int], blocked: set):
        self.move_timer += 1
        if self.move_timer < ENEMY_MOVE_INTERVAL:
            return
        self.move_timer = 0

        px, py = player_tile
        dist = abs(self.tile_x - px) + abs(self.tile_y - py)

        if dist > CHASE_DISTANCE:
            self._move_random(blocked | {player_tile})
        else:
            self._move_toward(px, py, blocked, player_tile)

    def _move_random(self, blocked: set):
        dirs = ['up', 'down', 'left', 'right']
        random.shuffle(dirs)
        for d in dirs:
            nx, ny = self._apply_dir(d)
            if self._in_bounds(nx, ny) and (nx, ny) not in blocked:
                self._commit(nx, ny, d)
                return

    def _move_toward(self, px: int, py: int, blocked: set, player_tile: tuple):
        dx = px - self.tile_x
        dy = py - self.tile_y

        preferred = []
        if abs(dx) >= abs(dy):
            if dx > 0: preferred.append('right')
            elif dx < 0: preferred.append('left')
            if dy > 0: preferred.append('down')
            elif dy < 0: preferred.append('up')
        else:
            if dy > 0: preferred.append('down')
            elif dy < 0: preferred.append('up')
            if dx > 0: preferred.append('right')
            elif dx < 0: preferred.append('left')

        all_dirs = ['up', 'down', 'left', 'right']
        order = preferred + [d for d in all_dirs if d not in preferred]

        for d in order:
            nx, ny = self._apply_dir(d)
            if not self._in_bounds(nx, ny):
                continue
            if (nx, ny) == player_tile:
                # Adjacente ao jogador: vira em direção a ele e para (ataque tratado em Level)
                if self.direction != d:
                    self.direction = d
                    self.surf = self.sprites[self.direction][self.anim_frame]
                return
            if (nx, ny) not in blocked:
                self._commit(nx, ny, d)
                return

    def _apply_dir(self, direction: str) -> tuple[int, int]:
        nx, ny = self.tile_x, self.tile_y
        if direction == 'up':    ny -= 1
        elif direction == 'down': ny += 1
        elif direction == 'left':  nx -= 1
        elif direction == 'right': nx += 1
        return nx, ny

    def _in_bounds(self, nx: int, ny: int) -> bool:
        return 0 <= nx < WORLD_TILES and 1 <= ny <= WORLD_TILES - 2

    def _commit(self, nx: int, ny: int, direction: str):
        self.tile_x, self.tile_y = nx, ny
        if direction != self.direction:
            self.direction = direction
            self.anim_frame = 0
        else:
            self.anim_frame = 1 - self.anim_frame
        self.surf = self.sprites[self.direction][self.anim_frame]

    def get_screen_pos(self, cam_x: int, cam_y: int) -> tuple[int, int]:
        return self.tile_x * TILE_SIZE - cam_x, self.tile_y * TILE_SIZE - cam_y


def generate_enemies(count: int = ENEMY_COUNT) -> list[Inimigo]:
    enemies = []
    occupied: set[tuple[int, int]] = set()
    attempts = 0
    while len(enemies) < count and attempts < 1000:
        attempts += 1
        edge = random.randint(0, 3)
        if edge == 0:    # borda superior
            x, y = random.randint(0, WORLD_TILES - 1), 1
        elif edge == 1:  # borda inferior
            x, y = random.randint(0, WORLD_TILES - 1), WORLD_TILES - 2
        elif edge == 2:  # borda esquerda
            x, y = 0, random.randint(1, WORLD_TILES - 2)
        else:            # borda direita
            x, y = WORLD_TILES - 1, random.randint(1, WORLD_TILES - 2)
        if (x, y) not in occupied:
            enemies.append(Inimigo(x, y))
            occupied.add((x, y))
    return enemies
