import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QMessageBox, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
from PyQt5 import uic
from src.modelos.modelos import Profesor # Importa el modelo
from src.bd.bd_manager import db
from src.logica.profesor_manager import ProfesorManager
from src.logica.modulo_manager import ModuloManager
from src.logica.ciclo_manager import CicloManager
from src.logica.generador import GeneradorAutomatico

# --- CONSTANTES ---
# Estilo visual CSS "Green Tonic"
GREEN_TONIC_STYLE = """
/* --- Estilo Base (Fondo General) --- */
QMainWindow, QDialog {
    background-color: #f0f7f4;
}

/* --- Botones Generales (Por defecto) --- */
QPushButton {
    background-color: #2e7d32;
    color: white;
    border-radius: 6px; /* Bordes un poco más redondeados */
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 600; /* Letra un poco más gruesa */
    border: 1px solid #1b5e20;
}
QPushButton:hover {
    background-color: #43a047;
    border: 1px solid #2e7d32;
}
QPushButton:pressed {
    background-color: #1b5e20;
    padding-top: 10px; /* Pequeño efecto de pulsación */
    padding-bottom: 6px;
}

/* --- Botones Superiores (Acciones Principales: Agregar/Editar) --- */
/* Usamos selectores por nombre de objeto si coinciden, o por defecto general */
QPushButton#btn_agregar_modulo, QPushButton#btn_editar_modulo, 
QPushButton#btn_agregar_profe, QPushButton#btn_editar_profe {
    color: #2e7d32; /* Texto verde */
    border: 2px solid #2e7d32; /* Borde verde más grueso */
    font-size: 14px;
}
QPushButton#btn_agregar_modulo:hover, QPushButton#btn_editar_modulo:hover,
QPushButton#btn_agregar_profe:hover, QPushButton#btn_editar_profe:hover {
    border: 5px solid #43a047;
}

/* --- ESTADO PRESSED (Opcional, para coherencia) --- */
QPushButton#btn_agregar_modulo:pressed, QPushButton#btn_editar_modulo:pressed,
QPushButton#btn_agregar_profe:pressed, QPushButton#btn_editar_profe:pressed {
    background-color: #1b5e20; /* Color oscuro al presionar */
}

/* --- Botones de Acción Peligrosa (Eliminar/Borrar) --- */
/* Tanto para el botón superior como el del menú lateral si lo hubiera */
QPushButton#btn_eliminar_modulo, QPushButton#btn_borrar_profe, QPushButton[text="Eliminar este ciclo"] {
    background-color: #ffebee; /* Fondo rojizo muy suave */
    color: #c62828; /* Texto rojo */
    border: 2px solid #c62828;
    margin: 5px;
}
QPushButton#btn_eliminar_modulo:hover, QPushButton#btn_borrar_profe:hover, QPushButton[text="Eliminar este ciclo"]:hover {
    border: 5px solid #c62828;
}

/* --- Tablas (QTableWidget) --- */
QTableWidget {
    background-color: white;
    alternate-background-color: #f1f8e9; /* Filas alternas con un verde muy sutil */
    gridline-color: #c8e6c9;
    border: 1px solid #81c784;
    border-radius: 4px;
}
QHeaderView::section {
    background-color: #2e7d32;
    color: white;
    padding: 8px;
    border: none;
    font-weight: bold;
    font-size: 14px;
}
QTableWidget::item {
    padding: 5px;
}
QTableWidget::item:selected {
    background-color: #a5d6a7; /* Color de selección suave */
    color: #1b5e20;
}

/* --- Menú Lateral (Botones de Navegación) --- */
QPushButton#btn_profesores, QPushButton#btn_modulos, QPushButton#btn_horarios {
    background-color: #263238; /* Gris azulado oscuro para el menú (contraste profesional) */
    color: #eceff1;
    text-align: left;
    padding-left: 20px;
    border: none;
    border-radius: 0px;
    font-size: 16px;
    height: 50px;
    margin: 0px;
}
QPushButton#btn_profesores:checked, QPushButton#btn_modulos:checked, QPushButton#btn_horarios:checked {
    background-color: #2e7d32; /* Se vuelve verde cuando está activo */
    color: white;
    border-left: 6px solid #aed581; /* Indicador visual a la izquierda */
    font-weight: bold;
}
QPushButton#btn_profesores:hover, QPushButton#btn_modulos:hover, QPushButton#btn_horarios:hover {
    background-color: #37474f; /* Ligero cambio al pasar el mouse en el menú */
}

/* --- Inputs y Combos --- */
QLineEdit, QComboBox, QSpinBox {
    border: 2px solid #a5d6a7; /* Borde más visible */
    border-radius: 6px;
    padding: 6px;
    background-color: white;
    font-size: 14px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 2px solid #2e7d32; /* Foco verde fuerte */
}

/* --- Títulos y Etiquetas --- */
QLabel {
    color: #263238;
    font-size: 20px;
}
QLabel#label_titulo, QLabel[text^="Modulos de"], QLabel[text^="Tabla de Profesores"], QLabel[text^="Horario de"] { 
    font-size: 22px;
    font-weight: bold;
    color: #1b5e20;
}
"""

