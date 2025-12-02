from supabase import create_client
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QHeaderView
)
 
URL = "https://lvcrigxkcyyeqbqfgruo.supabase.co"
KEY = "sb_publishable_AghBIqMcP2jEpnT2DiGYUA_2U2dLRy3"
 
supabase = create_client(URL, KEY)
 
class Ventana(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Tareas")
        self.setGeometry(100, 100, 600, 400)
 
        self.widget = QWidget()
        self.layout = QVBoxLayout()
 
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Tarea", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
 
        self.input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Nueva tarea")
        self.add_button = QPushButton("Agregar")
        self.add_button.clicked.connect(self.agregar_tarea)
 
        self.input_layout.addWidget(self.task_input)
        self.input_layout.addWidget(self.add_button)
 
        self.layout.addLayout(self.input_layout)
        self.layout.addWidget(self.table)
 
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
 
        self.cargar_tareas()
 
    def cargar_tareas(self):
        self.table.setRowCount(0)
        tareas = supabase.table("tareas").select("*").execute().data
        for tarea in tareas:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(tarea['id'])))
            self.table.setItem(row_position, 1, QTableWidgetItem(tarea['descripcion']))
            estado_item = QTableWidgetItem("Completada" if tarea['completada'] else "Pendiente")
            self.table.setItem(row_position, 2, estado_item)
 
    def agregar_tarea(self):
        descripcion = self.task_input.text().strip()
        if descripcion:
            supabase.table("tareas").insert({"descripcion": descripcion, "completada": False}).execute()
            self.task_input.clear()
            self.cargar_tareas()
        else:
            QMessageBox.warning(self, "Entrada inválida", "La descripción de la tarea no puede estar vacía.")
 
if __name__ == "__main__":
    app = QApplication([])
    ventana = Ventana()
    ventana.show()
    app.exec_()