#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3


class DBProxy:
    def __init__(self, db_name: str):
        self.connection = sqlite3.connect(db_name)
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS recordes (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT    NOT NULL,
                score INTEGER NOT NULL,
                date  TEXT    NOT NULL
            )
        ''')
        self.connection.commit()

    def save(self, record: dict):
        self.connection.execute(
            'INSERT INTO recordes (name, score, date) VALUES (:name, :score, :date)',
            record,
        )
        self.connection.commit()

    def retrieve_top5(self) -> list:
        return self.connection.execute(
            'SELECT name, score, date FROM recordes ORDER BY score DESC LIMIT 5'
        ).fetchall()

    def close(self):
        self.connection.close()