# Reemplazando las credenciales reales de Supabase/PostgreSQL en forma de dict
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
    def __init__(self, parent=None, datos_modulo=None, ciclo_id=None, lista_profesores=[]):
        super().__init__(parent)
        # Carga el archivo UI que diseñes para módulos
        uic.loadUi(os.path.join("src", "ui", "modulo_form.ui"), self)
        
        self.datos_modulo = datos_modulo
        self.ciclo_id = ciclo_id

        self.combo_profe.clear()
        self.combo_profe.addItem("Sin Asignar", None)

        # ID del profesor que tiene el módulo actualmente (si estamos editando)
        id_actual = str(datos_modulo.get('profesor_id')) if datos_modulo and datos_modulo.get('profesor_id') else None

        index_a_seleccionar = 0

        for i, profe in enumerate(lista_profesores):
            # Lógica híbrida: Funciona si 'profe' es Objeto o Diccionario
            if isinstance(profe, dict):
                pid = profe.get('id')
                nombre = profe.get('nombre')
            else:
                pid = getattr(profe, 'id', None)
                nombre = getattr(profe, 'nombre', 'Desconocido')
            self.combo_profe.addItem(nombre, pid)

            if str(pid) == id_actual:
                index_a_seleccionar = i + 1
            if self.datos_modulo:
                self.setWindowTitle("Editar Módulo")
                self.le_nombre.setText(str(self.datos_modulo.get('nombre', '')))
                self.sb_horas_max_semana.setValue(int(self.datos_modulo.get('horas_semanales', 0)))
                self.sb_horas_max_dia.setValue(int(self.datos_modulo.get('horas_max_dia', 0)))
                
                # Seleccionar el profesor correcto
                self.combo_profe.setCurrentIndex(index_a_seleccionar)
            else:
                self.setWindowTitle("Agregar Módulo")


    def obtener_datos(self):
        profesor_id_seleccionado = self.combo_profe.currentData()
        # Devuelve un diccionario con lo que escribió el usuario
        return {
            "nombre": self.le_nombre.text().strip(),
            "horas_semanales": self.sb_horas_max_semana.value(),
            "horas_max_dia": self.sb_horas_max_dia.value(),
            "profesor_id": profesor_id_seleccionado,
            "ciclo_id": self.ciclo_id 
        }
