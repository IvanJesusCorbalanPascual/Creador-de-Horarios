import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

class MiAplicacion(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Cargando la vista de horarios
        uic.loadUi("src/ui/horarios.ui", self) 
        self.configuracion_menu()
        self.cambiar_pagina(0)

    def configuracion_menu(self):
        # Mapeo de Botones
        self.btn_profesores.clicked.connect(lambda: self.cambiar_pagina(0))
        self.btn_modulos.clicked.connect(lambda: self.cambiar_pagina(1))
        self.btn_horarios.clicked.connect(lambda: self.cambiar_pagina(2))
        
        # Al cambiar de Ciclo, recarga la pagina
        # self.combo_ciclos.currentTextChanged.connect(self.al_cambiar_ciclo)

    def cambiar_pagina(self,index):
        self.stackedWidget.setCurrentIndex(index)

        if index == 0:
            self.cargar_profesores()
        elif index == 1:
            self.cargar_modulos()
        elif index == 2:
            self.cargar_horario()

    def cambiar_ciclo(self):
        ciclo_actual = self.combo_ciclos.currentText()
        print(f"Ciclo cambiado a {ciclo_actual}")
        indice_actual = self.stackedWidget.currentIndex()
        self.cambiar_pagina(indice_actual) # Carga la misma página en la que estaba el ususario

    # def cargar_cilo(self):
    """
    sql = "SELECT nombre FROM ciclos"
        res = self.db.consultar(sql)
        
        self.combo_ciclos.clear()
        if res:
            for ciclo in res:
                self.combo_ciclos.addItem(ciclo[0]) # ciclo[0] es el nombre
    """
    
    # Metodos para cargar las vistas
    def cargar_profesores(self):
        print("cargando profesores...")
        sql = "SELECT id, nombre, color_hex, horas_max_semana FROM profesores"

        self.tabla_profesores.setRowCount(0) # Limpiar tabla
        
    def cargar_modulos(self):
        print("cargando modulos...")

    def cargar_horario(self):
        print("cargando horarios...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiAplicacion()
    window.show()
    app.exec_()