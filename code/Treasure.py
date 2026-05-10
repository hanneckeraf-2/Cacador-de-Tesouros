#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import pygame

from code.Const import TILE_SIZE, WORLD_TILES

CHEST_COUNT = 15
CHEST_MARGIN = 2


class Chest:
    def __init__(self, tile_x: int, tile_y: int, content: 'str | tuple'):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.content = content  # 'key', 'empty', 'potion', 'poison', or ('gold', amount)
        self.is_open = False

        def _load(path):
            return pygame.transform.smoothscale(
                pygame.image.load(path).convert_alpha(), (TILE_SIZE, TILE_SIZE)
            )

        self.sprite_closed = _load('./asset/bau-up-fechado.png')
        self.sprite_open = _load('./asset/bau-up-aberto.png')
        self.surf = self.sprite_closed

    def open(self):
        if not self.is_open:
            self.is_open = True
            self.surf = self.sprite_open

    def interact_pos(self) -> tuple[int, int]:
        return self.tile_x, self.tile_y + 1

    def required_direction(self) -> str:
        return 'up'

    def get_screen_pos(self, cam_x: int, cam_y: int) -> tuple[int, int]:
        return self.tile_x * TILE_SIZE - cam_x, self.tile_y * TILE_SIZE - cam_y


def generate_chests() -> list[Chest]:
    gold_count = CHEST_COUNT - 1 - 4 - 3 - 3  # = 4
    pool = (
        ['key'] +
        ['empty'] * 4 +
        ['potion'] * 3 +
        ['poison'] * 3 +
        [('gold', random.randint(1, 20)) for _ in range(gold_count)]
    )
    random.shuffle(pool)

    chests = []
    occupied: set[tuple[int, int]] = set()
    content_idx = 0

    attempts = 0
    while len(chests) < CHEST_COUNT and attempts < 10_000:
        attempts += 1
        x = random.randint(CHEST_MARGIN, WORLD_TILES - 1 - CHEST_MARGIN)
        y = random.randint(CHEST_MARGIN, WORLD_TILES - 1 - CHEST_MARGIN)

        neighbors = {(x + dx, y + dy) for dx in range(-2, 3) for dy in range(-2, 3)}
        if neighbors & occupied:
            continue

        chests.append(Chest(x, y, pool[content_idx]))
        occupied.add((x, y))
        content_idx += 1

    return chests
