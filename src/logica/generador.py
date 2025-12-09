import sys 
import os
import random

# Bloque para detectar las rutas correctamente
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.abspath(os.path.join(ruta_actual, '..', '..'))
sys.path.append(ruta_raiz)

from src.bd.bd_manager import db
from src.logica.gestor_preferencias import GestorPreferencias
from src.logica.validador import Validador

class GeneradorAutomatico:
    def __init__(self):
        print("Inicializando el generador...")

        # Estas son nuestras herramientas
        self.db = db
        self.gest_pref = GestorPreferencias()
        self.validador = Validador()

        self.profesores = []
        self.modulos = []
        # Lista que guarda los conflictos
        self.conflictos = []

        # Aqui se guarda el horario generado
        self.profesores_por_modulo = {}

        # Evita duplicados de profesor
        self.asignaciones = {}

        # Evita duplicados de grupo/alumnos
        self.ocupacion_grupos = {}




    # Descarga los datos de Supabase antes de empezar y filtra por ciclos
    def preparar_datos_supabase(self, ciclo_filtro_id=None):
        print("Descargando los datos necesarios de Supabase...")

        # Carga los datos
        self.profesores = self.db.obtener_profesores()
        # Descarga todos
        todos_modulos = self.db.obtener_modulos()

        if ciclo_filtro_id:
            print(f"Filtrando para el ciclo ID: {ciclo_filtro_id}")
            # Se queda solo los módulos de este ciclo
            self.modulos = [m for m in todos_modulos if m.get('ciclo_id') == ciclo_filtro_id]
        else:
            self.modulos = todos_modulos

        # Carga las preferencias
        self.gest_pref.cargar_preferencias()

        if not self.profesores or not self.modulos:
            print("Error: No se han encontrado profesores o módulos para este ciclo")
            return False
        
        try:
            for modulo in self.modulos:
                self.profesores_por_modulo[modulo['id']] = []

            # Limpia asignaciones previas
            self.asignaciones = {}

            self.ocupacion_grupos = {}
            
        except Exception as e:
            print(f"Error intentando preparar los datos: {e} ")
            return False
        
        print(f"Los datos se han encontrado y preparado correctamente. Asignaturas a procesor: {len(self.modulos)}")
        return True
        
    # Comprueba que todo carga al ejecutarse
    def ejecutar(self, ciclo_id = None):

        # Limpia los conflictos 
        self.conflictos = []

        carga_exitosa = self.preparar_datos_supabase(ciclo_id)
        if not carga_exitosa:
            return
        
        print("Comenzando generación automática...")

        exito = self.calcular_distribucion(ignorar_preferencias_leves=False)

        if not exito:
            print("Ha habido un conflicto con preferencias personales (2).")
            print("Reintentando teniendo en cuenta solo restricciones obligatorias (1)")

            # Limpia completamente para intentarlo de nuevo
            self.asignaciones = {}
            self.ocupacion_grupos = {}
            for modulo in self.modulos:
                self.profesores_por_modulo[modulo['id']] = []

            # Ignora las preferencias leves en el 2º intento
            if self.calcular_distribucion(ignorar_preferencias_leves=True):
                print("Horario generado exitosamente, han sido ignoradas las preferencias leves.")
                self.guardar_cambios()
            else:
                print("No ha sido posible generar el horario, se han encontrado conflictos críticos.")
        else:
            print("¡Horario generado exitosamente!")
            self.guardar_cambios()


    def guardar_cambios(self):
        print("Guardando los resultados en Supabase..")
        
        datos_para_insertar = []

        # Lista de IDs que han sido procesados
        ids_afectados = list(self.profesores_por_modulo.keys())

        # Recorre el resultado en la memoria
        for modulo_id, clases in self.profesores_por_modulo.items():
            for clase in clases:
                # Convierte el numero de horas a hora real
                h_inicio, h_fin = self.convertir_indice_a_hora(clase['hora'])
                
                fila = {
                    "modulo_id": modulo_id,
                    "dia_semana": clase['dia'],
                    "hora_inicio": h_inicio,
                    "hora_fin": h_fin,
                    "profesor_id": clase['profesor_id']
                }
                datos_para_insertar.append(fila)

        if datos_para_insertar:
            error = self.db.guardar_horario_generado(datos_para_insertar, ids_afectados)
            if not error:
                print(f"Han sido guardadas exitosamente {len(datos_para_insertar)} clases en la base de datos.")
            else:
                print(f"Error al guardar en la base de datos: {error}")

    # Ayuda en el ordenamiento
    def obtener_horas_para_ordenar(self, modulo):
        return modulo['horas_semanales']
    
    # Traduce los numeros a horas reales para comparar con las preferencias
    def convertir_indice_a_hora(self, indice):
        mapa = {
            1: ("08:00:00", "09:00:00"),
            2: ("09:00:00", "10:00:00"),
            3: ("10:00:00", "11:00:00"),
            4: ("11:30:00", "12:30:00"),
            5: ("12:30:00", "13:30:00"),
            6: ("13:30:00", "14:30:00")
        }
        return mapa.get(indice, ("00:00:00", "00:00:00"))
       
    def calcular_distribucion(self, ignorar_preferencias_leves):
        dias_semana = [0, 1, 2, 3, 4]
        horas_lectivas = [1, 2, 3, 4, 5, 6]

        # Ordena de mayor a menor colocando primero las asignaturas grandes
        modulos_ordenados = sorted(self.modulos, key=self.obtener_horas_para_ordenar, reverse=True)

        for modulo in modulos_ordenados:
            horas_pendientes = modulo['horas_semanales']
            # Lee el ID en el diccionario
            profesor_id = modulo.get('profesor_id')
            # Lee el ID del ciclo
            ciclo_id = modulo.get('ciclo_id')

            # Si esta vacio, lo salta
            if profesor_id is None:
                continue

            # Comprueba que el ID existe en la tabla de profesores
            ids_disponibles = [p['id'] for p in self.profesores]
            if profesor_id not in ids_disponibles:
                print(f" Error, el módulo '{modulo['nombre']}' tiene profesor_id={profesor_id} y no existe en la tabla de profesores")
                continue

            intentos_sin_exito = 0
            while horas_pendientes > 0:
                asignado = False
                # Prueba días aleatorios para hacerlo variado
                random.shuffle(dias_semana)

                for dia in dias_semana:
                    if horas_pendientes == 0: break

                    # Valida el máximo de horas diarias
                    horas_hoy = self.contar_horas_modulo_dia(modulo['id'], dia)
                    if horas_hoy >= modulo.get('horas_max_dia', 2):
                        continue

                    for hora in horas_lectivas:
                        # Valida si el profesor esta ocupado
                        ocupado = (profesor_id, dia, hora)
                        if ocupado in self.asignaciones:
                            continue

                        # Si se tiene clase a esta hora no permite poner otra
                        if ciclo_id and (ciclo_id, dia, hora) in self.ocupacion_grupos:
                            continue
                        
                        # Traduce en numero de hora a String
                        h_inicio, h_fin = self.convertir_indice_a_hora(hora)

                        nivel_de_conflicto = self.gest_pref.comprobar_conflicto(profesor_id, dia, h_inicio, h_fin)

                        # Salta si el nivel de conflicto es 1
                        if nivel_de_conflicto == 1:
                            continue

                        # Siendo preferencia, salta solo si no estamos ignorandolas
                        if nivel_de_conflicto == 2 and not ignorar_preferencias_leves:
                            continue

                        # Asigna los huecos
                        self.asignaciones[ocupado] = modulo['id']

                        # Marca el grupo como ocupado
                        if ciclo_id:
                            self.ocupacion_grupos[(ciclo_id, dia, hora)] = modulo['id']

                        bloque = {'dia': dia, 'hora': hora, 'profesor_id': profesor_id}
                        self.profesores_por_modulo[modulo['id']].append(bloque)

                        horas_pendientes -= 1
                        asignado = True
                        break

                if not asignado:
                    intentos_sin_exito += 1
                    # Si falla muchas veces + de 100, cancela el intento
                    if intentos_sin_exito > 100:
                        mensaje = f"Error Crítico: No se ha podido asignar '{modulo['nombre']}' (Profesor ID: {profesor_id}) por falta de hueco o restricciones"
                        # Imprime el mensaje de error en la consola
                        print(mensaje)

                        # Guarda el mensaje de error en una lista
                        self.conflictos.append(mensaje)

                        return False
        return True
    
    def contar_horas_modulo_dia(self, modulo_id, dia):
        # Cuenta cuantas horas lleva ya este modulo en este día
        count = 0
        if modulo_id in self.profesores_por_modulo:
            for clase in self.profesores_por_modulo[modulo_id]:
                if clase['dia'] == dia:
                    count += 1
        return count

# --- Zona de pruebas ---
if __name__ == "__main__":
    generador = GeneradorAutomatico()
    generador.ejecutar()

    