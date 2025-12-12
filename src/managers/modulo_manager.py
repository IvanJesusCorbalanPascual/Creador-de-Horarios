from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QComboBox
from src.modelos.modelos import Modulo
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class ModuloManager:
    def __init__(self, bd):
        self.bd = bd

    def cargar_modulos_en_tabla(self, tabla_widget, id_ciclo_seleccionado):
        if not id_ciclo_seleccionado:
            return

        datos = self.bd.obtener_modulos_por_ciclo(id_ciclo_seleccionado)
        tabla_widget.setRowCount(0)

        if datos: # bucle que itera sobre todos los modulos en la bd y los inserta en cada fila de la tabla
            for fila_idx, modulo in enumerate(datos):
                tabla_widget.insertRow(fila_idx)

                # Columna 0: ID del modulo
                item_id = QTableWidgetItem(str(modulo['id']))
                item_id.setData(Qt.UserRole, modulo['id']) # Guardamos ID
                tabla_widget.setItem(fila_idx, 0, item_id)

                # Columna 1: Nombre
                tabla_widget.setItem(fila_idx, 1, QTableWidgetItem(str(modulo['nombre'])))

                # Columna 2: Horas Semanales
                tabla_widget.setItem(fila_idx, 2, QTableWidgetItem(str(modulo['horas_semanales'])))

                # Columna 3: Horas Diarias
                tabla_widget.setItem(fila_idx, 3, QTableWidgetItem(str(modulo['horas_max_dia'])))

                # Columna 4: Profesor
                nombre_mostrar = modulo.get('nombre_profesor', "Sin Asignar")
                id_profesor = modulo.get('profesor_id') # Puede ser un número o None

                color_hex = modulo.get('color_profesor')
                item_profe = QTableWidgetItem(nombre_mostrar)
                # Guardamos el ID del profesor "escondido" en la celda
                item_profe.setData(Qt.UserRole, id_profesor) 

                if id_profesor and color_hex:
                    try:
                        # Convertimos el string hex (ej: "#FF5733") a objeto QColor
                        color = QColor(color_hex)
                        if color.isValid():
                            item_profe.setBackground(color)
                            
                            # Si el color es muy oscuro, poner letras blancas para que se lea
                            if color.lightness() < 128:
                                item_profe.setForeground(QColor("white"))
                            else:
                                item_profe.setForeground(QColor("black"))
                    except Exception as e:
                        print(f"Error aplicando color: {e}")
                
                tabla_widget.setItem(fila_idx, 4, item_profe)
            
            # Ocultar la columna 0 (ID) para no mostrar el ID del módulo
            tabla_widget.setColumnHidden(0, True) 
            tabla_widget.resizeColumnsToContents()

        else:
            # No se encontraron módulos para este ciclo
            pass

    def agregar_modulo(self, datos):
        # Recibe un diccionario con los datos y llama al metodo de la bd
        if self.bd.crear_modulo(datos):
            return True
        return False
    
    def editar_modulo(self, id_modulo, datos):
        # datos['id'] = id_modulo # No necesitamos meter el ID en datos si pasamos id_modulo separado
        if self.bd.actualizar_modulo(id_modulo, datos):
            return True
        return False
    
    def eliminar_modulo(self, tabla_widget):
        # Le pasamos la tabla para obtener el ID del módulo seleccionado y eliminarlo de la bd
        fila = tabla_widget.currentRow()
        if fila < 0:
            return False
            
        id_item = tabla_widget.item(fila, 0)
        if not id_item:
            return False
            
        id_modulo = id_item.text()
        if self.bd.eliminar_modulo(id_modulo):
            return True
        return False