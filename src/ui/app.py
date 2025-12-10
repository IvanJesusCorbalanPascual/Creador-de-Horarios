import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QHeaderView, QDialog, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
from PyQt5 import uic
from src.bd.bd_manager import db
from src.logica.profesor_manager import ProfesorManager
from src.logica.modulo_manager import ModuloManager
from src.logica.ciclo_manager import CicloManager
from src.logica.exportador_manager import ExportadorManager
from src.logica.generador import GeneradorAutomatico
from src.config import DB_CONFIG
from src.ui.dialogs import DialogoProfesor, DialogoModulo, DialogoListaPreferencias

# --- Ventana Principal ---
class MiAplicacion(QMainWindow):
    def __init__(self):
        super().__init__()

        # Inicia DB
        self.db = db
        self.modulo_manager = ModuloManager(self.db)
        icon_path = "src/media/logoGT.png"
        self.setWindowIcon(QIcon(icon_path)) # Icono ventana
        # Carga UI
        uic.loadUi("src/ui/horarios.ui", self) 
        self.setWindowTitle("Gestor de Ciclos")
        self.profesor_manager = ProfesorManager(DB_CONFIG)
        self.cargar_ciclos_db() # Carga ciclos
        self.btn_generar_auto.clicked.connect(self.ejecutar_generador)
        self.ciclo_manager= CicloManager(self.db)
        self.exportador = ExportadorManager()
        self.configuracion_menu()
        self.cambiar_pagina(0) # Página inicial

    def configuracion_menu(self):

        # Configura botones
        self.btn_profesores.clicked.connect(lambda: self.cambiar_pagina(0))
        self.btn_modulos.clicked.connect(lambda: self.cambiar_pagina(1))
        self.btn_horarios.clicked.connect(lambda: self.cambiar_pagina(2))
        self.btn_agregar_ciclo.clicked.connect(self.agregar_nuevo_ciclo)
        self.btn_eliminar_ciclo.clicked.connect(self.eliminar_ciclo_actual)
        
        # Botones profesores
        self.btn_agregar_profe.clicked.connect(self.agregar_profesor)
        self.btn_editar_profe.clicked.connect(self.editar_profesor)
        self.btn_borrar_profe.clicked.connect(self.borrar_profesor)
        self.btn_preferencias.clicked.connect(self.gestionar_preferencias)

        # Botones módulos
        self.btn_agregar_modulo.clicked.connect(self.agregar_modulo)
        self.btn_editar_modulo.clicked.connect(self.editar_modulo)
        self.btn_eliminar_modulo.clicked.connect(self.borrar_modulo)
        
        # Recarga al cambiar ciclo
        self.combo_ciclos.currentIndexChanged.connect(self.cambiar_ciclo)
        
        # Boton exportar
        try:
            self.btn_exportar.clicked.connect(self.exportar_horario)
        except:
             pass

    # Marca pestaña activa
    def set_active_tab(self, index):
        self.cambiar_pagina(index)
        # Actualiza estado botones
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
        # Carga ciclos en combo
        ciclos = db.obtener_ciclos()
        self.combo_ciclos.clear()
        if ciclos:
            for ciclo in ciclos:
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
            # Nombre e ID
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
        # Abre diálogo profesor
        dialogo = DialogoProfesor(self)

        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_profesores() # Recarga tabla

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
                    self.cargar_profesores() # Recarga tabla
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
        # Verifica ciclo
        ciclo_id = self.combo_ciclos.currentData()
        
        if not ciclo_id:
            QMessageBox.warning(self, "Aviso", "Selecciona un ciclo válido primero")
            return

        lista_profesores = self.profesor_manager.get_profesores_by_ciclo_id(ciclo_id)
        # Abre diálogo
        dialogo = DialogoModulo(self, ciclo_id=ciclo_id, lista_profesores=lista_profesores)
        
        if dialogo.exec_() == QDialog.Accepted:
            datos = dialogo.obtener_datos()
            
            # Manejo de errores
            if not datos['nombre']:
                QMessageBox.warning(self, "Error", "Por favor, escribe el nombre del módulo")
                return

            # Guarda módulo
            if self.modulo_manager.agregar_modulo(datos):
                self.cargar_modulos() # Actualiza tabla
            else:
                QMessageBox.critical(self, "Error", "No se pudo guardar el módulo")

    def editar_modulo(self):
        # Editar el módulo seleccionado en la tabla
        # Comprobar que la fila es correcta
        fila = self.tabla_modulos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona un módulo para editar")
            return

        # Recupera datos
        item_id_modulo = self.tabla_modulos.item(fila, 0)
        id_modulo = item_id_modulo.data(Qt.UserRole) # ID DB
        nombre = self.tabla_modulos.item(fila, 1).text()
        h_sem = self.tabla_modulos.item(fila, 2).text()
        h_dia = self.tabla_modulos.item(fila, 3).text()

        item_profe = self.tabla_modulos.item(fila, 4)
        profesor_id = item_profe.data(Qt.UserRole) # Recuperamos el id

        datos_actuales = {
            'nombre': nombre,
            'horas_semanales': h_sem,
            'horas_max_dia': h_dia,
            'profesor_id': profesor_id # Pasa datos
        }

        # Abre diálogo edición
        ciclo_id = self.combo_ciclos.currentData()

        # Carga profesores
        lista_profesores = self.profesor_manager.get_profesores_by_ciclo_id(ciclo_id)

        dialogo = DialogoModulo(self, datos_modulo=datos_actuales, ciclo_id=ciclo_id, lista_profesores=lista_profesores)

        if dialogo.exec_() == QDialog.Accepted:
            nuevos_datos = dialogo.obtener_datos()
            if self.modulo_manager.editar_modulo(id_modulo, nuevos_datos):
                self.cargar_modulos() # Actualiza tabla
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
            # Elimina desde manager
            if self.modulo_manager.eliminar_modulo(self.tabla_modulos):
                self.cargar_modulos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo borrar el módulo")

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
        
        # Comprueba que ciclo quiero ver el usuario
        ciclo_actual_id = self.combo_ciclos.currentData()
        # Limpia la tabla visualmente
        self.tabl_horario_grid.clearContents()

        # Obtiene los datos completos del horario
        datos = self.db.obtener_horario_completo()

        if not datos:
            return
        
        # Mapa filas
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

                # Inserta en tabla
                self.tabl_horario_grid.setItem(fila, dia, item)

                # Ajusta tabla
                self.tabl_horario_grid.resizeColumnsToContents()
                self.tabl_horario_grid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.tabl_horario_grid.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

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
                # Genera solo este ciclo
                generador.ejecutar(ciclo_id=ciclo_actual_id)

                # Actualiza vista
                self.cargar_horario()

                QMessageBox.information(self, "Éxito", "¡Horario generado con éxito!", QMessageBox.Ok)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Se ha producido un error: {str(e)}")

    def exportar_horario(self):
        ciclo_actual_id = self.combo_ciclos.currentData()
        
        if not ciclo_actual_id:
            QMessageBox.warning(self, "Aviso", "Selecciona un ciclo válido")
            return
        
        nombre_ciclo=self.combo_ciclos.currentText()
        nombre_horario= f"Horario_{nombre_ciclo}.csv"
    
        datos = self.db.obtener_datos_exportacion(ciclo_id=ciclo_actual_id)

        if not datos:
            QMessageBox.warning(self, "Aviso", f"El horario del ciclo {self.combo_ciclos.currentText()} está vacío. Nada que exportar.")
            return
        
        # Abrir selector de archivos para elegir donde guardar el archivo csv
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Horario CSV", nombre_horario, "Archivos CSV (*.csv)"
        )

        if not ruta:
            return # El usuario canceló la exportacion
        
        if not ruta.endswith('.csv'):
            ruta += '.csv'
        
        try:
            # Llama al método de exportación real. El ExportadorManager devuelve (True/False, Mensaje)
            exito, mensaje = self.exportador.exportar_horario_csv(ruta, datos)

            if exito:
                # Mostrar mensaje de éxito solo si realmente se guardó
                QMessageBox.information(self, "Éxito", mensaje)
            else:
                # Mostrar mensaje de error si el Exportador devuelve False
                QMessageBox.critical(self, "Error", mensaje)
                
        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Fallo al procesar la exportación: {str(e)}")
