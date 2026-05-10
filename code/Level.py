#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import sys

import pygame
from pygame import Surface
from pygame.font import Font

from code.Background import Background
from code.Const import WIN_WIDTH, WIN_HEIGHT, TILE_SIZE, WORLD_TILES, C_WHITE, C_YELLOW, C_ORANGE, C_GOLD, C_GREEN
from code.Player import Player
from code.Score import Score
from code.Enemy import generate_enemies
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

        def _load_hud(path):
            raw = pygame.image.load(path).convert_alpha()
            h = 24
            w = raw.get_width() * h // raw.get_height()
            return pygame.transform.smoothscale(raw, (w, h))

        self.hud_heart_full = _load_hud('./asset/coracao_cheio.png')
        self.hud_heart_empty = _load_hud('./asset/coracao_vazio.png')
        self.hud_gold_icon = _load_hud('./asset/moedas_ouro.png')
        self.hud_key_icon = _load_hud('./asset/chaves.png')
        self.hud_chest_icon = _load_hud('./asset/bau-down-fechado.png')
        self.enemies = generate_enemies()

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

            for enemy in self.enemies:
                ex, ey = enemy.get_screen_pos(cam_x, cam_y)
                self.window.blit(enemy.surf, (ex, ey))

            px, py = self.player.get_screen_pos(cam_x, cam_y)
            self.window.blit(self.player.surf, (px, py))

            self._draw_hud()

            chest_tiles = {(c.tile_x, c.tile_y) for c in self.chests}
            enemy_tiles = {(e.tile_x, e.tile_y) for e in self.enemies}
            self.player.move(chest_tiles | enemy_tiles)

            self._move_enemies(chest_tiles)
            if self._check_enemy_attacks():
                return

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_SPACE:
                        if self._player_at_door():
                            if self.player.keys > 0:
                                self._next_level()
                            else:
                                self._show_message_panel([
                                    ('Você precisa encontrar a chave', C_YELLOW, 15),
                                    ('para avançar para o próximo nível!', C_YELLOW, 15),
                                ])
                        elif self._try_disarm_enemy():
                            pass
                        elif self._interact_chest():
                            return

            pygame.display.flip()

    def _next_level(self):
        self.level_num += 1
        self.player.tile_x = 25
        self.player.tile_y = 25
        self.player.direction = 'down'
        self.player.anim_frame = 0
        self.player.surf = self.player.sprites['down'][0]
        self.player.move_cooldown = 0
        self.player.keys -= 1
        self._place_door()
        self.chests = generate_chests()
        self.enemies = generate_enemies()

    def _facing_toward(self, direction: str, from_pos: tuple, to_pos: tuple) -> bool:
        fx, fy = from_pos
        tx, ty = to_pos
        dx, dy = tx - fx, ty - fy
        return (
            (direction == 'right' and dx == 1  and dy == 0) or
            (direction == 'left'  and dx == -1 and dy == 0) or
            (direction == 'down'  and dx == 0  and dy == 1) or
            (direction == 'up'    and dx == 0  and dy == -1)
        )

    def _move_enemies(self, chest_tiles: set):
        player_tile = (self.player.tile_x, self.player.tile_y)
        for enemy in self.enemies:
            other = {(e.tile_x, e.tile_y) for e in self.enemies if e is not enemy}
            enemy.move(player_tile, chest_tiles | other)

    def _check_enemy_attacks(self) -> bool:
        player_pos = (self.player.tile_x, self.player.tile_y)
        attackers = []
        for enemy in self.enemies:
            if self._facing_toward(enemy.direction, (enemy.tile_x, enemy.tile_y), player_pos):
                enemy.threat_timer += 1
                if enemy.threat_timer >= 60:
                    attackers.append(enemy)
            else:
                enemy.threat_timer = 0
        for enemy in attackers:
            self.enemies.remove(enemy)
            self.player.lives -= 1
            self._show_message_panel([
                ('O fantasma alcançou você! Perdeu uma vida.', C_ORANGE, 15),
            ])
            if self.player.lives <= 0:
                self._show_game_over()
                return True
        return False

    def _try_disarm_enemy(self) -> bool:
        player_pos = (self.player.tile_x, self.player.tile_y)
        for enemy in self.enemies:
            enemy_pos = (enemy.tile_x, enemy.tile_y)
            player_faces = self._facing_toward(self.player.direction, player_pos, enemy_pos)
            enemy_faces = self._facing_toward(enemy.direction, enemy_pos, player_pos)
            if player_faces and not enemy_faces:
                self.enemies.remove(enemy)
                self._show_message_panel([
                    ('Você desarmou o fantasma!', C_GREEN, 15),
                    ('Ele não vai mais te incomodar.', C_GREEN, 15),
                ])
                return True
        return False

    def _interact_chest(self) -> bool:
        player_pos = (self.player.tile_x, self.player.tile_y)
        for chest in self.chests:
            if (
                not chest.is_open
                and chest.interact_pos() == player_pos
                and chest.required_direction() == self.player.direction
            ):
                chest.open()
                return self._apply_chest_effect(chest)
        return False

    def _apply_chest_effect(self, chest) -> bool:
        content = chest.content
        if content == 'key':
            self.player.keys += 1
            lines = [
                ('Você achou a chave da porta secreta!', C_GOLD, 15),
                ('Agora pode avançar para o próximo nível.', C_WHITE, 15),
            ]
        elif content == 'potion':
            if self.player.lives < 3:
                self.player.lives += 1
                lines = [('Você encontrou uma poção de cura. +1 vida!', C_GREEN, 15)]
            else:
                lines = [('Que pena, não há nada aqui.', C_WHITE, 15)]
        elif content == 'poison':
            self.player.lives -= 1
            lines = [
                ('Ao abrir o baú, um veneno mortal saiu lá de dentro.', C_ORANGE, 15),
                ('Você perdeu 1 vida.', C_ORANGE, 15),
            ]
        elif isinstance(content, tuple):  # ('gold', amount)
            amount = content[1]
            self.player.gold += amount
            lines = [(f'Você encontrou {amount} moedas de ouro!', C_GOLD, 15)]
        else:  # empty
            lines = [('Que pena, não há nada aqui.', C_WHITE, 15)]

        self._show_message_panel(lines)

        if self.player.lives <= 0:
            self._show_game_over()
            return True
        return False

    def _show_message_panel(self, lines: list):
        all_lines = lines + [
            ('', C_WHITE, 10),
            ('Pressione qualquer tecla para continuar...', C_WHITE, 13),
        ]
        pad = 60
        panel_w = WIN_WIDTH - pad * 2
        panel_h = WIN_HEIGHT - pad * 2

        while True:
            cam_x, cam_y = self._calc_camera()
            self.bg.draw(self.window, cam_x, cam_y)

            overlay = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 210))
            self.window.blit(overlay, (pad, pad))
            pygame.draw.rect(self.window, C_WHITE, (pad, pad, panel_w, panel_h), 2)

            y = pad + 30
            for text, color, size in all_lines:
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

    def _show_game_over(self):
        name_chars = []

        while True:
            cam_x, cam_y = self._calc_camera()
            self.bg.draw(self.window, cam_x, cam_y)

            pad = 40
            panel_w = WIN_WIDTH - pad * 2
            panel_h = WIN_HEIGHT - pad * 2
            overlay = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            self.window.blit(overlay, (pad, pad))
            pygame.draw.rect(self.window, C_WHITE, (pad, pad, panel_w, panel_h), 2)

            info_lines = [
                ('FIM DE JOGO', C_YELLOW, 28),
                ('', C_WHITE, 8),
                (f'Nível alcançado: {self.level_num}', C_WHITE, 15),
                (f'Moedas coletadas: {self.player.gold}', C_GOLD, 15),
                ('', C_WHITE, 12),
                ('Digite suas iniciais (3 letras):', C_WHITE, 14),
            ]

            y = pad + 20
            for text, color, size in info_lines:
                if text:
                    font = pygame.font.SysFont('helvetica', size)
                    surf = font.render(text, True, color)
                    rect = surf.get_rect(centerx=WIN_WIDTH // 2, top=y)
                    self.window.blit(surf, rect)
                y += size + 10

            display = ' '.join(name_chars + ['_'] * (3 - len(name_chars)))
            input_font = pygame.font.SysFont('helvetica', 24)
            input_surf = input_font.render(display, True, C_YELLOW)
            input_rect = input_surf.get_rect(centerx=WIN_WIDTH // 2, top=y + 5)
            self.window.blit(input_surf, input_rect)

            if len(name_chars) == 3:
                hint_surf = pygame.font.SysFont('helvetica', 13).render(
                    'Pressione ENTER para confirmar', True, C_WHITE
                )
                self.window.blit(hint_surf, hint_surf.get_rect(centerx=WIN_WIDTH // 2, top=input_rect.bottom + 10))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and len(name_chars) == 3:
                        Score().save(''.join(name_chars), self.player.gold, self.level_num)
                        return
                    elif event.key == pygame.K_BACKSPACE and name_chars:
                        name_chars.pop()
                    elif len(name_chars) < 3 and event.unicode.isalpha():
                        name_chars.append(event.unicode.upper())

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

    def _draw_hud(self):
        # --- Canto superior esquerdo ---
        x, y = 8, 8
        hw = self.hud_heart_full.get_width()
        for i in range(3):
            icon = self.hud_heart_full if i < self.player.lives else self.hud_heart_empty
            self.window.blit(icon, (x + i * (hw + 3), y))
        y += 30
        self.window.blit(self.hud_gold_icon, (x, y))
        gw = self.hud_gold_icon.get_width()
        self._hud_text(13, str(self.player.gold), C_GOLD, (x + gw + 5, y + 6))
        y += 30
        self.window.blit(self.hud_key_icon, (x, y))
        kw = self.hud_key_icon.get_width()
        self._hud_text(13, str(self.player.keys), C_WHITE, (x + kw + 5, y + 6))
        if self.player.keys > 0:
            y += 26
            door_dist = abs(self.door_x - self.player.tile_x) + abs(self.door_y - self.player.tile_y)
            self._hud_text(12, f'Distância para a porta: {door_dist}', C_YELLOW, (x, y))
        y += 30
        opened = sum(1 for c in self.chests if c.is_open)
        self.window.blit(self.hud_chest_icon, (x, y))
        cw = self.hud_chest_icon.get_width()
        self._hud_text(13, f'{opened}/15', C_WHITE, (x + cw + 5, y + 6))

        # --- Canto inferior direito (empilhado de baixo para cima) ---
        rx = WIN_WIDTH - 8
        by = WIN_HEIGHT - 8
        closed = [c for c in self.chests if not c.is_open]
        if closed:
            dist = min(abs(c.tile_x - self.player.tile_x) + abs(c.tile_y - self.player.tile_y) for c in closed)
            s = pygame.font.SysFont('helvetica', 12).render(f'Distância para o baú mais próximo: {dist}', True, C_WHITE).convert_alpha()
            self.window.blit(s, s.get_rect(right=rx, bottom=by))
            by -= s.get_height() + 4
        s = pygame.font.SysFont('helvetica', 12).render(f'Pos: {self.player.tile_x}, {self.player.tile_y}', True, C_WHITE).convert_alpha()
        self.window.blit(s, s.get_rect(right=rx, bottom=by))
        by -= s.get_height() + 4
        s = pygame.font.SysFont('helvetica', 13).render(f'Nível: {self.level_num}', True, C_WHITE).convert_alpha()
        self.window.blit(s, s.get_rect(right=rx, bottom=by))

    def _hud_text(self, size: int, text: str, color: tuple, pos: tuple):
        font: Font = pygame.font.SysFont('helvetica', size)
        surf = font.render(text, True, color).convert_alpha()
        self.window.blit(surf, surf.get_rect(left=pos[0], top=pos[1]))
