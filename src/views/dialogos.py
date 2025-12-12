import os
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QLabel, QComboBox, QVBoxLayout, QAbstractItemView, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from src.bd.bd_manager import db
from src.managers.profesor_manager import ProfesorManager
from src.modelos.modelos import Profesor
from src.config import DB_CONFIG

class DialogoProfesor(QDialog):
    def __init__(self, parent=None, profesor=None, ciclo_id=None):
        super().__init__(parent)
        uic.loadUi(os.path.join("src", "ui", "profesor_form.ui"), self) 
        self.profesor_manager = ProfesorManager(DB_CONFIG)
        self.profesor = profesor
        self.ciclo_id = ciclo_id
        self.setWindowTitle("Editar Profesor" if profesor else "Agregar Profesor")
        
        if self.profesor:
            self.le_nombre.setText(profesor.nombre)
            self.sb_horas_max_dia.setValue(profesor.horas_max_dia)
            self.sb_horas_max_semana.setValue(profesor.horas_max_semana)

        if not self.profesor:
            self.ciclos_db = db.obtener_ciclos()
            if self.ciclos_db:
                self.lbl_ciclo = QLabel("Asignar a Ciclo:", self)
                self.combo_ciclo_nuevo = QComboBox(self)
                self.combo_ciclo_nuevo.addItem("Ninguno", None)
                index_default = 0
                for i, c in enumerate(self.ciclos_db):
                    self.combo_ciclo_nuevo.addItem(c['nombre'], c['id'])
                    if self.ciclo_id and c['id'] == self.ciclo_id:
                        index_default = i + 1
                self.combo_ciclo_nuevo.setCurrentIndex(index_default)

                if self.layout():
                     cnt = self.layout().count()
                     self.layout().insertWidget(cnt - 1, self.lbl_ciclo)
                     self.layout().insertWidget(cnt - 1, self.combo_ciclo_nuevo)
                else:
                    layout = QVBoxLayout()
                    layout.addWidget(self.lbl_ciclo)
                    layout.addWidget(self.combo_ciclo_nuevo)
                    self.setLayout(layout)

        self.buttonBox.accepted.connect(self.aceptar)
        self.buttonBox.rejected.connect(self.reject)
        self.bloquear_señales = False

    def aceptar(self):
        nombre = self.le_nombre.text().strip()
        h_dia = self.sb_horas_max_dia.value()
        h_sem = self.sb_horas_max_semana.value()

        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacio")
            return

        if self.profesor:
            self.profesor.nombre = nombre
            self.profesor.horas_max_dia = h_dia
            self.profesor.horas_max_semana = h_sem
            exito = self.profesor_manager.update_profesor(self.profesor)
        else:
            import random
            color_random = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            nuevo_profe = Profesor(None, nombre, color_random, h_dia, h_sem)
            nuevo_id = self.profesor_manager.add_profesor(nuevo_profe)
            exito = nuevo_id is not None
            
            if exito:
                ciclo_selec_id = None
                if hasattr(self, 'combo_ciclo_nuevo'):
                    ciclo_selec_id = self.combo_ciclo_nuevo.currentData()
                if not ciclo_selec_id and self.ciclo_id:
                    ciclo_selec_id = self.ciclo_id
                if ciclo_selec_id:
                    self.profesor_manager.assign_profesor_to_cycle(nuevo_id, ciclo_selec_id)
        
        if exito:
            self.accept()
        else:
            QMessageBox.critical(self, "Error de DB", "Fallo al guardar en la base de datos")

class DialogoModulo(QDialog):
    def __init__(self, parent=None, datos_modulo=None, ciclo_id=None, lista_profesores=[]):
        super().__init__(parent)
        uic.loadUi(os.path.join("src", "ui", "modulo_form.ui"), self)
        
        self.datos_modulo = datos_modulo
        self.ciclo_id = ciclo_id

        self.combo_profe.clear()
        self.combo_profe.addItem("Sin Asignar", None)

        id_actual = str(datos_modulo.get('profesor_id')) if datos_modulo and datos_modulo.get('profesor_id') else None
        index_a_seleccionar = 0

        for i, profe in enumerate(lista_profesores):
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
                self.combo_profe.setCurrentIndex(index_a_seleccionar)
            else:
                self.setWindowTitle("Agregar Módulo")

    def obtener_datos(self):
        profesor_id_seleccionado = self.combo_profe.currentData()
        return {
            "nombre": self.le_nombre.text().strip(),
            "horas_semanales": self.sb_horas_max_semana.value(),
            "horas_max_dia": self.sb_horas_max_dia.value(),
            "profesor_id": profesor_id_seleccionado,
            "ciclo_id": self.ciclo_id 
        }

