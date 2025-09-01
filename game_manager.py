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

    def format_price(self, price):
        clean_price = price.replace('R$', '').replace(' ', '').strip()
        
        if not clean_price:
            return "R$ 0,00"
        
        if not re.match(r'^[\d,.]+$', clean_price):
            clean_price = re.sub(r'[^\d,]', '', clean_price)
        
        if '.' in clean_price and ',' in clean_price:
            clean_price = clean_price.replace('.', '').replace(',', '.')
        elif ',' in clean_price:
            clean_price = clean_price.replace(',', '.')
        
        try:
            price_float = float(clean_price)
            formatted = f"R$ {price_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            return formatted
        except ValueError:
            return f"R$ {price}"
    
    def load_data(self):
        try:
            if os.path.exists('games.json'):
                with open('games.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    self.games = [Game.from_dict(game) for game in data.get('games', []) if not game.get('deleted', False)]
                    self.deleted_games = [Game.from_dict(game) for game in data.get('games', []) if game.get('deleted', False)]
                    
                    all_games = self.games + self.deleted_games
                    if all_games:
                        self.next_id = max(game.id for game in all_games) + 1
                    else:
                        self.next_id = 1
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self.games = []
            self.deleted_games = []
            self.next_id = 1
    
    def save_data(self):
        try:
            all_games = [game.to_dict() for game in self.games + self.deleted_games]
            data = {
                'games': all_games,
                'next_id': self.next_id
            }
            
            with open('games.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")

class PriceLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QDoubleValidator(0, 999999, 2, self))
        
    def focusInEvent(self, event):
        current_text = self.text().replace('R$', '').strip()
        self.setText(current_text)
        super().focusInEvent(event)
        
    def focusOutEvent(self, event):
        if self.text():
            manager = MainWindow.get_instance().game_manager if hasattr(MainWindow, 'get_instance') else GameManager()
            formatted = manager.format_price(self.text())
            self.setText(formatted)
        super().focusOutEvent(event)

class EditDialog(QDialog):
    def __init__(self, parent=None, name="", price="", status="não pago"):
        super().__init__(parent)
        self.setWindowTitle("Editar Jogo")
        self.setModal(True)
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nome:"))
        self.name_edit = QLineEdit(name)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        price_layout = QHBoxLayout()
        price_layout.addWidget(QLabel("Preço:"))
        self.price_edit = PriceLineEdit()
        self.price_edit.setText(price.replace('R$', '').strip())
        price_layout.addWidget(self.price_edit)
        layout.addLayout(price_layout)
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["pago", "não pago", "reembolsado"])
        self.status_combo.setCurrentText(status)
        status_layout.addWidget(self.status_combo)
        layout.addLayout(status_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        return self.name_edit.text(), self.price_edit.text(), self.status_combo.currentText()