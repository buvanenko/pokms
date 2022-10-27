import sys
import os
import subprocess
import ctypes
from threading import Thread
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QMessageBox,
    QListWidget,
)
from data import get, ver


def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        if is_admin() is False:
            self.show_message(
                "Ошибка", "Программа должна быть запущена от имени администратора"
            )
            sys.exit(1)

        try:
            self.hosts, self.keys, self.actual_version = get()
        except Exception:
            self.show_message(
                "Ошибка",
                "Не удалось получить данные. Проверьте подключение к интернету.",
            )
            sys.exit(1)
        if self.actual_version["ver"] != ver:
            self.show_update_message(self.actual_version)

        self.l = QListWidget()
        self.l.addItems(self.keys.keys())
        self.l.clearSelection()
        self.l.itemClicked.connect(self.selectionChanged)

        self.setWindowTitle("POKMS")
        self.setFixedSize(300, 300)
        button = QPushButton("Выберите редакцию")
        button.setCheckable(True)
        button.setEnabled(False)
        button.clicked.connect(self.activation_button)
        self.setCentralWidget(button)
        self.setMenuWidget(self.l)

        self.edition = None

    def show_message(self, title, text):
        QMessageBox.information(self, title, text)

    def show_update_message(self, version):
        text = f"Доступна новая версия: {version['ver']}. Обновить?"
        msg = QMessageBox.information(
            self,
            "Обновление",
            text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if msg == QMessageBox.StandardButton.Yes:
            subprocess.Popen(f"start {version['link']}", shell=True)
            sys.exit(0)

    def enable_button(self):
        self.centralWidget().setText("Активировать!")
        self.centralWidget().setEnabled(True)
        self.menuWidget().setEnabled(True)

    def activation_button(self):
        self.centralWidget().setText("Активация...")
        self.centralWidget().setEnabled(False)
        self.menuWidget().setEnabled(False)
        t = Thread(target=activation_thread)
        t.start()

    def selectionChanged(self, item):
        self.enable_button()
        self.edition = item.text()


app = QApplication(sys.argv)

window = MainWindow()
window.show()


def activation_thread():
    window.centralWidget().setText("Устанавливаем ключ продукта...")
    try:
        out = subprocess.check_output(
            "cscript C:\Windows\System32\slmgr.vbs -ipk " + window.keys[window.edition],
            shell=True,
        )
    except subprocess.CalledProcessError:
        window.show_message(
            "Ошибка", "Неверный ключ продукта. Выберите корректную редакцию."
        )
        window.enable_button()
        return

    for host in window.hosts:
        ex = None
        window.centralWidget().setText(
            "Попытка подключения к серверу активации: " + host + "..."
        )
        try:
            out = subprocess.check_output(
                "cscript C:\Windows\System32\slmgr.vbs  -skms " + host, shell=True
            )
            window.centralWidget().setText("Посылаем запрос к " + host + "...")
            out = subprocess.check_output(
                "cscript C:\Windows\System32\slmgr.vbs  /ato", shell=True
            )
        except subprocess.CalledProcessError as ex:
            continue
        break
    if ex is not None:
        window.show_message(
            "Ошибка",
            "Не удалось подключиться к серверу активации. Проверьте подключение к интернету.",
        )
        window.enable_button()
        return
    out = subprocess.check_output(
        "cscript C:\Windows\System32\slmgr.vbs  /xpr",
        shell=True,
        text=True,
        encoding="cp866",
    )
    window.show_message(
        "Готово",
        f"Работа активатора завершена. Система активирована до {str(out).split(' ')[-2]}.",
    )


app.exec()
