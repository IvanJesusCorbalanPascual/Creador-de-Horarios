import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5 import uic
from src.logica.profesor_manager import ProfesorManager # Importa la logica
from src.modelos.modelos import Profesor # Importa el modelo
from src.bd.bd_manager import db
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
    # Ventana de dialogo para el CRUD de Profesores
    def __init__(self, parent=None, profesor=None, ciclo_id=None):
        super().__init__(parent)
        # Cargamos la vista del formulario
        uic.loadUi(os.path.join("src", "ui", "profesor_form.ui"), self) 
        self.profesor_manager = ProfesorManager(DB_CONFIG)
        self.profesor = profesor # Profesor a editar, o None si es nuevo
        self.ciclo_id = ciclo_id # Ciclo al que pertenece (opcional)
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
        # Valida y guarda el profesor
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
            nuevo_id = self.profesor_manager.add_profesor(nuevo_profe)
            exito = nuevo_id is not None
            
            # Si se creo exitosamente y tenemos un ciclo seleccionado, lo asignamos
            if exito and self.ciclo_id:
                self.profesor_manager.assign_profesor_to_cycle(nuevo_id, self.ciclo_id)
        
        if exito:
            self.accept() # Cierra el dialogo con exito
        else:
            QMessageBox.critical(self, "Error de DB", "Fallo al guardar en la base de datos")

class DialogoModulo(QDialog):
    # Ventana para Crear/Editar Módulos
    def __init__(self, parent=None, datos_modulo=None, ciclo_id=None):
        super().__init__(parent)
        # Carga el archivo UI que diseñes para módulos
        uic.loadUi(os.path.join("src", "ui", "modulo_form.ui"), self)
        
        self.datos_modulo = datos_modulo
        self.ciclo_id = ciclo_id
        self.setWindowTitle("Editar Módulo" if datos_modulo else "Agregar Módulo")

        # Pre-llenar datos si estamos editando
        if self.datos_modulo:
            self.le_nombre.setText(str(self.datos_modulo['nombre']))
            self.sb_horas_max_semana.setValue(int(self.datos_modulo['horas_semanales']))
            self.sb_horas_max_dia.setValue(int(self.datos_modulo['horas_max_dia']))

    def obtener_datos(self):
        # Devuelve un diccionario con lo que escribió el usuario
        return {
            "nombre": self.le_nombre.text().strip(),
            "horas_semanales": self.sb_horas_max_semana.value(),
            "horas_max_dia": self.sb_horas_max_dia.value(),
            "ciclo_id": self.ciclo_id # Importante: asignamos el módulo al ciclo actual
        }
