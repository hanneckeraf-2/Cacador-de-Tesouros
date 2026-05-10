#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime

from code.DBProxy import DBProxy

DB_NAME = 'cacador_recordes'


def get_formatted_date() -> str:
    now = datetime.now()
    return now.strftime('%H:%M - %d/%m/%y')


class Score:
    def save(self, name: str, score: int, level: int):
        db = DBProxy(DB_NAME)
        db.save({'name': name, 'score': score, 'level': level, 'date': get_formatted_date()})
        db.close()

    def retrieve_top5(self) -> list:
        db = DBProxy(DB_NAME)
        records = db.retrieve_top5()
        db.close()
        return records
