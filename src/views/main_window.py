import os
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QDialog, QMessageBox, QHeaderView, QFileDialog, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
from PyQt5 import uic
from datetime import datetime, timedelta

# Importación de Managers
from src.managers.profesor_manager import ProfesorManager
from src.managers.modulo_manager import ModuloManager
from src.managers.ciclo_manager import CicloManager
from src.logica.generador import GeneradorAutomatico
from src.managers.exportador_manager import ExportadorManager
from src.managers.gestor_preferencias import GestorPreferencias

# Importación de Diálogos
from src.views.dialogos import DialogoProfesor, DialogoSeleccionarProfesor
from src.views.dialogos import DialogoModulo
from src.views.dialogos import DialogoListaPreferencias
from src.views.dialogos_horario import DialogoGestionHoras
from src.managers.config_manager import ConfigManager
from PyQt5.QtWidgets import QPushButton, QSizePolicy

# Configuración y DB
from src.bd.bd_manager import db
from src.config import DB_CONFIG

# --- Ventana Principal ---
class MiAplicacion(QMainWindow):
    def __init__(self):
        super().__init__()

        # Inicializamos la base de datos
        self.db = db
        self.modulo_manager = ModuloManager(self.db)
        icon_path = "src/media/reloj.ico"
        self.setWindowIcon(QIcon(icon_path)) # Icono de ventana
        # Cargando la vista principal
        uic.loadUi("src/ui/horarios.ui", self) 
        self.setWindowTitle("Gestor de Ciclos")
        self.config_manager = ConfigManager()
        self.profesor_manager = ProfesorManager(DB_CONFIG)
        self.cargar_ciclos_db() # Cargar ciclos al inicio
        self.btn_generar_auto.clicked.connect(self.ejecutar_generador)
        self.ciclo_manager= CicloManager(self.db)
        self.configuracion_menu()
        self.cambiar_pagina(0) # Pagina por defecto (profesores) al abrir la apliacion
        self.configurar_tabla_horario()
        # Cuando suelta una clase, hace un intercambio de asignaturas
        self.tabl_horario_grid.dropEvent = self.evento_soltar_personalizado
        self.exportador = ExportadorManager()
        self.gestor_pref = GestorPreferencias()
        self.gestor_pref.cargar_preferencias()

    def configuracion_menu(self):

        # Mapeo de Botones
        self.btn_profesores.clicked.connect(lambda: self.cambiar_pagina(0))
        self.btn_modulos.clicked.connect(lambda: self.cambiar_pagina(1))
        self.btn_horarios.clicked.connect(lambda: self.cambiar_pagina(2))
        self.btn_agregar_ciclo.clicked.connect(self.agregar_nuevo_ciclo)
        self.btn_eliminar_ciclo.clicked.connect(self.eliminar_ciclo_actual)
        self.btn_exportar_csv.clicked.connect(self.exportar_horario)
        self.btn_gestionar_horas.clicked.connect(self.abrir_gestion_horas)
        
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

    # Funcion que marca el boton de la seccion actual
    def set_active_tab(self, index):
        self.cambiar_pagina(index)
        # Visualmente marcar el botón
        self.btn_profesores.setChecked(index == 0)
        self.btn_modulos.setChecked(index == 1)
        self.btn_horarios.setChecked(index == 2)

    # Funcion que cambia la pagina (Profesores, Modulos, Horarios)
    def cambiar_pagina(self,index):
        self.stackedWidget.setCurrentIndex(index)

        if index == 0:
            self.cargar_profesores()
        elif index == 1:
            self.cargar_modulos()
        elif index == 2:
            self.cargar_horario()

    def agregar_nuevo_ciclo(self):
        nombre = self.le_ciclo.text().strip()
        if nombre:
            if self.ciclo_manager.agregar_ciclo(nombre):
                self.le_ciclo.clear() # Limpia el LineEdit
                self.cargar_ciclos_db() # Recarga la lista
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
        # Ciclo cambiado a {ciclo_actual}
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
        # Cargando profesores...
        nombre_ciclo = self.combo_ciclos.currentText()
        self.lbl_ciclo_profesor.setText(nombre_ciclo)
        # Obtener ID del ciclo seleccionado
        ciclo_id = self.combo_ciclos.currentData()
        
        if ciclo_id:
            # Filtrando por ciclo ID: {ciclo_id}
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
        ciclo_id = self.combo_ciclos.currentData()

        # Preguntar al usuario
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Añadir Profesor")
        msg_box.setText("¿Cómo quieres añadir el profesor?")
        btn_nuevo = msg_box.addButton("Crear Nuevo", QMessageBox.ActionRole)
        btn_existente = msg_box.addButton("Añadir Existente", QMessageBox.ActionRole) if ciclo_id else None
        btn_cancel = msg_box.addButton("Cancelar", QMessageBox.RejectRole)
        
        msg_box.exec_()
        
        if msg_box.clickedButton() == btn_cancel:
            return

        if msg_box.clickedButton() == btn_nuevo:
             # DialogoProfesor maneja la creación y asignación si se le pasa ciclo_id
             dialogo = DialogoProfesor(self, ciclo_id=ciclo_id)
             if dialogo.exec_() == QDialog.Accepted:
                 self.cargar_profesores()

        elif btn_existente and msg_box.clickedButton() == btn_existente:
             # Lógica para seleccionar existente
             todos_profes = self.profesor_manager.get_all_profesores()
             profes_ciclo = self.profesor_manager.get_profesores_by_ciclo_id(ciclo_id)
             ids_en_ciclo = [p.id for p in profes_ciclo]
             
             # Filtrar: Solo los que NO están ya en el ciclo
             disponibles = [p for p in todos_profes if p.id not in ids_en_ciclo]
             
             if not disponibles:
                 QMessageBox.information(self, "Aviso", "No hay profesores disponibles para añadir (todos asignados o inexistentes).")
                 return
                 
             dialogo_sel = DialogoSeleccionarProfesor(self, disponibles)
             if dialogo_sel.exec_() == QDialog.Accepted:
                 pid = dialogo_sel.profesor_seleccionado_id
                 if self.profesor_manager.assign_profesor_to_cycle(pid, ciclo_id):
                     self.cargar_profesores()
                 else:
                     QMessageBox.critical(self, "Error", "Fallo al asignar profesor al ciclo")

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
                QMessageBox.critical(self, "Error", "No se pudo guardar el módulo")

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
        # Ciclo cambiado a {ciclo_actual}
        indice_actual = self.stackedWidget.currentIndex()
        self.cambiar_pagina(indice_actual) # Carga la misma página en la que estaba el usuario
 
    def cargar_modulos(self):
        # cargando modulos...
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
        # Cargando horarios...
        nombre_ciclo = self.combo_ciclos.currentText()
        self.lbl_ciclo_horario.setText(nombre_ciclo)

        # Activa el bloqueo
        self.bloquear_señales = True

        try:
            # Comprueba que ciclo quiero ver el usuario
            ciclo_actual_id = self.combo_ciclos.currentData()
            # Limpia la tabla visualmente
            self.tabl_horario_grid.clearContents()

            # Obtiene los datos completos del horario
            datos = self.db.obtener_horario_completo()

            if not datos:
                return
            
            # Obtiene las horas configuradas
            horas_configuradas = self.config_manager.obtener_horas()
            
            # Configura la tabla visualmente (Filas)
            self.tabl_horario_grid.setRowCount(len(horas_configuradas))
            
            # Extraer solo la hora de inicio para las etiquetas, manejando dict o str
            etiquetas_filas = []
            mapa_filas = {}
            mapa_filas_reverse = {} # Key: Index, Val: Hora Inicio str
            filas_descanso = []

            for i, h in enumerate(horas_configuradas):
                if isinstance(h, dict):
                    hora_str = h.get("inicio", "00:00:00")
                    fin_str = h.get("fin", "00:00:00")
                    label = f"{hora_str[:5]} - {fin_str[:5]}"
                    
                    if h.get("es_descanso"):
                        label += " (R)"
                        filas_descanso.append(i)
                    
                    etiquetas_filas.append(label)
                else: 
                    hora_str = h # Legacy fallback
                    etiquetas_filas.append(hora_str[:5])
                
                mapa_filas[hora_str] = i
                mapa_filas_reverse[i] = hora_str

            self.tabl_horario_grid.setVerticalHeaderLabels(etiquetas_filas) 

            # Pintamos filas de descanso
            for f_idx in filas_descanso:
                for c_idx in range(self.tabl_horario_grid.columnCount()):
                    # Creamos item vacio para poder pintarlo y bloquearlo
                    item_gris = QTableWidgetItem("") 
                    item_gris.setBackground(QColor("#e0e0e0")) 
                    item_gris.setFlags(Qt.NoItemFlags) 
                    self.tabl_horario_grid.setItem(f_idx, c_idx, item_gris) 

            for clase in datos:

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


                # Busca la fila correspondiente usando las horas dinámicas
                if hora in mapa_filas:
                     fila = mapa_filas[hora]
                else:
                    # Intento de matching parcial si falla exacto (por segundos 00)
                    fila = -1
                    for h_str, f_idx in mapa_filas.items():
                         if h_str.startswith(hora[:5]):
                             fila = f_idx
                             break
                    if fila == -1: continue 

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

                # Guarda el ID único de la fila, asi sabe si lo movemos
                item.setData(Qt.UserRole, clase['id'])
                # Guarda el ID del profesor también en un slot diferente
                item.setData(Qt.UserRole + 1, clase['profesor_id'])


                # Inserta todo en la tabla
                self.tabl_horario_grid.setItem(fila, dia, item)

            # Ajustando el horario a la pantalla
            self.tabl_horario_grid.resizeColumnsToContents()
            self.tabl_horario_grid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.tabl_horario_grid.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        except Exception as e:
                print(f"Error al cargar el horario:: {e}")

        finally:
            # Desactiva el bloqueo independietemente de que falle o no
            self.bloquear_señales = False

    def configurar_tabla_horario(self):
        # Habilita el arrastrar y soltar
        self.tabl_horario_grid.setDragEnabled(True)
        self.tabl_horario_grid.setAcceptDrops(True)
        # Permite mover celdas dentro de la misma tabla
        self.tabl_horario_grid.setDragDropMode(QAbstractItemView.DragDrop)
        self.tabl_horario_grid.setDefaultDropAction(Qt.CopyAction)
        # Hace el intercambio de clases al soltar
        self.tabl_horario_grid.dropEvent = self.evento_soltar_personalizado

        # Conecta el evento de cambiar celda, desconectando primero para evitar errores
        try:
            self.tabl_horario_grid.itemChanged.disconnect()
        except:
            pass
        # self.tabl_horario_grid.itemChanged.connect(self.al_cambiar_celda)


    def al_cambiar_celda(self, item):
        if hasattr(self, 'bloquear_señales') and self.bloquear_señales:
            return
            
        # Guarda en variables datos clave    
        fila = item.row()
        columna = item.column()
        modulo_id = item.data(Qt.UserRole)
        nombre_modulo = item.text()
        
        # Se ha movido: {nombre_modulo} (ID: {modulo_id}) a Día {columna}, Fila {fila}

        if not modulo_id:
            return
        
        # Mapea la fila visual a la hora real MODIFICADO
        horas_configuradas = self.config_manager.obtener_horas()
        
        # Construye el mapa indice -> hora inicio
        mapa_horas = {}
        for i, h in enumerate(horas_configuradas):
             if isinstance(h, dict):
                 mapa_horas[i] = h.get("inicio")
             else:
                 mapa_horas[i] = h

        nueva_hora = mapa_horas.get(fila)

        if not nueva_hora:
            print(f"Error, has soltado la clase en una fila desconocida")
            return
        
        # Guarda el movimiento horario en supabase
        exito = self.db.actualizar_movimiento_horario(modulo_id, columna, nueva_hora)
        
        if exito:
            # El cambio se ha guardado en la BD correctamente
            pass
        else:
            QMessageBox.warning(self, "Error", "No ha sido posible guardar el movimiento en la BD.\n Volver a su sitio al recargar")
        self.cargar_horario()


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

                if generador.conflictos:
                    txt_conflictos = "\n".join(generador.conflictos)
                    QMessageBox.warning(self, "Generación cancelada", 
                                        f"NO se ha guardado el horario, se encontraron incidencias:\n\n{txt_conflictos}\n\nComprueba las restricciones y vuelve a intentarlo")
                    # Comprueba si ha sido un exito a medias
                elif generador.advertencias:
                    # Pregunta si/no
                    txt_avisos = "\n".join(generador.advertencias)
                    pregunta = QMessageBox.question(self, "Conflictos de Preferencia", f"El horario se ha generado, pero \n\n{txt_avisos}\n\n ¿Quieres guardarlo de todas formas ignorando esas preferencias?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    # Si el usuario elige si, guarda los cambios y refresca el horario
                    if pregunta == QMessageBox.Yes:
                        generador.guardar_cambios()
                        self.cargar_horario()
                        QMessageBox.information(self, "Guardado", "Se ha guardado el horario con advertencias")
                    else:
                        QMessageBox.information(self, "Cancelado", "Cancelado, no se han guardado los cambios")
                else:
                    generador.guardar_cambios()
                    self.cargar_horario()
                    QMessageBox.information(self, "Éxito Total", "¡Horario generado perfectamente! Todas las preferencias se han respetado", QMessageBox.Ok)
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

    def abrir_gestion_horas(self):
        # Abre el diálogo de gestión de horas
        dialogo = DialogoGestionHoras(self, self.config_manager)
        if dialogo.exec_() == QDialog.Accepted:
            # Si se guardaron cambios, recargamos el horario para que se redibuje la tabla
            self.cargar_horario()

    def evento_soltar_personalizado(self, event):
        # Obtiene los datos en su origen
        origen = event.source()
        items_seleccionados = origen.selectedItems()
        if not items_seleccionados: return

        item_origen = items_seleccionados[0]
        fila_origen, col_origen = item_origen.row(), item_origen.column()

        # Obtiene los datos en su destino
        indice_destino = self.tabl_horario_grid.indexAt(event.pos())
        if not indice_destino.isValid(): return

        fila_destino, col_destino = indice_destino.row(), indice_destino.column()

        # Si lo sueltas en el mismo sitio donde ya estaba, no hace nada y lo ignora
        # Si lo sueltas en el mismo sitio donde ya estaba, no hace nada y lo ignora
        if fila_origen == fila_destino and col_origen == col_destino:
            event.ignore()
            return
            
        # COMPROBACION RECREO
        horas_config = self.config_manager.obtener_horas()
        if 0 <= fila_destino < len(horas_config):
            hora_dest = horas_config[fila_destino]
            if isinstance(hora_dest, dict) and hora_dest.get("es_descanso", False):
                QMessageBox.warning(self, "Acción no permitida", "No puedes colocar una clase en horas de recreo/descanso.")
                event.ignore()
                return
        
        # Recupera el ID del profesor que se guarda en cargar_horario
        profesor_id = item_origen.data(Qt.UserRole + 1)



        if profesor_id:
            horas_configuradas = self.config_manager.obtener_horas()
            mapa_horas_comprobar = {}
            for i, h in enumerate(horas_configuradas):
                 if isinstance(h, dict):
                     mapa_horas_comprobar[i] = h.get("inicio")
                 else:
                     mapa_horas_comprobar[i] = h

            hora_inicio_check = mapa_horas_comprobar.get(fila_destino)

            def calc_fin_tiempo(h): # PONER COMENTARIOS AQUI URGENTE
                try:
                    d = datetime.strptime(h, "%H:%M:%S")
                    return (d + timedelta(hours=1).strftime("%H:%M:%S"))
                except: return h

            if hora_inicio_check:
                hora_fin_check = calc_fin_tiempo(hora_inicio_check)

                # Pregunta al gestor si existe un conflicto
                nivel_de_conflicto = self.gestor_pref.comprobar_conflicto(profesor_id, col_destino, hora_inicio_check, hora_fin_check)
            
                # Nivel de conflicto obligatorio (1)
                if nivel_de_conflicto == 1:
                    QMessageBox.critical(self, "Movimiento Prohibido", f"El profesor de este modulo tiene una restricción obligatoria para ese día y hora.\n\nNo ha sido posible mover aquí la clase")
                    event.ignore()
                    return
                
                # Nivel de advertencia (2)
                if nivel_de_conflicto == 2:
                    res = QMessageBox.warning(self, "Advertencia", f"El profesor de este modulo prefiero no trabajar ese día y hora.\n\n¿Estás seguro de moverlo aquí?", QMessageBox.Yes | QMessageBox.No)
                    if res == QMessageBox.No:
                        event.ignore()
                        return
 
        # Guarda los IDs para tener los datos para la BD por si acaso
        id_horario_origen = item_origen.data(Qt.UserRole)
        item_destino_pre = self.tabl_horario_grid.item(fila_destino, col_destino)
        id_horario_destino = item_destino_pre.data(Qt.UserRole) if item_destino_pre else None

        # Recupera los items, la información que hay en cada celda
        item_objeto_origen = self.tabl_horario_grid.takeItem(fila_origen, col_origen)  
        item_objeto_destino = self.tabl_horario_grid.takeItem(fila_destino, col_destino)

        # Los coloca en posicion inversa, intercambiandolos
        if item_objeto_origen:
            self.tabl_horario_grid.setItem(fila_destino, col_destino, item_objeto_origen)
        
        if item_objeto_destino:
            self.tabl_horario_grid.setItem(fila_origen, col_origen, item_objeto_destino)

        # Recalcular el mapa indices
        horas_configuradas = self.config_manager.obtener_horas()
        mapa_horas = {}
        for i, h in enumerate(horas_configuradas):
             if isinstance(h, dict):
                 mapa_horas[i] = h.get("inicio")
             else:
                 mapa_horas[i] = h
        

        # Función que suma 1 hora al tiempo
        def calcular_fin(hora_str):
            try:
                dt = datetime.strptime(hora_str, "%H:%M:%S")
                return (dt + timedelta(hours=1)).strftime("%H:%M:%S")
            except: return hora_str

        # Actualiza el origen al destino que movimos en la base de datos
        if id_horario_origen:
            nueva_hora = mapa_horas.get(fila_destino)
            # Lo actualiza en la base de datos, si no es None
            if nueva_hora:
                nueva_hora_fin = calcular_fin(nueva_hora)
                self.db.actualizar_movimiento_horario(id_horario_origen, col_destino, nueva_hora, nueva_hora_fin)

        # Si hay alguien en el destino, lo actualiza también
        if id_horario_destino:
            nueva_hora_dest = mapa_horas.get(fila_origen)
            # Lo actualiza en la base de datos, si no es None
            if nueva_hora_dest:
                nueva_hora_fin_dest = calcular_fin(nueva_hora_dest)
                self.db.actualizar_movimiento_horario(id_horario_destino, col_origen, nueva_hora_dest, nueva_hora_fin_dest)

        event.setDropAction(Qt.CopyAction)
        event.accept()