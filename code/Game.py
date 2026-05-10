#!/usr/bin/python
# -*- coding: utf-8 -*-
import pygame

from code.Const import WIN_WIDTH, WIN_HEIGHT
from code.Level import Level
from code.Menu import Menu


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption('Caçador de Tesouros')
        pygame.display.set_icon(pygame.image.load('./asset/Icone.png'))

    def run(self):
        while True:
            menu = Menu(self.window)
            result = menu.run()
            if result == 'Jogar':
                level = Level(self.window, 'cenario1')
                level.run()
