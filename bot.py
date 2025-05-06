import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from random import uniform, choice
import threading
import time
import os 

def get_chrome_profile_path():
    username = os.getlogin()
    base_path = fr"C:\Users\{username}\AppData\Local\Google\Chrome\User Data"
    return base_path if os.path.exists(base_path) else None

profile_path = get_chrome_profile_path()
if not profile_path:
    print("Perfil do navegador não encontrado!")
    exit()


class BotApp:
    def __init__(self, master):
        self.master = master
        master.title("Auto Mensageiro")
        master.geometry("400x300")

        self.frases = []
        self.driver = None
        self.running = False

        # Interface
        tk.Label(master, text="Link do site:").pack()
        self.link_entry = tk.Entry(master, width=50)
        self.link_entry.pack()

        tk.Label(master, text="Tempo mínimo (s):").pack()
        self.min_time_entry = tk.Entry(master)
        self.min_time_entry.pack()

        tk.Label(master, text="Tempo máximo (s):").pack()
        self.max_time_entry = tk.Entry(master)
        self.max_time_entry.pack()

        tk.Button(master, text="Carregar TXT com frases", command=self.carregar_txt).pack(pady=5)
        tk.Button(master, text="Iniciar Bot", command=self.iniciar_bot).pack(pady=5)
        tk.Button(master, text="Parar Bot", command=self.parar_bot).pack(pady=5)

        self.status = tk.Label(master, text="Status: Aguardando", fg="blue")
        self.status.pack(pady=10)

    def carregar_txt(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos de texto", "*.txt")])
        if caminho:
            with open(caminho, 'r', encoding='utf-8') as f:
                self.frases = [linha.strip() for linha in f if linha.strip()]
            messagebox.showinfo("Sucesso", f"{len(self.frases)} frases carregadas!")

    def iniciar_bot(self):
        if not self.frases:
            messagebox.showerror("Erro", "Nenhuma frase carregada.")
            return

        if not self.link_entry.get().strip():
            messagebox.showerror("Erro", "Informe um link válido.")
            return

        try:
            self.min_time = float(self.min_time_entry.get())
            self.max_time = float(self.max_time_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Informe tempos válidos (números).")
            return

        self.running = True
        threading.Thread(target=self.executar_bot, daemon=True).start()

    def parar_bot(self):
        self.running = False
        self.status.config(text="Status: Parado", fg="red")
        if self.driver:
            self.driver.quit()

    def executar_bot(self):
        self.status.config(text="Status: Inicializando navegador...", fg="green")


        options = Options()
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--profile-directory=Default")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        link = self.link_entry.get().strip()
        self.driver.get(link)
        time.sleep(5)

        self.status.config(text="Status: Enviando mensagens...", fg="green")

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
    root = tk.Tk()
    app = BotApp(root)
    root.mainloop()
