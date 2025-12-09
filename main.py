import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QMessageBox, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5 import uic
from src.logica.profesor_manager import ProfesorManager # Importa la logica
from src.modelos.modelos import Profesor # Importa el modelo
from src.bd.bd_manager import db
from src.logica.modulo_manager import ModuloManager
from src.logica.generador import GeneradorAutomatico

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
            self.le_profesor.setText(str(self.datos_modulo['profesor_asignado']))

    def obtener_datos(self):
        # Devuelve un diccionario con lo que escribió el usuario
        return {
            "nombre": self.le_nombre.text().strip(),
            "horas_semanales": self.sb_horas_max_semana.value(),
            "horas_max_dia": self.sb_horas_max_dia.value(),
            "profesor_asignado": self.le_profesor.text().strip(),
            "ciclo_id": self.ciclo_id # Importante: asignamos el módulo al ciclo actual
        }
    
class DialogoPreferencia(QDialog):
    def __init__(self, parent=None, profesor_id=None, nombre_profe=""):
        super().__init__(parent)
        # Carga el archivo UI
        uic.loadUi(os.path.join("src", "ui", "preferencia_form.ui"), self)
        self.profesor_id = profesor_id
        self.setWindowTitle(f"Restricción para: {nombre_profe}")

        self.buttonBox.accepted.connect(self.aceptar)
        self.buttonBox.rejected.connect(self.reject)
            
    def aceptar(self):
        # El indice del combobox de los días
        dia_semana = self.cb_dia.currentIndex()

        # Convierte a String las horas
        hora_inicio = self.te_inicio.time().toString("HH:mm:ss")
        hora_fin = self.te_fin.time().toString("HH:mm:ss")

        # Mapea el combobox de tipo a la prioridad que corresponde
        tipo_index = self.cb_tipo.currentIndex()
        prioridad = 1 if tipo_index == 0 else 2

        motivo = ""
        if hasattr(self, 'le_motivo'):
            motivo = self.le_motivo.text().strip()

        # Valida que la hora de inicio no sea mayor o igual que la hora de fin
        if hora_inicio >= hora_fin:
            QMessageBox.warning(self, "Error", "La hora de inicio debe ser anterior a la de fin.")
            return
            
        # Prepara los datos para supabase
        datos = {
            "profesor_id": self.profesor_id,
            "dia_semana": dia_semana,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "nivel_prioridad": prioridad,
            "motivo": motivo
        }

        res = db.agregar_preferencia(datos)

        if res:
            QMessageBox.information(self, "Éxito", "Se ha guardado la restricción correctamente.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se ha podido guardar la restricción en la BD.")

