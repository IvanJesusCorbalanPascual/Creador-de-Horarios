import sys 
import os

# Configuración rutas
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.abspath(os.path.join(ruta_actual, '..', '..'))
sys.path.append(ruta_raiz)

from src.bd.bd_manager import db
from src.logica.validador import Validador

class GestorPreferencias:
    def __init__(self):
        self.validador = Validador()
        # Caché de preferencias
        self.cache_preferencias = []

        # Referencia a DB
        self.db = db

    def cargar_preferencias(self):
        
        datos = self.db.obtener_preferencias()

        if datos is None:
            self.cache_preferencias = []
        else:
            # Almacena en memoria
            self.cache_preferencias = datos

        # Log de carga
        print(f"Se han cargado las preferencias correctamente: {len(self.cache_preferencias)}")
        

    def comprobar_conflicto(self, profesor_id, dia, hora_inicio, hora_fin):
        
        conflicto_actual = 0 # Default: sin conflicto

        # Revisa preferencias
        for preferencia in self.cache_preferencias:
            if preferencia['profesor_id'] == profesor_id and preferencia['dia_semana'] == dia:
                # Verifica solapamiento
                choca = self.validador.existe_solapamiento(hora_inicio, hora_fin, preferencia['hora_inicio'], 
                preferencia['hora_fin'])

                if choca:
                    # Evalúa prioridad
                    prioridad = preferencia['nivel_prioridad']
                    
                    # Conflicto crítico: bloquea
                    if prioridad == 1:
                        return 1
                    
                    # Conflicto leve: registra
                    elif prioridad == 2:
                        conflicto_actual = 2 

        # Devuelve nivel conflicto (0 o 2)
        return conflicto_actual
    
# --- ZONA DE PRUEBAS --- (Creado por Gemini para testeo)
if __name__ == "__main__":
    gestor = GestorPreferencias()
    
    print("\n🕵️ INICIANDO TEST DE GESTOR DE PREFERENCIAS")
    
    # 1. Cargar datos reales (debería salir tu print de "cargadas correctamente")
    gestor.cargar_preferencias()
    
    # DATOS DE PRUEBA
    # Revisa semilla para IDs correctos
    
    id_juan = 1  # (Asegúrate que este sea el ID correcto mirando tu Supabase o semilla)
    dia_lunes = 0
    
    # CASO 1: Choque frontal (08:00 a 09:00) -> Debería dar 1
    resultado = gestor.comprobar_conflicto(id_juan, dia_lunes, "08:00:00", "09:00:00")
    print(f"Prueba Lunes 08:00 (Esperado: 1): {resultado}")

    # CASO 2: Horario libre (11:00 a 12:00) -> Debería dar 0
    resultado = gestor.comprobar_conflicto(id_juan, dia_lunes, "11:00:00", "12:00:00")
    print(f"Prueba Lunes 11:00 (Esperado: 0): {resultado}")