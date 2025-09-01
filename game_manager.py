import sys
import json
import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, 
                             QComboBox, QLabel, QMessageBox, QDialog, QDialogButtonBox,
                             QHeaderView, QAction, QMenu, QToolBar, QStyle, QAbstractItemView)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QColor, QFont, QIcon, QDoubleValidator

class Game:
    def __init__(self, id, name, price, status, deleted=False):
        self.id = id
        self.name = name
        self.price = price
        self.status = status
        self.deleted = deleted
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'status': self.status,
            'deleted': self.deleted
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data['id'],
            data['name'],
            data['price'],
            data['status'],
            data.get('deleted', False)
        )

class GameManager:
    def __init__(self):
        self.games = []
        self.deleted_games = []
        self.next_id = 1
        self.load_data()

    def add_game(self, name, price, status):
        formatted_price = self.format_price(price)
        
        self.games.insert(0, Game(self.next_id, name, formatted_price, status))
        self.next_id += 1
        self.save_data()
    
    def update_game(self, id, name, price, status):
        for i, game in enumerate(self.games):
            if game.id == id:
                formatted_price = self.format_price(price)
                
                game.name = name
                game.price = formatted_price
                game.status = status
                self.games.insert(0, self.games.pop(i))
                break
        self.save_data()
    
    def delete_games(self, ids, permanent=False):
        if permanent:
            self.deleted_games = [game for game in self.deleted_games if game.id not in ids]
        else:
            for id in ids:
                for i, game in enumerate(self.games):
                    if game.id == id:
                        game.deleted = True
                        self.deleted_games.append(self.games.pop(i))
                        break
        self.save_data()
    
    def restore_games(self, ids):
        for id in ids:
            for i, game in enumerate(self.deleted_games):
                if game.id == id:
                    game.deleted = False
                    self.games.insert(0, self.deleted_games.pop(i))
                    break
        self.save_data()
    
    def clear_trash(self):
        self.deleted_games.clear()
        self.save_data()