# --- Ventana Principal ---
class MiAplicacion(QMainWindow):
    def __init__(self):
        super().__init__()

        # Inicializamos la base de datos
        self.db = db
        self.modulo_manager = ModuloManager(self.db)
        
        # Cargando la vista principal
        uic.loadUi("src/ui/horarios.ui", self) 
        self.profesor_manager = ProfesorManager(DB_CONFIG)
        self.cargar_ciclos_db() # Cargar ciclos al inicio
        self.configuracion_menu()
        self.cambiar_pagina(0) # Pagina por defecto (profesores) al abrir la apliacion

    def configuracion_menu(self):
        # Mapeo de Botones
        self.btn_profesores.clicked.connect(lambda: self.cambiar_pagina(0))
        self.btn_modulos.clicked.connect(lambda: self.cambiar_pagina(1))
        self.btn_horarios.clicked.connect(lambda: self.cambiar_pagina(2))
        
        # Conexiones de botones de Profesores
        self.btn_agregar_profe.clicked.connect(self.agregar_profesor)
        self.btn_editar_profe.clicked.connect(self.editar_profesor)
        self.btn_borrar_profe.clicked.connect(self.borrar_profesor)

        # Conexiones de botones de Profesores
        self.btn_agregar_modulo.clicked.connect(self.agregar_modulo)
        self.btn_editar_modulo.clicked.connect(self.editar_modulo)
        self.btn_eliminar_modulo.clicked.connect(self.borrar_modulo)
        
        # Al cambiar de Ciclo, recarga la pagina
        self.combo_ciclos.currentIndexChanged.connect(self.cambiar_ciclo)

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

    def cargar_ciclos_db(self):
        # Carga los ciclos desde la base de datos al ComboBox
        ciclos = db.obtener_ciclos()
        self.combo_ciclos.clear()
        if ciclos:
            for ciclo in ciclos:
                # ciclo is likely a dict {'id': 1, 'nombre': 'DAM1'}
                self.combo_ciclos.addItem(ciclo.get('nombre'), ciclo.get('id'))
        else:
             self.combo_ciclos.addItem("Sin Ciclos")
    
    # Metodos para cargar las vistas
    def cargar_profesores(self):
        print("cargando profesores...")
        
        # Obtener ID del ciclo seleccionado
        ciclo_id = self.combo_ciclos.currentData()
        
        if ciclo_id:
            print(f"Filtrando por ciclo ID: {ciclo_id}")
            profesores = self.profesor_manager.get_profesores_by_ciclo_id(ciclo_id)
        else:
            profesores = self.profesor_manager.get_all_profesores()

        self.tabla_profesores.setColumnCount(4)
        self.tabla_profesores.setHorizontalHeaderLabels(["Nombre", "Color", "Horas Dia", "Horas Sem"])
        self.tabla_profesores.setRowCount(0) # Limpiar tabla
        self.tabla_profesores.setRowCount(len(profesores)) # Establecer el numero de filas

        for fila, profe in enumerate(profesores):
            # Columna 0: Nombre (y guardamos ID en UserRole)
            item_nombre = QTableWidgetItem(profe.nombre)
            item_nombre.setData(Qt.UserRole, profe.id)
            self.tabla_profesores.setItem(fila, 0, item_nombre)
            
            # Columna 1: Color
            item_color = QTableWidgetItem()
            if profe.color_hex:
                try:
                    color = QColor(profe.color_hex)
                    item_color.setBackground(color)
                except:
                    pass # Si el color no es valido, no hacemos nada
            self.tabla_profesores.setItem(fila, 1, item_color)

            # Columna 2: Horas Max Dia 
            self.tabla_profesores.setItem(fila, 2, QTableWidgetItem(str(profe.horas_max_dia)))

            # Columna 3: Horas Max Semana 
            self.tabla_profesores.setItem(fila, 3, QTableWidgetItem(str(profe.horas_max_semana)))
            
            # Ajustar columnas al contenido (opcional)
            self.tabla_profesores.resizeColumnsToContents()

    def agregar_profesor(self):
        # Abre el dialogo para agregar un profesor
        dialogo = DialogoProfesor(self)

        """
        Abre el dialogo para agregar un profesor
        ciclo_id = self.combo_ciclos.currentData() # Obtener ID del ciclo actual
        dialogo = DialogoProfesor(self, ciclo_id=ciclo_id)
        """

        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_profesores() # Recargar la tabla tras el exito

    def editar_profesor(self):
        # Abre el dialogo para editar el profesor seleccionado
        seleccion = self.tabla_profesores.currentRow()
        if seleccion >= 0:
            # Obtener el ID de la primera columna
            profesor_id = self.tabla_profesores.item(seleccion, 0).data(Qt.UserRole)
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
        # Borra el profesor seleccionado
        seleccion = self.tabla_profesores.currentRow()
        if seleccion >= 0:
            profesor_id = self.tabla_profesores.item(seleccion, 0).data(Qt.UserRole)
            nombre = self.tabla_profesores.item(seleccion, 0).text()
            ciclo_id = self.combo_ciclos.currentData()

            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Borrar Profesor")
            msg_box.setText(f"Opciones de borrado para '{nombre}'")
            msg_box.setIcon(QMessageBox.Question)
            
            btn_ciclo = None
            if ciclo_id:
                btn_ciclo = msg_box.addButton("Eliminar del Ciclo Actual", QMessageBox.ActionRole)
            
            btn_total = msg_box.addButton("Eliminar TOTALMENTE (BD)", QMessageBox.ActionRole)
            btn_cancel = msg_box.addButton("Cancelar", QMessageBox.RejectRole)
            
            msg_box.exec_()
            
            clicked_button = msg_box.clickedButton()
            
            if clicked_button == btn_cancel:
                return

            if clicked_button == btn_ciclo and ciclo_id:
                # Eliminar solo de la relacion profesor_ciclo
                 if self.profesor_manager.delete_profesor_from_ciclo(profesor_id, ciclo_id):
                    self.cargar_profesores()
                 else:
                    QMessageBox.critical(self, "Error", "Fallo al desvincular del ciclo")
            
            elif clicked_button == btn_total:
                # Confirmacion extra para borrado total
                confirm = QMessageBox.question(self, "Confirmar Borrado Total", 
                                             f"Esto borrará a '{nombre}' de TODOS los ciclos y de la base de datos.\n¿Seguro?",
                                             QMessageBox.Yes | QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    if self.profesor_manager.delete_profesor(profesor_id):
                        self.cargar_profesores()
                    else:
                        QMessageBox.critical(self, "Error DB", "Fallo al borrar totalmente")
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona un profesor para borrar")

    def agregar_modulo(self):
        # 1. Obtenemos el ID del ciclo que se está viendo actualmente
        ciclo_id = self.combo_ciclos.currentData()
        
        if not ciclo_id:
            QMessageBox.warning(self, "Aviso", "Selecciona un ciclo válido primero.")
            return

        # 2. Abrimos el diálogo pasándole el ciclo_id
        dialogo = DialogoModulo(self, ciclo_id=ciclo_id)
        
        if dialogo.exec_() == QDialog.Accepted:
            datos = dialogo.obtener_datos()
            
            # Manejo de errores
            if not datos['nombre']:
                QMessageBox.warning(self, "Error", "Por favor, escribe el nombre del módulo")
                return

            # 3. Guardamos usando el manager
            if self.modulo_manager.agregar_modulo(datos):
                self.cargar_modulos() # Refrescar la tabla
            else:
                QMessageBox.critical(self, "Error", "No se pudo guardar el módulo.")

    def editar_modulo(self):
        # Editar el módulo seleccionado en la tabla
        # 1. Comprobar selección
        fila = self.tabla_modulos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona un módulo para editar")
            return

        # 2. Recuperar datos de la tabla para pre-llenar el formulario
        # (Es más rápido que consultar a la BD otra vez)
        id_modulo = self.tabla_modulos.item(fila, 0).text()
        nombre = self.tabla_modulos.item(fila, 1).text()
        h_sem = self.tabla_modulos.item(fila, 2).text()
        h_dia = self.tabla_modulos.item(fila, 3).text()
        
        # Empaquetamos en un dict temporal
        datos_actuales = {
            'nombre': nombre,
            'horas_semanales': h_sem,
            'horas_max_dia': h_dia
        }
        
        # Recuperamos ciclo_id por si acaso (aunque al editar no solemos cambiarlo de ciclo aquí)
        ciclo_id = self.combo_ciclos.currentData()

        # 3. Abrir diálogo
        dialogo = DialogoModulo(self, datos_modulo=datos_actuales, ciclo_id=ciclo_id)
        
        if dialogo.exec_() == QDialog.Accepted:
            nuevos_datos = dialogo.obtener_datos()
            
            # 4. Actualizar
            if self.modulo_manager.editar_modulo(id_modulo, nuevos_datos):
                self.cargar_modulos()
            else:
                QMessageBox.critical(self, "Error", "Fallo al actualizar el módulo")

    def borrar_modulo(self):
        # Elimina el módulo seleccionado
        fila = self.tabla_modulos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona un módulo para borrar")
            return
            
        nombre = self.tabla_modulos.item(fila, 1).text()
        
        confirmacion = QMessageBox.question(
            self, "Borrar Módulo", 
            f"¿Estás seguro de borrar el módulo '{nombre}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmacion == QMessageBox.Yes:
            # Pasamos la tabla entera al manager, él sabe buscar el ID y borrar
            if self.modulo_manager.eliminar_modulo(self.tabla_modulos):
                self.cargar_modulos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo borrar el módulo")

    def cambiar_ciclo(self): # Funcion anadida segun tu peticion
        ciclo_actual = self.combo_ciclos.currentText()
        print(f"Ciclo cambiado a {ciclo_actual}")
        indice_actual = self.stackedWidget.currentIndex()
        self.cambiar_pagina(indice_actual) # Carga la misma página en la que estaba el ususario
 
    def cargar_modulos(self):
        print("cargando modulos...")
        ciclo_actual = self.combo_ciclos.currentText()
        # llamada a la tabla_modulos en tu UI
        if hasattr(self, 'tabla_modulos'):
             self.modulo_manager.cargar_modulos_en_tabla(self.tabla_modulos, ciclo_actual)
        else:
             print("Error: No se encontro la tabla 'tabla_modulos' en la UI")
 
    def cargar_horario(self):
        print("cargando horarios...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiAplicacion()
    window.show()
    app.exec_()