class DialogoPreferencia(QDialog):
    def __init__(self, parent=None, profesor_id=None, nombre_profe=""):
        super().__init__(parent)
        uic.loadUi(os.path.join("src", "ui", "preferencia_form.ui"), self)
        self.profesor_id = profesor_id
        self.setWindowTitle(f"Restricción para: {nombre_profe}")

        self.buttonBox.accepted.connect(self.aceptar)
        self.buttonBox.rejected.connect(self.reject)
            
    def aceptar(self):
        dia_semana = self.cb_dia.currentIndex()
        hora_inicio = self.te_inicio.time().toString("HH:mm:ss")
        hora_fin = self.te_fin.time().toString("HH:mm:ss")
        tipo_index = self.cb_tipo.currentIndex()
        prioridad = 1 if tipo_index == 0 else 2
        motivo = ""
        if hasattr(self, 'le_motivo'):
            motivo = self.le_motivo.text().strip()

        if hora_inicio >= hora_fin:
            QMessageBox.warning(self, "Error", "La hora de inicio debe ser anterior a la de fin.")
            return
            
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
        self.setWindowTitle(f"Gestionar: {nombre_profe}")
        if hasattr(self, 'lbl_nombre_profe'):
            self.lbl_nombre_profe.setText(f"Restricciones de: {nombre_profe}")

        self.tabla_restricciones.setColumnCount(5)
        self.tabla_restricciones.setHorizontalHeaderLabels(["Día", "Inicio", "Fin", "Prioridad", "Motivo"])
        self.tabla_restricciones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_restricciones.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.btn_nueva.clicked.connect(self.abrir_nueva_restriccion)
        self.btn_borrar.clicked.connect(self.borrar_restriccion_seleccionada)
        self.btn_cerrar.clicked.connect(self.reject)
        self.cargar_datos()

    def cargar_datos(self):
        datos = db.obtener_preferencias(self.profesor_id)
        self.tabla_restricciones.setRowCount(0)
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

        for fila, pref in enumerate(datos):
            self.tabla_restricciones.insertRow(fila)
            dia_txt = dias_semana[pref['dia_semana']] if 0 <= pref['dia_semana'] < 5 else "Desconocido"
            self.tabla_restricciones.setItem(fila, 0, QTableWidgetItem(dia_txt))
            self.tabla_restricciones.setItem(fila, 1, QTableWidgetItem(str(pref['hora_inicio'])))
            self.tabla_restricciones.setItem(fila, 2, QTableWidgetItem(str(pref['hora_fin'])))
            prior_txt = "Obligatorio" if pref['nivel_prioridad'] == 1 else "Preferiblemente"
            self.tabla_restricciones.setItem(fila, 3, QTableWidgetItem(prior_txt))
            self.tabla_restricciones.setItem(fila, 4, QTableWidgetItem(str(pref['motivo'])))
            self.tabla_restricciones.item(fila, 0).setData(Qt.UserRole, pref['id'])

    def abrir_nueva_restriccion(self):
        dialogo = DialogoPreferencia(self, self.profesor_id, "Nueva Restricción")
        if dialogo.exec_() == QDialog.Accepted:
            self.cargar_datos()

    def borrar_restriccion_seleccionada(self):
        fila = self.tabla_restricciones.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Debes seleccionar una fila para borrar")
            return
        id_pref = self.tabla_restricciones.item(fila, 0).data(Qt.UserRole)
        confirm = QMessageBox.question(self, "ELIMINAR", "¿SEGURO que quieres eliminar esta restricción?", 
                                        QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            if db.eliminar_preferencia(id_pref):
                self.cargar_datos()
            else:
                QMessageBox.critical(self, "Error", "No ha sido posible eliminar")