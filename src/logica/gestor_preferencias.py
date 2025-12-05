import sys 
import os

# Para encontrar la carpeta src.bd
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.abspath(os.path.join(ruta_actual, '..', '..'))
sys.path.append(ruta_raiz)

from src.bd.bd_manager import db
from src.logica.validador import Validador



class GestorPreferencias:
    def __init__(self):
        self.validador = Validador()
        self.cache_preferencias = [] # Evita tener que consultar la BD muchas veces

        # Guarda la conexión db para usarla despues
        self.db = db

    def cargar_preferencias(self):
        
        datos = self.db.obtener_preferencias()

        if datos is None:
            self.cache_preferencias = []
        else:
            # Guarda solo los datos en la variable
            self.cache_preferencias = datos

        # "len" cuenta cuantos elementos hay en la lista
        print(f"Se han cargado las preferencias correctamente: {len(self.cache_preferencias)}")
        

    def comprobar_conflicto(self, profesor_id, dia, hora_inicio, hora_fin):
        # Si esta vacio las preferencias, lo rellena primero
        if not self.cache_preferencias:
            self.cargar_preferencias()

        conflicto_actual = 0 # Por defecto, asume que no hay conflictos

        # Recorre todas las preferencias guardadas en memoria
        for preferencia in self.cache_preferencias:
            if preferencia['profesor_id'] == profesor_id and preferencia['dia_semana'] == dia:
                # Comprueba si el horario que se quiere poner choca con las preferencias
                choca = self.validador.existe_solapamiento(hora_inicio, hora_fin, preferencia['hora_inicio'], 
                preferencia['hora_fin'])

                if choca:
                    # Decide la gravedad
                    prioridad = preferencia['nivel_prioridad']
                    
                    # Es imposible asignarle la clase, sale inmediatamente del bucle
                    if prioridad == 1:
                        return 1
                    
                    # Apunta que hay una queja, sigue buscando por si hubiera algo peor.
                    elif prioridad == 2:
                        conflicto_actual = 2 

        # Si no ha devuelto 1, devuelve lo que haya encontrado (0 o 2)
        return conflicto_actual
    
# --- ZONA DE PRUEBAS --- (Creado por Gemini para testeo)
if __name__ == "__main__":
    gestor = GestorPreferencias()
    
    print("\n🕵️ INICIANDO TEST DE GESTOR DE PREFERENCIAS")
    
    # 1. Cargar datos reales (debería salir tu print de "cargadas correctamente")
    gestor.cargar_preferencias()
    
    # DATOS DE PRUEBA (Estos tienen que existir en tu Semilla para que funcione)
    # Revisa en tu 'semilla.py' qué ID le diste a Juan y qué restricción pusiste.
    # Por defecto en la semilla era: Juan Perez, Lunes (0), 08:00-09:00, Nivel 1.
    
    id_juan = 1  # (Asegúrate que este sea el ID correcto mirando tu Supabase o semilla)
    dia_lunes = 0
    
    # CASO 1: Choque frontal (08:00 a 09:00) -> Debería dar 1
    resultado = gestor.comprobar_conflicto(id_juan, dia_lunes, "08:00:00", "09:00:00")
    print(f"Prueba Lunes 08:00 (Esperado: 1): {resultado}")

    # CASO 2: Horario libre (11:00 a 12:00) -> Debería dar 0
    resultado = gestor.comprobar_conflicto(id_juan, dia_lunes, "11:00:00", "12:00:00")
    print(f"Prueba Lunes 11:00 (Esperado: 0): {resultado}")

                
        