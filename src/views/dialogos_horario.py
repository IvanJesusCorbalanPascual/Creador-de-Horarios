from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QMessageBox, QHeaderView, 
                             QTimeEdit, QAbstractItemView)
from PyQt5.QtCore import Qt, QTime
from datetime import datetime, timedelta

class DialogoGestionHoras(QDialog):
    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Gestionar Horas del Horario")
        self.resize(600, 500) # Más ancho para que se vea bien
        self.config_manager = config_manager
        
        # Layout Principal
        self.layout = QVBoxLayout(self)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(2)
        self.tabla.setHorizontalHeaderLabels(["Hora Inicio", "Hora Fin"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Establece un ancho mínimo de columna para evitar "fino"
        self.tabla.horizontalHeader().setMinimumSectionSize(150)
        # Establece un alto de fila mayor para que no corte los números
        self.tabla.verticalHeader().setDefaultSectionSize(45)
        
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.layout.addWidget(self.tabla)

        # Botones de Acción
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Añadir Hora")
        self.btn_del = QPushButton("Eliminar Seleccionada")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_del)
        self.layout.addLayout(btn_layout)

        # Botones Aceptar/Cancelar
        final_layout = QHBoxLayout()
        self.btn_save = QPushButton("Guardar Cambios")
        self.btn_cancel = QPushButton("Cancelar")
        
        # Estilos básicos
        self.btn_save.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        self.btn_del.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")

        final_layout.addWidget(self.btn_save)
        final_layout.addWidget(self.btn_cancel)
        self.layout.addLayout(final_layout)

        # Conexiones
        self.btn_add.clicked.connect(self.agregar_fila)
        self.btn_del.clicked.connect(self.eliminar_fila)
        self.btn_save.clicked.connect(self.guardar_cambios)
        self.btn_cancel.clicked.connect(self.reject)

        self.cargar_datos()

    def cargar_datos(self):
        horas_list = self.config_manager.obtener_horas()
        self.tabla.setRowCount(0)
        
        # Compatible con la versión antigua (si devuelve strings) o nueva (dicts)
        for item in horas_list:
            if isinstance(item, dict):
                self.agregar_fila_visual(item.get("inicio", "08:00:00"), item.get("fin", "09:00:00"))
            else:
                fin = self.calcular_fin(item)
                self.agregar_fila_visual(item, fin)

    def agregar_fila_visual(self, hora_inicio_str, hora_fin_str):
        row = self.tabla.rowCount()
        self.tabla.insertRow(row)
        
        # TimeEdit para Inicio
        te_inicio = QTimeEdit()
        te_inicio.setDisplayFormat("HH:mm:ss")
        time_obj_ini = QTime.fromString(hora_inicio_str, "HH:mm:ss")
        te_inicio.setTime(time_obj_ini)
        
        # TimeEdit para Fin (AHORA EDITABLE)
        te_fin = QTimeEdit()
        te_fin.setDisplayFormat("HH:mm:ss")
        time_obj_fin = QTime.fromString(hora_fin_str, "HH:mm:ss")
        te_fin.setTime(time_obj_fin)
        
        self.tabla.setCellWidget(row, 0, te_inicio)
        self.tabla.setCellWidget(row, 1, te_fin)
        
        # Conectamos el cambio de hora de inicio para ajustar el fin si es necesario
        te_inicio.timeChanged.connect(self.al_cambiar_inicio)

    def al_cambiar_inicio(self, nueva_hora):
        sender = self.sender()
        if not sender: return
        
        # Buscamos en qué fila está el widget que envió la señal
        rows = self.tabla.rowCount()
        target_row = -1
        for r in range(rows):
            if self.tabla.cellWidget(r, 0) == sender:
                target_row = r
                break
        
        if target_row == -1: return

        # Obtenemos el widget de fin de esa fila
        te_fin = self.tabla.cellWidget(target_row, 1)
        if not te_fin: return
        
        hora_fin = te_fin.time()
        
        # Si la Nueva Hora de Inicio >= Hora Fin actual, empujamos la hora fin
        # para que sea Inicio + 1 hora
        if nueva_hora >= hora_fin:
             # Usamos datetime para sumar 1 hora fácil
             # nueva_hora es QTime
             ini_dt = datetime.combine(datetime.today(), nueva_hora.toPyTime())
             fin_dt = ini_dt + timedelta(hours=1)
             
             te_fin.setTime(QTime(fin_dt.hour, fin_dt.minute, fin_dt.second))

    def agregar_fila(self):
        # Añade una fila por defecto
        self.agregar_fila_visual("08:00:00", "09:00:00")

    def eliminar_fila(self):
        row = self.tabla.currentRow()
        if row >= 0:
            self.tabla.removeRow(row)
        else:
            QMessageBox.warning(self, "Aviso", "Selecciona una fila para borrar")

    # Eliminamos actualizar_fin automático ya que ahora es manual
    # def actualizar_fin(self, row, qtime): ...

    def calcular_fin(self, hora_str):
        try:
            d = datetime.strptime(hora_str, "%H:%M:%S")
            return (d + timedelta(hours=1)).strftime("%H:%M:%S")
        except: return hora_str

    def guardar_cambios(self):
        nuevas_horas = []
        rows = self.tabla.rowCount()
        
        for r in range(rows):
            widget_ini = self.tabla.cellWidget(r, 0) # QTimeEdit
            widget_fin = self.tabla.cellWidget(r, 1) # QTimeEdit
            
            if widget_ini and widget_fin:
                t_ini = widget_ini.time().toString("HH:mm:ss")
                t_fin = widget_fin.time().toString("HH:mm:ss")
                
                # VALIDACIÓN: Fin debe ser > Inicio
                if t_fin <= t_ini:
                    QMessageBox.warning(self, "Error de Validación", 
                                        f"En la fila {r+1}, la hora final ({t_fin}) debe ser mayor que la inicial ({t_ini}).")
                    return

                nuevas_horas.append({"inicio": t_ini, "fin": t_fin})
        
        # Ordenar las horas por inicio
        nuevas_horas.sort(key=lambda x: x["inicio"])

        if self.config_manager.guardar_horas(nuevas_horas):
            QMessageBox.information(self, "Éxito", "Horas actualizadas correctamente")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la configuración")
