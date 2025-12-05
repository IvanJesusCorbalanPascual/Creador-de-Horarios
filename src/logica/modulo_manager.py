from PyQt5.QtWidgets import QTableWidget
from src.modelos.modelos import Modulo
from src.bd.bd_manager import bd

class ModuloManager:
    def __init__(self, bd):
        self.bd = bd

    def cargar_modulos_en_tabla(self, tabla_widget, nombre_ciclo_seleccionado):
        if not nombre_ciclo_seleccionado:
            return
        
        print(f"Cargando módulos para : {nombre_ciclo_seleccionado}...")

        datos = self.bd.obtener_modulos_por_ciclo(nombre_ciclo_seleccionado)
        tabla_widget.setRowCount(0)

        if datos:
            for fila_idx, modulo in enumerate(datos):
                tabla_widget.insertRow(fila_idx)

                tabla_widget.setItem(fila_idx, 0, QTableWidget(str(modulo['id'])))
                tabla_widget.setItem(fila_idx, 1, QTableWidget(str(modulo['nombre'])))
                tabla_widget.setItem(fila_idx, 2, QTableWidget(str(modulo['horas_semanales'])))

                if 'horas_max_dia' in modulo:
                    tabla_widget.setItem(fila_idx, 3, QTableWidget(str(modulo['horas_max_dia'])))

            tabla_widget.setColumnHidden(0,True)
            tabla_widget.resizeContentsToColumns()

        else:
            print("No se encontraron módulos para este cilo")

    def agregar_modulo(self, datos):
        # Recibe un diccionario con los datos y llama al metodo de la bd
        if self.bd.crear_modulo(datos):
            return True
        return False
    
    def editar_modulo(self, id_modulo, datos):
        datos['id'] = id_modulo
        if self.bd.crear_modulo(datos):
            return True
        return False
    
    def eliminar_modulo(self, id_modulo):
        