#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

import pygame
from pygame import Surface, Rect
from pygame.font import Font

from code.Const import WIN_WIDTH, WIN_HEIGHT, C_WHITE, C_YELLOW, C_GOLD, C_BLACK, C_DARK_GRAY, MENU_OPTION
from code.Score import Score

MENU_LEFT_MARGIN = 100

PANEL_W = 420
PANEL_H = 210
PANEL_X = (WIN_WIDTH - PANEL_W) // 2
PANEL_Y = (WIN_HEIGHT - PANEL_H) // 2
PANEL_COLOR = (25, 25, 25)
PANEL_BORDER_COLOR = C_GOLD


class Menu:
    def __init__(self, window: Surface):
        self.window = window
        raw = pygame.image.load('./asset/MenuBg.png').convert_alpha()
        self.surf = pygame.transform.scale(raw, (WIN_WIDTH, WIN_HEIGHT))
        self.rect = self.surf.get_rect(left=0, top=0)

    def run(self):
        menu_option = 0
        pygame.mixer_music.load('./asset/Menu.mp3')
        pygame.mixer_music.set_volume(0.3)
        pygame.mixer_music.play(-1)

        while True:
            self._draw_menu(menu_option)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        menu_option = (menu_option + 1) % len(MENU_OPTION)
                    if event.key == pygame.K_UP:
                        menu_option = (menu_option - 1) % len(MENU_OPTION)
                    if event.key == pygame.K_RETURN:
                        if MENU_OPTION[menu_option] == 'Como Jogar':
                            self.show_how_to_play()
                        elif MENU_OPTION[menu_option] == 'Recordes':
                            self.show_records()
                        elif MENU_OPTION[menu_option] == 'Sobre o Jogo':
                            self.show_about()
                        elif MENU_OPTION[menu_option] == 'Sair':
                            pygame.quit()
                            sys.exit()
                        else:
                            return MENU_OPTION[menu_option]

    def _draw_menu(self, menu_option: int):
        self.window.blit(source=self.surf, dest=self.rect)
        self.menu_text(38, 'Caçador de Tesouros', C_GOLD, (WIN_WIDTH / 2, 80),
                       outline_color=C_DARK_GRAY, center=True)
        for i, option in enumerate(MENU_OPTION):
            color = C_YELLOW if i == menu_option else C_WHITE
            self.menu_text(22, option, color, (MENU_LEFT_MARGIN, 190 + 30 * i),
                           outline_color=C_BLACK, center=False)

    def show_how_to_play(self):
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))

        controls = [
            ('← ↑ ↓ →', 'Movimentar o personagem'),
            ('SPACE',    'Interagir: abrir baú, desarmar inimigo, abrir portas'),
        ]

        while True:
            self._draw_menu(menu_option=-1)
            self.window.blit(overlay, (0, 0))

            panel_rect = pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, PANEL_H)
            pygame.draw.rect(self.window, PANEL_COLOR, panel_rect, border_radius=8)
            pygame.draw.rect(self.window, PANEL_BORDER_COLOR, panel_rect, width=2, border_radius=8)

            self.menu_text(20, 'Como Jogar', C_GOLD, (WIN_WIDTH / 2, PANEL_Y + 22),
                           outline_color=C_DARK_GRAY, center=True)

            pygame.draw.line(self.window, C_DARK_GRAY,
                             (PANEL_X + 16, PANEL_Y + 42),
                             (PANEL_X + PANEL_W - 16, PANEL_Y + 42))

            text_x = PANEL_X + 20
            for row, (key, description) in enumerate(controls):
                y = PANEL_Y + 60 + row * 52
                self.menu_text(17, key, C_YELLOW, (text_x, y),
                               outline_color=C_BLACK, center=False)
                self.menu_text(15, description, C_WHITE, (text_x, y + 22),
                               outline_color=C_BLACK, center=False)

            self.menu_text(13, 'Pressione ESC para voltar', C_YELLOW,
                           (WIN_WIDTH / 2, WIN_HEIGHT - 14),
                           outline_color=C_BLACK, center=True)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return

    def show_about(self):
        panel_w, panel_h = 420, 240
        panel_x = (WIN_WIDTH - panel_w) // 2
        panel_y = (WIN_HEIGHT - panel_h) // 2
        mid_x   = panel_x + panel_w // 2

        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))

        icon_size = 140
        icon_surf = pygame.transform.smoothscale(
            pygame.image.load('./asset/Icone.png').convert_alpha(),
            (icon_size, icon_size),
        )
        icon_x = mid_x + (panel_w // 2 - icon_size) // 2
        icon_y = panel_y + 42 + ((panel_h - 42) - icon_size) // 2

        lines = [
            'Este jogo foi desenvolvido pelo aluno',
            'Ismael Hannecker Alcantara Ferreira,',
            'RU 4871671, para a atividade de',
            'Linguagem de Programação Aplicada',
            'no ano de 2026.',
            '',
            'Todas as imagens e áudios utilizados',
            'foram criados usando IAs como',
            'Dall-E, Manus, Chat-GPT, etc.',
        ]

        while True:
            self._draw_menu(menu_option=-1)
            self.window.blit(overlay, (0, 0))

            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            pygame.draw.rect(self.window, PANEL_COLOR, panel_rect, border_radius=8)
            pygame.draw.rect(self.window, PANEL_BORDER_COLOR, panel_rect, width=2, border_radius=8)

            self.menu_text(20, 'Sobre o Jogo', C_GOLD, (WIN_WIDTH / 2, panel_y + 22),
                           outline_color=C_DARK_GRAY, center=True)

            pygame.draw.line(self.window, C_DARK_GRAY,
                             (panel_x + 16, panel_y + 42),
                             (panel_x + panel_w - 16, panel_y + 42))

            pygame.draw.line(self.window, C_DARK_GRAY,
                             (mid_x, panel_y + 48),
                             (mid_x, panel_y + panel_h - 10))

            text_x = panel_x + 14
            y = panel_y + 55
            for line in lines:
                if line:
                    self.menu_text(13, line, C_WHITE, (text_x, y),
                                   outline_color=C_BLACK, center=False)
                y += 17

            self.window.blit(icon_surf, (icon_x, icon_y))

            self.menu_text(13, 'Pressione ESC para voltar', C_YELLOW,
                           (WIN_WIDTH / 2, WIN_HEIGHT - 14),
                           outline_color=C_BLACK, center=True)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return

    def show_records(self):
        panel_w, panel_h = 420, 225
        panel_x = (WIN_WIDTH - panel_w) // 2
        panel_y = (WIN_HEIGHT - panel_h) // 2

        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))

        records = Score().retrieve_top5()

        col_name  = panel_x + 20
        col_score = panel_x + 165
        col_date  = panel_x + 255

        while True:
            self._draw_menu(menu_option=-1)
            self.window.blit(overlay, (0, 0))

            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            pygame.draw.rect(self.window, PANEL_COLOR, panel_rect, border_radius=8)
            pygame.draw.rect(self.window, PANEL_BORDER_COLOR, panel_rect, width=2, border_radius=8)

            self.menu_text(20, 'Recordes', C_GOLD, (WIN_WIDTH / 2, panel_y + 22),
                           outline_color=C_DARK_GRAY, center=True)

            pygame.draw.line(self.window, C_DARK_GRAY,
                             (panel_x + 16, panel_y + 42),
                             (panel_x + panel_w - 16, panel_y + 42))

            self.menu_text(13, 'NOME', C_YELLOW, (col_name, panel_y + 52),
                           outline_color=C_BLACK, center=False)
            self.menu_text(13, 'PLACAR', C_YELLOW, (col_score, panel_y + 52),
                           outline_color=C_BLACK, center=False)
            self.menu_text(13, 'DATA', C_YELLOW, (col_date, panel_y + 52),
                           outline_color=C_BLACK, center=False)

            pygame.draw.line(self.window, C_DARK_GRAY,
                             (panel_x + 16, panel_y + 68),
                             (panel_x + panel_w - 16, panel_y + 68))

            if records:
                for i, (name, score, date) in enumerate(records):
                    y = panel_y + 78 + i * 26
                    self.menu_text(13, str(name),          C_WHITE, (col_name,  y), outline_color=C_BLACK, center=False)
                    self.menu_text(13, f'{score:>6}',      C_WHITE, (col_score, y), outline_color=C_BLACK, center=False)
                    self.menu_text(13, str(date),          C_WHITE, (col_date,  y), outline_color=C_BLACK, center=False)
            else:
                self.menu_text(14, 'Nenhum recorde registrado ainda.', C_WHITE,
                               (WIN_WIDTH / 2, panel_y + 130), outline_color=C_BLACK, center=True)

            self.menu_text(13, 'Pressione ESC para voltar', C_YELLOW,
                           (WIN_WIDTH / 2, WIN_HEIGHT - 14),
                           outline_color=C_BLACK, center=True)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return

    def menu_text(self, text_size: int, text: str, text_color: tuple, text_pos: tuple,
                  outline_color: tuple = C_BLACK, center: bool = True):
        text_font: Font = pygame.font.SysFont(name='helvetica', size=text_size)

        outline_surf: Surface = text_font.render(text, True, outline_color).convert_alpha()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if center:
                    outline_rect = outline_surf.get_rect(center=(text_pos[0] + dx, text_pos[1] + dy))
                else:
                    outline_rect = outline_surf.get_rect(left=text_pos[0] + dx, top=text_pos[1] + dy)
                self.window.blit(source=outline_surf, dest=outline_rect)

        text_surf: Surface = text_font.render(text, True, text_color).convert_alpha()
        if center:
            text_rect: Rect = text_surf.get_rect(center=text_pos)
        else:
            text_rect: Rect = text_surf.get_rect(left=text_pos[0], top=text_pos[1])
        self.window.blit(source=text_surf, dest=text_rect)
