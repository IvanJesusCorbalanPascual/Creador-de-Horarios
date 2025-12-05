import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QMessageBox
from PyQt5 import uic
from src.logica.profesor_manager import ProfesorManager # Importa la logica
from src.modelos.modelos import Profesor # Importa el modelo
from src.bd.bd_manager import bd
from src.logica.modulo_manager import ModuloManager

# Asumiendo que la configuracion de la DB esta en un dict
# Reemplazar con tus credenciales reales de Supabase/PostgreSQL
DB_CONFIG = {
    'host': 'tu_host_db',
    'database': 'tu_db_name',
    'user': 'tu_user',
    'password': 'tu_password'
}

# --- Ventana para Agregar/Editar Profesor ---
class DialogoProfesor(QDialog):
    """Ventana de dialogo para el CRUD de Profesores"""
    def __init__(self, parent=None, profesor=None):
        super().__init__(parent)
        # Cargamos la vista del formulario
        uic.loadUi(os.path.join("src", "ui", "profesor_form.ui"), self) 
        self.profesor_manager = ProfesorManager(DB_CONFIG)
        self.profesor = profesor # Profesor a editar, o None si es nuevo
        self.setWindowTitle("Editar Profesor" if profesor else "Agregar Profesor")
        
        # Inicializar campos si estamos editando
        if self.profesor:
            self.le_nombre.setText(profesor.nombre)
            self.sb_horas_max_dia.setValue(profesor.horas_max_dia)
            self.sb_horas_max_semana.setValue(profesor.horas_max_semana)

        # Conectar botones (Aceptar y Cancelar)
        self.buttonBox.accepted.connect(self.aceptar)
        self.buttonBox.rejected.connect(self.reject)

    def aceptar(self):
        """Valida y guarda el profesor"""
        # Recoger datos del formulario
        nombre = self.le_nombre.text().strip()
        h_dia = self.sb_horas_max_dia.value()
        h_sem = self.sb_horas_max_semana.value()

        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacio")
            return

        # Crear o actualizar el objeto Profesor
        if self.profesor:
            # Edicion
            self.profesor.nombre = nombre
            self.profesor.horas_max_dia = h_dia
            self.profesor.horas_max_semana = h_sem
            exito = self.profesor_manager.update_profesor(self.profesor)
        else:
            # Nuevo
            # Constructor: Profesor(id, nombre, horas_max_dia, horas_max_semana)
            nuevo_profe = Profesor(None, nombre, h_dia, h_sem)
            exito = self.profesor_manager.add_profesor(nuevo_profe)
        
        if exito:
            self.accept() # Cierra el dialogo con exito
        else:
            QMessageBox.critical(self, "Error de DB", "Fallo al guardar en la base de datos")

# --- Ventana Principal ---
class MiAplicacion(QMainWindow):
    def __init__(self):
        super().__init__()

        self.bd = bd

        self.modulo_manager = ModuloManager(self.bd)
        
        # Cargando la vista de horarios
        uic.loadUi("src/ui/horarios.ui", self)
        self.profesor_manager = ProfesorManager(DB_CONFIG) # FIX: Initialize manager
        self.configuracion_menu()
        self.cargar_ciclo()
        self.cambiar_pagina(0) # Pagina por defecto al abrir la apliacion

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

    def cargar_ciclo(self):
        lista_ciclos = self.bd.obtener_ciclos()

        self.combo_ciclos.clear()
        if lista_ciclos:
            for ciclo in lista_ciclos:
                self.combo_ciclos.addItem(ciclo['nombre'])

        try:
            self.combo_ciclos.currentTextChanged.disconnect()
        except:
            pass
        self.combo_ciclos.currentTextChanged.connect(self.cambiar_ciclo)

    # Metodos para cargar las vistas
    def cargar_profesores(self):
        print("cargando profesores...")
        # sql = "SELECT id, nombre, color_hex, horas_max_semana FROM profesores" # Unused

        profesores = self.profesor_manager.get_all_profesores() # FIX: Get professors from manager

        self.tabla_profesores.setRowCount(0) # Limpiar tabla
        self.tabla_profesores.setRowCount(len(profesores)) # Establecer el numero de filas

        for fila, profe in enumerate(profesores):
            # Columna 0: ID (oculta)
            self.tabla_profesores.setItem(fila, 0, QTableWidgetItem(str(profe.id))) 

            # Columna 1: Nombre 
            self.tabla_profesores.setItem(fila, 1, QTableWidgetItem(profe.nombre))
            
            # Columna 2: Horas Max Dia 
            self.tabla_profesores.setItem(fila, 2, QTableWidgetItem(str(profe.horas_max_dia)))

            # Columna 3: Horas Max Semana 
            self.tabla_profesores.setItem(fila, 3, QTableWidgetItem(str(profe.horas_max_semana)))
            
            # Ajustar columnas al contenido (opcional)
            self.tabla_profesores.resizeColumnsToContents()

    def agregar_profesor(self):
        """Abre el dialogo para agregar un profesor"""
        dialogo = DialogoProfesor(self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_profesores() # Recargar la tabla tras el exito

    def editar_profesor(self):
        """Abre el dialogo para editar el profesor seleccionado"""
        seleccion = self.tabla_profesores.currentRow()
        if seleccion >= 0:
            # Obtener el ID de la primera columna oculta
            profesor_id = int(self.tabla_profesores.item(seleccion, 0).text())
            # Buscar el objeto profesor por ID en la lista cargada
            
            profesores = self.profesor_manager.get_all_profesores()
            profesor_a_editar = next((p for p in profesores if p.id == profesor_id), None)
            
            if profesor_a_editar:
                dialogo = DialogoProfesor(self, profesor_a_editar)
                if dialogo.exec_() == QDialog.Accepted:
                    self.cargar_profesores() # Recargar la tabla
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona un profesor para editar")

    def borrar_profesor(self):
        """Borra el profesor seleccionado"""
        seleccion = self.tabla_profesores.currentRow()
        if seleccion >= 0:
            profesor_id = int(self.tabla_profesores.item(seleccion, 0).text())
            nombre = self.tabla_profesores.item(seleccion, 1).text()
            
            respuesta = QMessageBox.question(self, "Confirmar Borrado", 
                                             f"¿Seguro que quieres borrar a '{nombre}'",
                                             QMessageBox.Yes | QMessageBox.No)
            
            if respuesta == QMessageBox.Yes:
                if self.profesor_manager.delete_profesor(profesor_id):
                    self.cargar_profesores() # Recargar la tabla
                else:
                    QMessageBox.critical(self, "Error de DB", "Fallo al borrar el profesor")
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona un profesor para borrar")

    def cambiar_ciclo(self): # Funcion anadida segun tu peticion
        ciclo_actual = self.combo_ciclos.currentText()
        print(f"Ciclo cambiado a {ciclo_actual}")
        indice_actual = self.stackedWidget.currentIndex()
        self.cambiar_pagina(indice_actual) # Carga la misma página en la que estaba el ususario
 
    def cargar_modulos(self): # Funcion anadida segun tu peticion
        print("cargando modulos...")
 
    def cargar_horario(self): # Funcion anadida segun tu peticion
        print("cargando horarios...")
        
    def cargar_modulos(self):
        print("cargando modulos...")

    def cargar_horario(self):
        print("cargando horarios...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiAplicacion()
    window.show()
    app.exec_()