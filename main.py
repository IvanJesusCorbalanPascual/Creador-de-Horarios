import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

class MiAplicacion(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Cargando la vista de horarios
        uic.loadUi("src/ui/horarios.ui", self) 

    def configuracion_menu(self):
        # Mapeo de Botones
        self.btn_profesores.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btn_modulos.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.btn_horarios.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        
        # Al cambiar de Ciclo, recarga la pagina
        self.combo_ciclos.currentTextChanged.connect(self.al_cambiar_ciclo)

    def cambiar_pagina(self,index):
        if index == 0:
            cargar_profesores()
        elif index == 1:
            cargar_modulos()
        elif index == 2:
            cargar_horario()

    # def cargar_cilo(self):
    

    # Metodos para cargar las vistas
    def cargar_profesores(self):
        sql = "SELECT id, nombre, color_hex, horas_max_semana FROM profesores"

        self.tabla_profesores.setRowCount(0) # Limpiar tabla
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiAplicacion()
    window.show()
    app.exec_()