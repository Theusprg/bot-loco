import sys
import os
import threading
import time
from random import uniform, choice
from PyQt5.QtGui import QIcon, QMouseEvent, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_chrome_profile_path():
    user_folder = os.path.expanduser("~")
    base_path = fr"{user_folder}\AppData\Local\Google\Chrome\User Data"
    return base_path if os.path.exists(base_path) else None


profile_path = get_chrome_profile_path()
if not profile_path:
    print("Perfil do navegador não encontrado!")
    exit()


import sys
import os
import threading
import time
from random import uniform, choice
from PyQt5.QtGui import QIcon, QMouseEvent, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def resource_path(relative_path):
    """Retorna o caminho absoluto, funcionando no PyInstaller e no script normal."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_chrome_profile_path():
    user_folder = os.path.expanduser("~")
    base_path = fr"{user_folder}\AppData\Local\Google\Chrome\User Data"
    return base_path if os.path.exists(base_path) else None


profile_path = get_chrome_profile_path()
if not profile_path:
    print("Perfil do navegador não encontrado!")
    exit()


class BotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path("icone.ico")))

        self.init_ui()

        self.frases = []
        self.driver = None
        self.running = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("BOT-LOCO 🤖")
        self.setFixedSize(400, 300)

        # Fundo da imagem
        background_path = resource_path("icone.ico")

        if os.path.exists(background_path):
            self.setAutoFillBackground(True)
            palette = QPalette()
            pixmap = QPixmap(background_path).scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            palette.setBrush(QPalette.Window, QBrush(pixmap))
            self.setPalette(palette)

        # Layout principal
        layout = QVBoxLayout()

        # Cabeçalho azul escuro
        cabecalho = QLabel("Configure os campos para iniciar o bot:")
        cabecalho.setFont(QFont("Segoe UI", 11))
        cabecalho.setStyleSheet("background-color: #0a1a3d; color: white; padding: 8px;")
        layout.addWidget(cabecalho)

        # Campos
        self.link_entry = QLineEdit()
        self.link_entry.setPlaceholderText("Link do Loco")
        self.link_entry.setText("https://loco.com/streamers/tealz?lang=pt-br")  # Alterado o link

        self.min_time_entry = QLineEdit()
        self.min_time_entry.setPlaceholderText("Tempo mínimo (segundos)")
        self.min_time_entry.setText("60")

        self.max_time_entry = QLineEdit()
        self.max_time_entry.setPlaceholderText("Tempo máximo (segundos)")
        self.max_time_entry.setText("90")

        layout.addWidget(self.link_entry)
        layout.addWidget(self.min_time_entry)
        layout.addWidget(self.max_time_entry)

        # Botões
        button_layout = QHBoxLayout()
        self.carregar_btn = QPushButton("Carregar TXT")
        self.carregar_btn.clicked.connect(self.carregar_txt)

        self.iniciar_btn = QPushButton("Iniciar Bot")
        self.iniciar_btn.clicked.connect(self.iniciar_bot)

        self.parar_btn = QPushButton("Parar Bot")
        self.parar_btn.clicked.connect(self.parar_bot)

        for btn in [self.carregar_btn, self.iniciar_btn, self.parar_btn]:
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # Status
        self.status_label = QLabel("Status: Parado")
        layout.addWidget(self.status_label)

        # Estilo geral
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 14px;
                color: #e0e0f0;
            }
            QLineEdit {
                background-color: #2d2d3d;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
                color: #e0e0f0;
            }
            QPushButton {
                background-color: #5e9eff;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #3b7dd8;
            }
        """)

    def carregar_txt(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo de Texto", "", "Arquivos de Texto (*.txt)")
        if caminho:
            try:
                with open(caminho, 'r', encoding='utf-8') as f:
                    self.frases = [linha.strip() for linha in f if linha.strip()]
                QMessageBox.information(self, "Sucesso", f"{len(self.frases)} frases carregadas!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar o arquivo: {e}")

    def iniciar_bot(self):
        if not self.frases:
            QMessageBox.warning(self, "Erro", "Nenhuma frase carregada.")
            return
        if not self.link_entry.text().strip():
            QMessageBox.warning(self, "Erro", "Informe um link válido.")
            return
        try:
            self.min_time = float(self.min_time_entry.text())
            self.max_time = float(self.max_time_entry.text())
        except ValueError:
            QMessageBox.warning(self, "Erro", "Informe tempos válidos.")
            return

        self.running = True
        self.status_label.setText("Status: Inicializando navegador...")
        threading.Thread(target=self.executar_bot, daemon=True).start()

    def parar_bot(self):
        self.running = False
        self.status_label.setText("Status: Parado")
        if self.driver:
            self.driver.quit()

    def executar_bot(self):
        self.status_label.setText("Status: Inicializando navegador...")
        options = Options()
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--profile-directory=Default")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.maximize_window()

        self.driver.get(self.link_entry.text().strip())
        self.status_label.setText("Status: Aguardando carregamento...")
        time.sleep(5)

        self.status_label.setText("Status: Enviando mensagens...")

        while self.running:
            try:
                frase = choice(self.frases)
                tempo = uniform(self.min_time, self.max_time)

                caixa_texto = self.driver.find_element(By.XPATH, "//input[@class='css-1epp86n e5o5bse0']")
                caixa_texto.clear()
                caixa_texto.send_keys(frase)
                time.sleep(0.5)

                botao = self.driver.find_element(By.XPATH, "//button[@class='css-mqythl']")
                botao.click()

                time.sleep(tempo)
            except Exception as e:
                print(f"Erro: {e}")
                time.sleep(2)

        self.driver.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icone.ico"))
    window = BotApp()
    window.show()
    sys.exit(app.exec_())


    def iniciar_bot(self):
        if not self.frases:
            QMessageBox.warning(self, "Erro", "Nenhuma frase carregada.")
            return
        if not self.link_entry.text().strip():
            QMessageBox.warning(self, "Erro", "Informe um link válido.")
            return
        try:
            self.min_time = float(self.min_time_entry.text())
            self.max_time = float(self.max_time_entry.text())
        except ValueError:
            QMessageBox.warning(self, "Erro", "Informe tempos válidos.")
            return

        self.running = True
        self.status_label.setText("Status: Inicializando navegador...")
        threading.Thread(target=self.executar_bot, daemon=True).start()

    def parar_bot(self):
        self.running = False
        self.status_label.setText("Status: Parado")
        if self.driver:
            self.driver.quit()

    def executar_bot(self):
        self.status_label.setText("Status: Inicializando navegador...")
        options = Options()
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--profile-directory=Default")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.maximize_window()

        self.driver.get(self.link_entry.text().strip())
        self.status_label.setText("Status: Aguardando carregamento...")
        time.sleep(5)

        self.status_label.setText("Status: Enviando mensagens...")

        while self.running:
            try:
                frase = choice(self.frases)
                tempo = uniform(self.min_time, self.max_time)

                caixa_texto = self.driver.find_element(By.XPATH, "//input[@class='css-1epp86n e5o5bse0']")
                caixa_texto.clear()
                caixa_texto.send_keys(frase)
                time.sleep(0.5)

                botao = self.driver.find_element(By.XPATH, "//button[@class='css-mqythl']")
                botao.click()

                time.sleep(tempo)
            except Exception as e:
                print(f"Erro: {e}")
                time.sleep(2)

        self.driver.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icone.ico"))
    window = BotApp()
    window.show()
    sys.exit(app.exec_())