class DialogoListaPreferencias(QDialog):
    def __init__(self, parent=None, profesor_id=None, nombre_profe=""):
        super().__init__(parent)
        uic.loadUi(os.path.join("src", "ui", "lista_preferencias.ui"), self)
        self.profesor_id = profesor_id

        # Actualiza el título con el nombre del profesor
        self.setWindowTitle(f"Gestionar: {nombre_profe}")
        # Actualiza el label dentro del groupbox con eol nombre del profesor
        if hasattr(self, 'lbl_nombre_profe'):
            self.lbl_nombre_profe.setText(f"Restricciones de: {nombre_profe}")

        # Configura la tabla
        self.tabla_restricciones.setColumnCount(5)
        self.tabla_restricciones.setHorizontalHeaderLabels(["Día", "Inicio", "Fin", "Prioridad", "Motivo"])
        self.tabla_restricciones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Selecciona una fila entera
        self.tabla_restricciones.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Conexión con los botones
        self.btn_nueva.clicked.connect(self.abrir_nueva_restriccion)
        self.btn_borrar.clicked.connect(self.borrar_restriccion_seleccionada)
        self.btn_cerrar.clicked.connect(self.reject)

        # Carga los datos iniciales
        self.cargar_datos()

    def cargar_datos(self):
        datos = db.obtener_preferencias(self.profesor_id)
        self.tabla_restricciones.setRowCount(0)

        # Almacena los dias de la semana
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

        for fila, pref in enumerate(datos):
            self.tabla_restricciones.insertRow(fila)

            # Traducción del día de número a texto
            dia_txt = dias_semana[pref['dia_semana']] if 0 <= pref['dia_semana'] < 5 else "Desconocido"
            self.tabla_restricciones.setItem(fila, 0, QTableWidgetItem(dia_txt))

            # Horas Inicio y Fin
            self.tabla_restricciones.setItem(fila, 1, QTableWidgetItem(str(pref['hora_inicio'])))
            self.tabla_restricciones.setItem(fila, 2, QTableWidgetItem(str(pref['hora_fin'])))

            # Prioridades
            prior_txt = "Obligatorio" if pref['nivel_prioridad'] == 1 else "Preferiblemente"
            self.tabla_restricciones.setItem(fila, 3, QTableWidgetItem(prior_txt))

            # Motivo
            self.tabla_restricciones.setItem(fila, 4, QTableWidgetItem(str(pref['motivo'])))

            # Guarda el ID real de cada fila 
            self.tabla_restricciones.item(fila, 0).setData(Qt.UserRole, pref['id'])

    def abrir_nueva_restriccion(self):
        # Abre la ventana para añadir restricciones
        dialogo = DialogoPreferencia(self, self.profesor_id, "Nueva Restricción")
        if dialogo.exec_() == QDialog.Accepted:
            # Recarga la lista al volver
            self.cargar_datos()

    def borrar_restriccion_seleccionada(self):
        fila = self.tabla_restricciones.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Debes seleccionar una fila para borrar")
            return
        
        # Recupera el ID real
        id_pref = self.tabla_restricciones.item(fila, 0).data(Qt.UserRole)

        confirm = QMessageBox.question(self, "ELIMINAR", "¿SEGURO que quieres eliminar esta restricción?", 
                                        QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            if db.eliminar_preferencia(id_pref):
                self.cargar_datos()
            else:
                QMessageBox.critical(self, "Error", "No ha sido posible eliminar")

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
        self.btn_generar_auto.clicked.connect(self.ejecutar_generador)
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
        self.btn_preferencias.clicked.connect(self.gestionar_preferencias)

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

    def gestionar_preferencias(self):
        # Obtiene la fila seleccionada
        fila = self.tabla_profesores.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Advertencia", "Selecciona un profesor primero")
            return
        
        # Obtiene el ID y el nombre
        item_nombre = self.tabla_profesores.item(fila, 0)
        profesor_id = item_nombre.data(Qt.UserRole)
        nombre_profe = item_nombre.text()

        dialogo = DialogoListaPreferencias(self, profesor_id, nombre_profe)
        dialogo.exec_()

    def agregar_modulo(self):
        # 1. Obtenemos el ID del ciclo que se está viendo actualmente
        ciclo_id = self.combo_ciclos.currentData()
        
        if not ciclo_id:
            QMessageBox.warning(self, "Aviso", "Selecciona un ciclo válido primero")
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
                QMessageBox.critical(self, "Error", "No se pudo guardar el módulo")

    def editar_modulo(self):
        # Editar el módulo seleccionado en la tabla
        # Comprobar que la fila es correcta
        fila = self.tabla_modulos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona un módulo para editar")
            return

        # Recuperar datos de la tabla para pre-llenar el formulario
        id_modulo = self.tabla_modulos.item(fila, 0).text()
        nombre = self.tabla_modulos.item(fila, 1).text()
        h_sem = self.tabla_modulos.item(fila, 2).text()
        h_dia = self.tabla_modulos.item(fila, 3).text()
        
        # Empaquetamos en un dict temporal
        profesor_asignado = self.tabla_modulos.item(fila, 4).text() if self.tabla_modulos.item(fila, 4) else ""
        datos_actuales = {
            'nombre': nombre,
            'horas_semanales': h_sem,
            'horas_max_dia': h_dia,
            'profesor_asignado': profesor_asignado
        }
        
        # Recuperamos ciclo_id por si acaso (aunque al editar no solemos cambiarlo de ciclo aquí)
        ciclo_id = self.combo_ciclos.currentData()

        # Abrir diálogo
        dialogo = DialogoModulo(self, datos_modulo=datos_actuales, ciclo_id=ciclo_id)
        
        if dialogo.exec_() == QDialog.Accepted:
            nuevos_datos = dialogo.obtener_datos()
            
            # Actualizar
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
        ciclo_actual = self.combo_ciclos.currentText()
        # llamada a la tabla_modulos en tu UI
        if hasattr(self, 'tabla_modulos'):
             self.modulo_manager.cargar_modulos_en_tabla(self.tabla_modulos, ciclo_actual)
             self.tabla_modulos.resizeColumnsToContents()
             self.tabla_modulos.resizeRowsToContents()
             self.tabla_modulos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
             print("Error: No se encontro la tabla 'tabla_modulos' en la UI")
 
    def cargar_horario(self):
        print("Cargando horarios...")
        
        # Comprueba que ciclo quiero ver el usuario
        ciclo_actual_id = self.combo_ciclos.currentData()
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

                # Si la clase no pertenece al ciclo seleccionado o no tiene módulo lo salta
                if not clase.get('modulos'):
                    continue

                ciclo_clase = clase['modulos'].get('ciclo_id')

                # Si el ID no coincide no lo rellena
                if ciclo_clase != ciclo_actual_id:
                    continue

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

                # Obtiene el ID de ciclo que se esta visualizando
                ciclo_actual_id = self.combo_ciclos.currentData()
                # Llama al generador y lo ejecuta
                generador = GeneradorAutomatico()
                # Al pasarle el ciclo_id solo toca ese curso
                generador.ejecutar(ciclo_id=ciclo_actual_id)

                # Refresca la vista
                self.cargar_horario()

                QMessageBox.information(self, "Éxito", "¡Horario generado con éxito!", QMessageBox.Ok)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Se ha producido un error: {str(e)}")
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiAplicacion()
    window.show()
    app.exec_()

