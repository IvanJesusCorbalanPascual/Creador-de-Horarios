# src/logica/profesor_manager.py

from src.modelos.modelos import Profesor

class ProfesorManager:
    # Simulacion de una 'tabla' de profesores en memoria
    _profesores = [
        Profesor(1, "Ana Garcia", "#FF5733", 6, 30),
        Profesor(2, "Pedro Lopez", "#33FF57", 5, 25),
        Profesor(3, "Marta Diaz", "#3357FF", 7, 35)
    ]
    _next_id = 4 # Proximo ID para simular la DB

    def __init__(self, db_config):
        self.db_config = db_config

    def get_all_profesores(self):
        # Carga todos los profesores desde la DB
        return self._profesores

    def add_profesor(self, profesor):
        # Agrega un nuevo profesor a la DB
        profesor.id = self._next_id
        self._next_id += 1
        self._profesores.append(profesor)
        return True 

    def update_profesor(self, profesor):
        # Actualiza la informacion de un profesor existente
        for i, p in enumerate(self._profesores):
            if p.id == profesor.id:
                self._profesores[i] = profesor 
                return True
        return False

    def delete_profesor(self, profesor_id):
        # Elimina un profesor por su ID
        initial_count = len(self._profesores)
        self._profesores = [p for p in self._profesores if p.id != profesor_id]
        return len(self._profesores) < initial_count