import os
import sys
import ctypes
import webbrowser

from threading import Thread
from PyQt6 import QtWidgets

import design
import data
import activation

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

class POKMS(QtWidgets.QDialog, design.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
        
        if is_admin() is False:
            QtWidgets.QMessageBox.information(self, "Ошибка", "Программа должна быть запущена от имени администратора")
            sys.exit(1)
        
        try:
            self.hosts, self.keys, self.actual_version = data.get()
        except Exception:
            QtWidgets.QMessageBox.information(self, "Ошибка", "Не удалось получить данные. Проверьте подключение к интернету.")
            sys.exit(1)

        if self.actual_version["ver"] != data.ver:
            self.show_update_message(self.actual_version)

        self.productsList.addItems(self.keys.keys())
        self.productsList.clearSelection()
        self.productsList.itemClicked.connect(self.selection_changed)
        self.searchBox.textChanged.connect(self.search)

    def search(self):
        search_text = self.searchBox.text()
        for i in range(self.productsList.count()):
            item = self.productsList.item(i)
            if search_text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def show_update_message(self, version):
        text = f"Доступна новая версия: {version['ver']}. Обновить?"
        msg = QtWidgets.QMessageBox.information(
            self,
            "Обновление",
            text,
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.Yes,
        )
        if msg == QtWidgets.QMessageBox.StandardButton.Yes:
            webbrowser.open(version["url"])

    def selection_changed(self):
        self.activateButton.setEnabled(True)
        self.activateButton.clicked.connect(self.activation_button)
        self.activateButton.setText("Активировать")

    def activation_button(self):
        self.edition = self.productsList.currentItem().text()
        self.productsList.setEnabled(False)
        self.activateButton.setText("Активация...")
        self.activateButton.setEnabled(False)
        self.activateButton.clicked.disconnect()
        Thread(target=self.activation).start()

    def activation(self):
        self.activateButton.setText("Установка ключа...")
        if activation.install_key(self.keys[self.edition]) is False:
            QtWidgets.QMessageBox.information(self, "Ошибка", "Не удалось установить ключ.")
            self.activateButton.setText("Активировать")
            self.productsList.setEnabled(True)
            return
        
        for host in self.hosts:
            self.activateButton.setText(f"Подключение к KMS серверу {host}...")
            if activation.install_kms(host) is True:
                break
        
        expire = activation.check_expire()
        self.activateButton.setText(f"Готово! Активация действительна до {expire}")
        self.activateButton.setEnabled(False)
        self.productsList.setEnabled(True)



def main():
    app = QtWidgets.QApplication(sys.argv)
    window = POKMS()
    app.exec()

if __name__ == '__main__':
    main()