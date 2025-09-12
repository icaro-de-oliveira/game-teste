import sys
import json
import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, 
                             QComboBox, QLabel, QMessageBox, QDialog, QDialogButtonBox,
                             QHeaderView, QAction, QMenu, QToolBar, QStyle, QAbstractItemView)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QColor, QFont, QIcon, QDoubleValidator, QIntValidator

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
        self.funds = 0.0
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
                self.funds = 0.0
                with open('games.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    self.games = [Game.from_dict(game) for game in data.get('games', []) if not game.get('deleted', False)]
                    self.deleted_games = [Game.from_dict(game) for game in data.get('games', []) if game.get('deleted', False)]
                    
                    all_games = self.games + self.deleted_games
                    if all_games:
                        self.next_id = max(game.id for game in all_games) + 1
                        self.funds = data.get('funds', 0.0)
                    else:
                        self.next_id = 1
                        self.funds = data.get('funds', 0.0)
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self.games = []
            self.deleted_games = []
            self.next_id = 1
            self.funds = data.get('funds', 0.0)
    
    def save_data(self):
        try:
            all_games = [game.to_dict() for game in self.games + self.deleted_games]
            data = {
                'games': all_games,
                'next_id': self.next_id,
                'funds': self.funds
            }
            
            with open('games.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")


    def add_funds(self, amount):
        try:
            self.funds += float(amount)
            self.save_data()
        except ValueError:
            pass

    def spend_funds(self, amount):
        try:
            value = float(str(amount).replace('R$', '').replace('.', '').replace(',', '.'))
            if self.funds >= value:
                self.funds -= value
                self.save_data()
                return True
            return False
        except Exception:
            return False

    def refund_funds(self, amount):
        try:
            value = float(str(amount).replace('R$', '').replace('.', '').replace(',', '.'))
            self.funds += value
            self.save_data()
        except Exception:
            pass


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


class AddFundsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Fundos")
        self.setModal(True)
        self.setFixedSize(250, 120)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Valor a adicionar:"))

        self.amount_edit = QLineEdit()
        self.amount_edit.setValidator(QDoubleValidator(0, 999999, 2, self))
        layout.addWidget(self.amount_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_amount(self):
        text = self.amount_edit.text().strip()
        if not text:
            return ''
        # Corrige vírgula
        if text.count(',') > 1 or text.count('.') > 1:
            QMessageBox.warning(self, "Erro", "Digite um valor numérico válido!")
            return ''
        text = text.replace(',', '.')
        try:
            float(text)
            return text
        except ValueError:
            QMessageBox.warning(self, "Erro", "Digite um valor numérico válido!")
            return ''



class RemoveFundsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Remover Fundos")
        self.setModal(True)
        self.setFixedSize(250, 120)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Valor a remover:"))

        self.amount_edit = QLineEdit()
        self.amount_edit.setValidator(QDoubleValidator(0, 999999, 2, self))
        layout.addWidget(self.amount_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_amount(self):
        text = self.amount_edit.text().strip()
        if not text:
            return ''
        # Corrige vírgula
        if text.count(',') > 1 or text.count('.') > 1:
            QMessageBox.warning(self, "Erro", "Digite um valor numérico válido!")
            return ''
        text = text.replace(',', '.')
        try:
            float(text)
            return text
        except ValueError:
            QMessageBox.warning(self, "Erro", "Digite um valor numérico válido!")
            return ''

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
        # Se status for alterado, bloquear edição do preço
        self.status_combo.currentTextChanged.connect(lambda: self.price_edit.setDisabled(True))

        funds_label = QLabel(f"Saldo disponível: R$ {MainWindow.get_instance().game_manager.funds:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        layout.addWidget(funds_label)

        try:
            price_val = float(price.replace(',', '.'))
        except:
            price_val = 0.0
        if MainWindow.get_instance().game_manager.funds < price_val:
            idx = self.status_combo.findText("pago")
            if idx != -1:
                self.status_combo.model().item(idx).setEnabled(False)

        status_layout.addWidget(self.status_combo)
        layout.addLayout(status_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        return self.name_edit.text(), self.price_edit.text(), self.status_combo.currentText()
    
class MainWindow(QMainWindow):
    _instance = None
    
    def __init__(self):
        super().__init__()
        MainWindow._instance = self
        self.game_manager = GameManager()
        self.init_ui()
        self.update_table()
    
    @classmethod
    def get_instance(cls):
        return cls._instance
    
    def init_ui(self):
        self.setWindowTitle("Gerenciador de Jogos")
        self.setGeometry(100, 100, 900, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Pesquisar:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.update_table)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Preço", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 150)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_game)
        layout.addWidget(self.table)
        
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Adicionar Jogo")
        self.add_button.clicked.connect(self.add_game)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Editar Jogo")
        self.edit_button.clicked.connect(self.edit_game)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Excluir Jogo(s)")
        self.delete_button.clicked.connect(self.delete_games)
        button_layout.addWidget(self.delete_button)
        
        self.trash_button = QPushButton("Lixeira")
        self.trash_button.clicked.connect(self.show_trash)
        button_layout.addWidget(self.trash_button)
        
        layout.addLayout(button_layout)

        bottom_layout = QHBoxLayout()
        self.funds_label = QLabel()
        self.update_funds_label()
        bottom_layout.addWidget(self.funds_label)

        self.funds_button = QPushButton("Adicionar Fundos")
        self.remove_funds_button = QPushButton("Remover Fundos")
        self.remove_funds_button.clicked.connect(self.remove_funds)
        self.funds_button.clicked.connect(self.add_funds)
        bottom_layout.addWidget(self.funds_button)
        bottom_layout.addWidget(self.remove_funds_button)

        layout.addLayout(bottom_layout)
        
        self.create_menu()
    
    def create_menu(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("Arquivo")
        
        add_action = QAction("Adicionar Jogo", self)
        add_action.triggered.connect(self.add_game)
        file_menu.addAction(add_action)
        
        trash_action = QAction("Lixeira", self)
        trash_action.triggered.connect(self.show_trash)
        file_menu.addAction(trash_action)
        
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def update_table(self, search_text=""):
        self.table.setRowCount(0)
        for game in self.game_manager.games:
            if (search_text.lower() in game.name.lower() or 
                search_text in str(game.id) or 
                search_text in game.price):
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                id_item = QTableWidgetItem(str(game.id))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 0, id_item)                
                self.table.setItem(row, 1, QTableWidgetItem(game.name))                
                price_item = QTableWidgetItem(game.price)
                price_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 2, price_item)
                
                status_item = QTableWidgetItem(game.status)
                if game.status == "pago":
                    status_item.setBackground(QColor(144, 238, 144))
                elif game.status == "não pago":
                    status_item.setBackground(QColor(255, 182, 193))
                elif game.status == "reembolsado":
                    status_item.setBackground(QColor(255, 215, 0))
                
                status_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 3, status_item)
    
    def add_game(self):
        dialog = EditDialog(self)
        if dialog.exec_():
            name, price, status = dialog.get_data()
            if name and price:
                if status == 'pago' and not self.game_manager.spend_funds(price):
                    QMessageBox.warning(self, 'Aviso', 'Fundos insuficientes!')
                    return
            self.game_manager.add_game(name, price, status)
            self.update_funds_label()
            self.update_table(self.search_edit.text())
        else:
            QMessageBox.warning(self, "Aviso", "Nome e preço são obrigatórios!")
    
    def edit_game(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecione um jogo para editar!")
            return
        
        row = self.table.row(selected[0])
        id = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        price = self.table.item(row, 2).text().replace('R$ ', '')
        status = self.table.item(row, 3).text()
        
        dialog = EditDialog(self, name, price, status)
        if dialog.exec_():
            new_name, new_price, new_status = dialog.get_data()
            if new_name and new_price:
                reply = QMessageBox.question(self, "Confirmar", "Deseja realmente salvar as alterações?",
                                           QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    old_status = status
                    if old_status != new_status:
                        if new_status == "pago" and old_status != "pago":
                            if not self.game_manager.spend_funds(new_price):
                                QMessageBox.warning(self, "Aviso", "Fundos insuficientes!")
                                return
                        elif new_status == "reembolsado" and old_status == "pago":
                            self.game_manager.refund_funds(new_price)
                    self.game_manager.update_game(id, new_name, new_price, new_status)
                    self.update_funds_label()
                    self.update_table(self.search_edit.text())
            else:
                QMessageBox.warning(self, "Aviso", "Nome e preço são obrigatórios!")
    
    def delete_games(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um jogo para excluir!")
            return
        
        rows = set()
        for item in selected:
            rows.add(item.row())
        
        ids = []
        for row in rows:
            id_item = self.table.item(row, 0)
            if id_item:
                ids.append(int(id_item.text()))
        
        reply = QMessageBox.question(self, "Confirmar", 
                                   f"Deseja realmente excluir {len(rows)} jogo(s)?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.game_manager.delete_games(ids)
            self.update_table(self.search_edit.text())
    
    
    def update_funds_label(self):
        self.funds_label.setText(f"Saldo: R$ {self.game_manager.funds:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

    def add_funds(self):
        dialog = AddFundsDialog(self)
        if dialog.exec_():
            amount = dialog.get_amount()
            if amount:
                self.game_manager.add_funds(amount)
                self.update_funds_label()

    
    def remove_funds(self):
        dialog = RemoveFundsDialog(self)
        if dialog.exec_():
            amount = dialog.get_amount()
            if amount:
                try:
                    value = float(str(amount).replace(',', '.'))
                    if value <= 0:
                        QMessageBox.warning(self, "Aviso", "Digite um valor válido!")
                        return
                    if value > self.game_manager.funds:
                        QMessageBox.warning(self, "Aviso", "Você não possui fundos suficientes!")
                        return
                    self.game_manager.funds -= value
                    self.game_manager.save_data()
                    self.update_funds_label()
                except ValueError:
                    QMessageBox.warning(self, "Erro", "Digite um valor numérico válido!")

    def show_trash(self):
        dialog = TrashDialog(self.game_manager, self)
        dialog.exec_()
        self.update_table(self.search_edit.text())

class TrashDialog(QDialog):
    def __init__(self, game_manager, parent=None):
        super().__init__(parent)
        self.game_manager = game_manager
        self.setWindowTitle("Lixeira")
        self.setModal(True)
        self.setFixedSize(700, 400)
        
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Preço", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)
        
        button_layout = QHBoxLayout()
        
        self.restore_button = QPushButton("Restaurar")
        self.restore_button.clicked.connect(self.restore_games)
        button_layout.addWidget(self.restore_button)
        
        self.delete_button = QPushButton("Excluir Permanentemente")
        self.delete_button.clicked.connect(self.delete_permanent)
        button_layout.addWidget(self.delete_button)
        
        self.clear_button = QPushButton("Limpar Tudo")
        self.clear_button.clicked.connect(self.clear_trash)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)

        bottom_layout = QHBoxLayout()
        self.funds_label = QLabel()
        self.update_funds_label()
        bottom_layout.addWidget(self.funds_label)

        self.funds_button = QPushButton("Adicionar Fundos")
        self.remove_funds_button = QPushButton("Remover Fundos")
        self.remove_funds_button.clicked.connect(self.remove_funds)
        self.funds_button.clicked.connect(self.add_funds)
        bottom_layout.addWidget(self.funds_button)
        bottom_layout.addWidget(self.remove_funds_button)

        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        self.update_table()
    
    def update_table(self):
        self.table.setRowCount(0)
        for game in self.game_manager.deleted_games:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            id_item = QTableWidgetItem(str(game.id))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, id_item)            
            self.table.setItem(row, 1, QTableWidgetItem(game.name))            
            price_item = QTableWidgetItem(game.price)
            price_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, price_item)
            
            status_item = QTableWidgetItem(game.status)
            if game.status == "pago":
                status_item.setBackground(QColor(144, 238, 144))
            elif game.status == "não pago":
                status_item.setBackground(QColor(255, 182, 193))
            elif game.status == "reembolsado":
                status_item.setBackground(QColor(255, 215, 0))
            
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, status_item)
    
    def restore_games(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um jogo para restaurar!")
            return
        
        rows = set()
        for item in selected:
            rows.add(item.row())
        
        ids = []
        for row in rows:
            id_item = self.table.item(row, 0)
            if id_item:
                ids.append(int(id_item.text()))
        
        self.game_manager.restore_games(ids)
        self.update_table()
    
    def delete_permanent(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um jogo para excluir permanentemente!")
            return
        
        rows = set()
        for item in selected:
            rows.add(item.row())
        
        ids = []
        for row in rows:
            id_item = self.table.item(row, 0)
            if id_item:
                ids.append(int(id_item.text()))
        
        reply = QMessageBox.question(self, "Confirmar", 
                                   f"Deseja realmente excluir permanentemente {len(rows)} jogo(s)?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.game_manager.delete_games(ids, permanent=True)
            self.update_table()
    
    def clear_trash(self):
        if not self.game_manager.deleted_games:
            QMessageBox.information(self, "Info", "A lixeira já está vazia!")
            return
        
        reply = QMessageBox.question(self, "Confirmar", 
                                   "Deseja realmente limpar toda a lixeira?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.game_manager.clear_trash()
            self.update_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())