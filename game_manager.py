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