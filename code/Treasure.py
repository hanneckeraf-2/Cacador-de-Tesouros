#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import pygame

from code.Const import TILE_SIZE, WORLD_TILES

CHEST_COUNT = 15
CHEST_MARGIN = 2


class Chest:
    def __init__(self, tile_x: int, tile_y: int, orientation: str):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.orientation = orientation  # 'up' or 'down'
        self.is_open = False

        def _load(path):
            return pygame.transform.smoothscale(
                pygame.image.load(path).convert_alpha(), (TILE_SIZE, TILE_SIZE)
            )

        self.sprite_closed = _load(f'./asset/bau-{orientation}-fechado.png')
        self.sprite_open = _load(f'./asset/bau-{orientation}-aberto.png')
        self.surf = self.sprite_closed

    def open(self):
        if not self.is_open:
            self.is_open = True
            self.surf = self.sprite_open

    def interact_pos(self) -> tuple[int, int]:
        if self.orientation == 'up':
            return self.tile_x, self.tile_y + 1
        return self.tile_x, self.tile_y - 1

    def required_direction(self) -> str:
        return 'up' if self.orientation == 'up' else 'up'

    def get_screen_pos(self, cam_x: int, cam_y: int) -> tuple[int, int]:
        return self.tile_x * TILE_SIZE - cam_x, self.tile_y * TILE_SIZE - cam_y


def generate_chests() -> list[Chest]:
    chests = []
    occupied: set[tuple[int, int]] = set()

    attempts = 0
    while len(chests) < CHEST_COUNT and attempts < 10_000:
        attempts += 1
        x = random.randint(CHEST_MARGIN, WORLD_TILES - 1 - CHEST_MARGIN)
        y = random.randint(CHEST_MARGIN, WORLD_TILES - 1 - CHEST_MARGIN)

        neighbors = {(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
        if neighbors & occupied:
            continue

        orientation = random.choice(['up', 'down'])
        chests.append(Chest(x, y, orientation))
        occupied.add((x, y))

    return chests
