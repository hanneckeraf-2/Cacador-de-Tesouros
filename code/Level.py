#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import sys

import pygame
from pygame import Surface
from pygame.font import Font

from code.Background import Background
from code.Const import WIN_WIDTH, WIN_HEIGHT, TILE_SIZE, WORLD_TILES, C_WHITE, C_YELLOW
from code.Player import Player
from code.Treasure import generate_chests


class Level:
    def __init__(self, window: Surface, name: str):
        self.window = window
        self.name = name
        self.bg = Background(f'./asset/{name}.png', f'./asset/{name}-frontal.png')
        self.player = Player(tile_x=25, tile_y=25)
        self.door_surf = pygame.transform.smoothscale(
            pygame.image.load('./asset/porta.png').convert_alpha(),
            (TILE_SIZE, TILE_SIZE)
        )
        self.level_num = 1
        self.door_x = 0
        self.door_y = 0
        self._place_door()
        self.chests = generate_chests()

    def _place_door(self):
        self.door_y = random.choice([0, WORLD_TILES - 1])
        self.door_x = random.randint(0, WORLD_TILES - 1)

    def _door_trigger_pos(self) -> tuple[int, int]:
        if self.door_y == 0:
            return self.door_x, 1
        return self.door_x, WORLD_TILES - 2

    def _player_at_door(self) -> bool:
        trigger_pos = self._door_trigger_pos()
        required_dir = 'up' if self.door_y == 0 else 'down'
        return (
            (self.player.tile_x, self.player.tile_y) == trigger_pos
            and self.player.direction == required_dir
        )

    def run(self):
        pygame.mixer.music.load('./asset/TrilhaJogo1.mp3')
        pygame.mixer.music.play(-1)
        self._show_intro_panel()
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)

            cam_x, cam_y = self._calc_camera()
            self.bg.draw(self.window, cam_x, cam_y)

            dx = self.door_x * TILE_SIZE - cam_x
            dy = self.door_y * TILE_SIZE - cam_y
            self.window.blit(self.door_surf, (dx, dy))

            for chest in self.chests:
                cx, cy = chest.get_screen_pos(cam_x, cam_y)
                self.window.blit(chest.surf, (cx, cy))

            px, py = self.player.get_screen_pos(cam_x, cam_y)
            self.window.blit(self.player.surf, (px, py))

            self._hud_text(14, f'Nível: {self.level_num}', C_WHITE, (8, 8))
            self._hud_text(14, f'Vidas: {self.player.lives}', C_WHITE, (8, 26))
            self._hud_text(14, f'Ouro: {self.player.gold}', C_WHITE, (8, 44))
            self._hud_text(14, f'Chaves: {self.player.keys}', C_WHITE, (8, 62))

            chest_tiles = {(c.tile_x, c.tile_y) for c in self.chests}
            self.player.move(chest_tiles)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_SPACE:
                        if self._player_at_door():
                            self._next_level()
                        else:
                            self._interact_chest()

            pygame.display.flip()

    def _next_level(self):
        self.level_num += 1
        self.player.tile_x = 25
        self.player.tile_y = 25
        self.player.direction = 'down'
        self.player.anim_frame = 0
        self.player.surf = self.player.sprites['down'][0]
        self.player.move_cooldown = 0
        self._place_door()
        self.chests = generate_chests()

    def _interact_chest(self):
        player_pos = (self.player.tile_x, self.player.tile_y)
        for chest in self.chests:
            if (
                chest.interact_pos() == player_pos
                and chest.required_direction() == self.player.direction
            ):
                chest.open()
                break

    def _show_intro_panel(self):
        lines = [
            ('Cada nível possui 15 baús.', C_WHITE, 15),
            ('Apenas 1 contém a chave para avançar para o próximo nível.', C_WHITE, 15),
            ('Os outros podem conter tesouros ou poções.', C_WHITE, 15),
            ('', C_WHITE, 10),
            ('TOME CUIDADO: alguns baús possuem perigos escondidos.', C_YELLOW, 15),
            ('', C_WHITE, 14),
            ('Pressione qualquer tecla para começar...', C_WHITE, 13),
        ]

        pad = 40
        panel_w = WIN_WIDTH - pad * 2
        panel_h = WIN_HEIGHT - pad * 2

        while True:
            cam_x, cam_y = self._calc_camera()
            self.bg.draw(self.window, cam_x, cam_y)

            overlay = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 210))
            self.window.blit(overlay, (pad, pad))
            pygame.draw.rect(self.window, C_WHITE, (pad, pad, panel_w, panel_h), 2)

            y = pad + 28
            for text, color, size in lines:
                if text:
                    font = pygame.font.SysFont('helvetica', size)
                    surf = font.render(text, True, color)
                    rect = surf.get_rect(centerx=WIN_WIDTH // 2, top=y)
                    self.window.blit(surf, rect)
                y += size + 10

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    return

    def _calc_camera(self) -> tuple[int, int]:
        cam_x = self.player.tile_x * TILE_SIZE + TILE_SIZE // 2 - WIN_WIDTH // 2
        cam_y = self.player.tile_y * TILE_SIZE + TILE_SIZE // 2 - WIN_HEIGHT // 2
        cam_x = max(0, min(cam_x, WORLD_TILES * TILE_SIZE - WIN_WIDTH))
        cam_y = max(0, min(cam_y, WORLD_TILES * TILE_SIZE - WIN_HEIGHT))
        return cam_x, cam_y

    def _hud_text(self, size: int, text: str, color: tuple, pos: tuple):
        font: Font = pygame.font.SysFont('helvetica', size)
        surf = font.render(text, True, color).convert_alpha()
        self.window.blit(surf, surf.get_rect(left=pos[0], top=pos[1]))
