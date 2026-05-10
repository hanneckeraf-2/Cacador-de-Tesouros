#!/usr/bin/python
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class Entity(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def move(self):
        pass
