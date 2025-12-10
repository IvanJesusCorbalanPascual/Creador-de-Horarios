import sys
from PyQt5.QtWidgets import QApplication
from src.ui.app import MiAplicacion
from src.config import GREEN_TONIC_STYLE

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
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GREEN_TONIC_STYLE)
    window = MiAplicacion()
    window.show()
    sys.exit(app.exec_())