#!/usr/bin/python
# -*- coding: utf-8 -*-
import pygame
from pygame import Surface

from code.Const import TILE_SIZE, WIN_WIDTH, WIN_HEIGHT, WORLD_TILES

WALL_ROWS = (0, WORLD_TILES - 1)


class Background:
    def __init__(self, floor_path: str, wall_h_path: str = None):
        raw = pygame.image.load(floor_path).convert()
        self.tile = pygame.transform.smoothscale(raw, (TILE_SIZE, TILE_SIZE))

        self.wall_h = None
        if wall_h_path:
            raw_w = pygame.image.load(wall_h_path).convert_alpha()
            self.wall_h = pygame.transform.smoothscale(raw_w, (TILE_SIZE, TILE_SIZE))

    def draw(self, window: Surface, cam_x: int, cam_y: int):
        start_tx = cam_x // TILE_SIZE
        start_ty = cam_y // TILE_SIZE
        end_tx = start_tx + WIN_WIDTH // TILE_SIZE + 2
        end_ty = start_ty + WIN_HEIGHT // TILE_SIZE + 2

        for ty in range(start_ty, min(end_ty, WORLD_TILES)):
            for tx in range(start_tx, min(end_tx, WORLD_TILES)):
                sx = tx * TILE_SIZE - cam_x
                sy = ty * TILE_SIZE - cam_y
                window.blit(self.tile, (sx, sy))
                if self.wall_h and ty in WALL_ROWS:
                    window.blit(self.wall_h, (sx, sy))
