# src/logica/profesor_manager.py

from src.modelos.modelos import Profesor

from src.bd.bd_manager import db

class ProfesorManager:
    def __init__(self, db_config):
        self.db_config = db_config
        # db_config is not strictly needed if we use the singleton db, 
        # but we keep it for compatibility with existing calls.

    # Mock data for fallback
    _profesores_mock = [
        Profesor(1, "Ana Garcia (Offline)", "#FF5733", 6, 30),
        Profesor(2, "Pedro Lopez (Offline)", "#33FF57", 5, 25),
        Profesor(3, "Marta Diaz (Offline)", "#3357FF", 7, 35)
    ]

    def get_all_profesores(self):
        # Carga todos los profesores desde la DB
        data = db.obtener_profesores()
        
        if not data:
            print("AVISO: Usando datos simulados (Offline Mode)")
            return self._profesores_mock

        profesores = []
        for p_data in data:
            # Profesor(id, nombre, color_hex, horas_max_dia, horas_max_semana)
            # Handle potential missing keys with defaults if necessary, though DB should enforce them.
            prof = Profesor(
                p_data.get('id'),
                p_data.get('nombre'),
                p_data.get('color_hex', '#FFFFFF'), # Default color
                p_data.get('horas_max_dia', 0),
                p_data.get('horas_max_semana', 0)
            )
            profesores.append(prof)
        return profesores
    
    def get_profesores_by_ciclo_id(self, ciclo_id):
        # Carga profesores filtrados por ciclo
        data = db.obtener_profesores_por_ciclo(ciclo_id)
        
        profesores = []
        for p_data in data:
            prof = Profesor(
                p_data.get('id'),
                p_data.get('nombre'),
                p_data.get('color_hex', '#FFFFFF'),
                p_data.get('horas_max_dia', 0),
                p_data.get('horas_max_semana', 0)
            )
            profesores.append(prof)
        return profesores

    def add_profesor(self, profesor):
        # Agrega un nuevo profesor a la DB
        datos = {
            "nombre": profesor.nombre,
            "color_hex": profesor.color_hex,
            "horas_max_dia": profesor.horas_max_dia,
            "horas_max_semana": profesor.horas_max_semana
        }
        res = db.agregar_o_editar_profesor(datos)
        return res is not None

    def update_profesor(self, profesor):
        # Actualiza la informacion de un profesor existente
        datos = {
            "id": profesor.id,
            "nombre": profesor.nombre,
            "color_hex": profesor.color_hex,
            "horas_max_dia": profesor.horas_max_dia,
            "horas_max_semana": profesor.horas_max_semana
        }
        res = db.agregar_o_editar_profesor(datos)
        return res is not None

    def delete_profesor(self, profesor_id):
        # Elimina un profesor por su ID
        res = db.eliminar_profesor(profesor_id)
        return res is not None

    def delete_profesor_from_ciclo(self, profesor_id, ciclo_id):
        # Desvincula un profesor de un ciclo especifico
        res = db.eliminar_profesor_de_ciclo(profesor_id, ciclo_id)
        return res is not None