# --- Ventana Principal ---
class MiAplicacion(QMainWindow):
    def __init__(self):
        super().__init__()

        # Inicializamos la base de datos
        self.db = db
        self.modulo_manager = ModuloManager(self.db)
        icon_path = "src/media/logoGT.png"
        self.setWindowIcon(QIcon(icon_path)) # Icono de ventana
        # Cargando la vista principal
        uic.loadUi("src/ui/horarios.ui", self) 
        self.setWindowTitle("Gestor de Ciclos")
        self.profesor_manager = ProfesorManager(DB_CONFIG)
        self.cargar_ciclos_db() # Cargar ciclos al inicio
        self.btn_generar_auto.clicked.connect(self.ejecutar_generador)
        self.ciclo_manager= CicloManager(self.db)
        self.configuracion_menu()
        self.cambiar_pagina(0) # Pagina por defecto (profesores) al abrir la apliacion

    def configuracion_menu(self):

        # Mapeo de Botones
        self.btn_profesores.clicked.connect(lambda: self.cambiar_pagina(0))
        self.btn_modulos.clicked.connect(lambda: self.cambiar_pagina(1))
        self.btn_horarios.clicked.connect(lambda: self.cambiar_pagina(2))
        self.btn_agregar_ciclo.clicked.connect(self.agregar_nuevo_ciclo)
        self.btn_eliminar_ciclo.clicked.connect(self.eliminar_ciclo_actual)
        
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

    # Funcion que marca el boton de la seccion actual
    def set_active_tab(self, index):
        self.cambiar_pagina(index)
        # Visualmente marcar el botón
        self.btn_profesores.setChecked(index == 0)
        self.btn_modulos.setChecked(index == 1)
        self.btn_horarios.setChecked(index == 2)

    def cambiar_pagina(self,index):
        self.stackedWidget.setCurrentIndex(index)

        if index == 0:
            self.cargar_profesores()
        elif index == 1:
            self.cargar_modulos()
        elif index == 2:
            self.cargar_horario()

    def agregar_nuevo_ciclo(self):
        nombre = self.le_ciclo.text()
        if nombre:
            if self.ciclo_manager.agregar_ciclo(nombre):
                self.le_ciclo.clear() # Limpia el LineEdit
                self.cargar_ciclos_db()      # Recarga la lista
                QMessageBox.information(self, "Listo", "Ciclo creado.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo crear el ciclo.")

    def eliminar_ciclo_actual(self):
        id_ciclo = self.combo_ciclos.currentData()
        
        # Si no hay ciclo seleccionado, no hacemos nada
        if not id_ciclo: return

        # Confirmación rápida
        respuesta = QMessageBox.question(
            self, "Borrar", "¿Seguro que quieres borrar este ciclo y sus datos?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            self.ciclo_manager.eliminar_ciclo(id_ciclo)
            self.cargar_ciclos_db() # Actualiza la lista
            QMessageBox.information(self, "Listo", "Ciclo eliminado.")

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
        nombre_ciclo = self.combo_ciclos.currentText()
        self.lbl_ciclo_profesor.setText(nombre_ciclo)
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
            self.tabla_profesores.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

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

        lista_profesores = self.profesor_manager.get_profesores_by_ciclo_id(ciclo_id)
        # 2. Abrimos el diálogo pasándole el ciclo_id
        dialogo = DialogoModulo(self, ciclo_id=ciclo_id, lista_profesores=lista_profesores)
        
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
        # Comprobar que la fila es correcta
        fila = self.tabla_modulos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona un módulo para editar")
            return

        # Recuperar datos de la tabla para pre-llenar el formulario
        item_id_modulo = self.tabla_modulos.item(fila, 0)
        id_modulo = item_id_modulo.data(Qt.UserRole) # ID real para la DB
        nombre = self.tabla_modulos.item(fila, 1).text()
        h_sem = self.tabla_modulos.item(fila, 2).text()
        h_dia = self.tabla_modulos.item(fila, 3).text()

        item_profe = self.tabla_modulos.item(fila, 4)
        profesor_id = item_profe.data(Qt.UserRole) # Recuperamos el id

        datos_actuales = {
            'nombre': nombre,
            'horas_semanales': h_sem,
            'horas_max_dia': h_dia,
            'profesor_id': profesor_id # Se lo pasamos al diálogo
        }

        # 4. Preparar y abrir diálogo
        ciclo_id = self.combo_ciclos.currentData()

        # Pedimos TODOS los profesores para llenar el combo
        lista_profesores = self.profesor_manager.get_profesores_by_ciclo_id(ciclo_id)

        dialogo = DialogoModulo(self, datos_modulo=datos_actuales, ciclo_id=ciclo_id, lista_profesores=lista_profesores)

        if dialogo.exec_() == QDialog.Accepted:
            nuevos_datos = dialogo.obtener_datos()
            if self.modulo_manager.editar_modulo(id_modulo, nuevos_datos):
                self.cargar_modulos() # Recargar tabla para ver cambios
                QMessageBox.information(self, "Éxito", "Módulo actualizado correctamente")
            else:
                QMessageBox.critical(self, "Error", "No se pudo actualizar")

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
            # Pasamos la tabla entera al manager, este buscará el ID y lo borrará
            if self.modulo_manager.eliminar_modulo(self.tabla_modulos):
                self.cargar_modulos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo borrar el módulo")

    def cambiar_ciclo(self):
        # Cambia el ciclo seleccionado
        ciclo_actual = self.combo_ciclos.currentText()
        print(f"Ciclo cambiado a {ciclo_actual}")
        indice_actual = self.stackedWidget.currentIndex()
        self.cambiar_pagina(indice_actual) # Carga la misma página en la que estaba el usuario
 
    def cargar_modulos(self):
        print("cargando modulos...")
        nombre_ciclo = self.combo_ciclos.currentText()
        self.lbl_ciclo_modulos.setText(nombre_ciclo)
        ciclo_actual = self.combo_ciclos.currentData()
        # llamada a la tabla_modulos en tu UI
        if hasattr(self, 'tabla_modulos'):
             self.modulo_manager.cargar_modulos_en_tabla(self.tabla_modulos, ciclo_actual)
             self.tabla_modulos.resizeColumnsToContents()
             self.tabla_modulos.horizontalHeader().setVisible(True)
             self.tabla_modulos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
             print("Error: No se encontro la tabla 'tabla_modulos' en la UI")
 
    def cargar_horario(self):
        print("Cargando horarios...")
        nombre_ciclo = self.combo_ciclos.currentText()
        self.lbl_ciclo_horario.setText(nombre_ciclo)

        # Limpia la tabla visualmente
        self.tabl_horario_grid.clearContents()

        # Obtiene los datos completos del horario
        datos = self.db.obtener_horario_completo()

        if not datos:
            return
        
        # Convierta una hora en un número de cada fila
        mapa_filas = {
            "08:00:00": 0,
            "09:00:00": 1,
            "10:00:00": 2,
            "10:30:00": 3, 
            "11:30:00": 4,
            "12:30:00": 5,
            "13:30:00": 6
        }

        for clase in datos:
            try:
                # Extrae información básica
                dia = clase['dia_semana']
                hora = clase['hora_inicio']

                # Si no hay modulo, pone un texto por defecto que evita que falle
                nombre_modulo = clase['modulos']['nombre'] if clase.get('modulos') else "No hay asignatura"

                info_profe= clase.get('profesores')   
                nombre_profe = info_profe['nombre'] if info_profe else "No hay profesor"

                # Usa el color si tiene, si no usa color blanco
                color_hex = info_profe['color_hex'] if info_profe and info_profe.get('color_hex') else "#ffffff"


                # Busca la fila correspondiente
                if hora in mapa_filas:
                    fila = mapa_filas[hora]
                else:
                    continue # Si no es igual la hora que en la tabla lo salta

                # Crea la celda
                txt_celda = f"{nombre_modulo}"
                item = QTableWidgetItem(txt_celda)
                # Sale el profesor del modulo al pasar el ratón por encima
                item.setToolTip(f"Profesor: {nombre_profe}")
                item.setTextAlignment(Qt.AlignCenter)

                # Aplica el color de fondo y texto
                item.setBackground(QColor(color_hex))
                # Letra blanca por defecto
                item.setForeground(QColor("white"))

                # Inserta todo en la tabla
                self.tabl_horario_grid.setItem(fila, dia, item)

            except Exception as e:
                print(f"Error al rellenar una celda: {e}")


    def ejecutar_generador(self):
        respuesta = QMessageBox.question(
            self, "Generar Horario", 
            "Advertencia: Estas a punto de generar un nuevo horario, esto borrara el actual. \n ¿Estás seguro?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            try:
                # Llama al generador y lo ejecuta
                generador = GeneradorAutomatico()
                generador.ejecutar()

                # Refresca la vista
                self.cargar_horario()

                QMessageBox.information(self, "Éxito", "¡Horario generado con éxito!", QMessageBox.Ok)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Se ha producido un error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GREEN_TONIC_STYLE)
    window = MiAplicacion()
    window.show()
    app.exec_()