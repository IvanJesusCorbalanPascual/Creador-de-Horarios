from src.bd.bd_manager import db

class CicloManager:
    def __init__(self, db_manager=None):
        self.db = db_manager if db_manager else db

    def agregar_ciclo(self, nombre):
        if not nombre or len(nombre.strip()) == 0:
            return False, "El nombre no puede estar vacío."
        
        resultado = self.db.crear_ciclo(nombre.strip())
        if resultado:
            return True, "Ciclo creado correctamente."
        else:
            return False, "Error al guardar en la base de datos."

    def eliminar_ciclo(self, id_ciclo):
        if not id_ciclo:
            return False, "No hay un ciclo seleccionado."
        
        resultado = self.db.eliminar_ciclo(id_ciclo)
        if resultado:
            return True, "Ciclo eliminado correctamente."
        else:
            return False, "No se pudo eliminar el ciclo (puede tener datos asociados)."