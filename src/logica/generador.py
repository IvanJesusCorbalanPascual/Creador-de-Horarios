import sys 
import os
import random

# Configuración de rutas
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_raiz = os.path.abspath(os.path.join(ruta_actual, '..', '..'))
sys.path.append(ruta_raiz)

from src.bd.bd_manager import db
from src.logica.gestor_preferencias import GestorPreferencias
from src.logica.validador import Validador

class GeneradorAutomatico:
    def __init__(self):
        print("Inicializando el generador...")

        # Módulos auxiliares
        self.db = db
        self.gest_pref = GestorPreferencias()
        self.validador = Validador()

        self.profesores = []
        self.modulos = []
        # Conflictos encontrados
        self.conflictos = []
        self.advertencias = []

        # Horario generado
        self.profesores_por_modulo = {}

        # Control de ocupación
        self.asignaciones = {}
        self.ocupacion_grupos = {}




    # Obtiene y filtra datos iniciales
    def preparar_datos_supabase(self, ciclo_filtro_id=None):
        print("Descargando los datos necesarios de Supabase...")

        # Carga datos
        self.profesores = self.db.obtener_profesores()
        todos_modulos = self.db.obtener_modulos()

        if ciclo_filtro_id:
            print(f"Filtrando para el ciclo ID: {ciclo_filtro_id}")
            # Filtra por ciclo
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

            # Reinicia estructuras
            self.asignaciones = {}
            self.ocupacion_grupos = {}
            
        except Exception as e:
            print(f"Error intentando preparar los datos: {e} ")
            return False
        
        print(f"Los datos se han encontrado y preparado correctamente. Asignaturas a procesor: {len(self.modulos)}")
        return True
        
    # Ejecuta proceso principal
    def ejecutar(self, ciclo_id = None):

        # Reinicia conflictos
        self.conflictos = []
        # Limpia las advertencias
        self.advertencias = []

        carga_exitosa = self.preparar_datos_supabase(ciclo_id)
        if not carga_exitosa:
            return
        
        print("Comenzando generación automática...")

        exito = self.calcular_distribucion(ignorar_preferencias_leves=False)

        if not exito:
            print("Ha habido un conflicto con preferencias personales (2).")
            print("Reintentando teniendo en cuenta solo restricciones obligatorias (1)")

            # Reinicia para reintento
            self.asignaciones = {}
            self.ocupacion_grupos = {}
            for modulo in self.modulos:
                self.profesores_por_modulo[modulo['id']] = []

            # Reintento ignorando preferencias leves
            if self.calcular_distribucion(ignorar_preferencias_leves=True):
                print("Horario generado exitosamente, han sido ignoradas las preferencias leves")

                self.advertencias.append("Se han ignorado las preferencias de nivel 2, solo se tendran en cuenta las obligatorias")
           
            else:
                print("No ha sido posible generar el horario, se han encontrado conflictos críticos")
        else:
            print("¡Horario generado exitosamente!")


    def guardar_cambios(self):
        print("Guardando los resultados en Supabase..")
        
        datos_para_insertar = []

        # Lista de IDs que han sido procesados
        ids_afectados = list(self.profesores_por_modulo.keys())

        # Procesa horario generado
        for modulo_id, clases in self.profesores_por_modulo.items():
            for clase in clases:
                # Obtiene hora real
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
    
    # Convierte índice a horario real
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

        # Prioriza módulos con más horas
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
                # Aleatoriza días
                random.shuffle(dias_semana)

                for dia in dias_semana:
                    if horas_pendientes == 0: break

                    # Valida el máximo de horas diarias
                    horas_hoy = self.contar_horas_modulo_dia(modulo['id'], dia)
                    if horas_hoy >= modulo.get('horas_max_dia', 2):
                        continue

                    for hora in horas_lectivas:
                        # Verifica ocupación del profesor
                        ocupado = (profesor_id, dia, hora)
                        if ocupado in self.asignaciones:
                            continue

                        # Verifica ocupación del grupo
                        if ciclo_id and (ciclo_id, dia, hora) in self.ocupacion_grupos:
                            continue
                        
                        # Obtiene horario
                        h_inicio, h_fin = self.convertir_indice_a_hora(hora)

                        nivel_de_conflicto = self.gest_pref.comprobar_conflicto(profesor_id, dia, h_inicio, h_fin)

                        # Evita conflicto crítico
                        if nivel_de_conflicto == 1:
                            continue

                        # Evita preferencia personal
                        if nivel_de_conflicto == 2 and not ignorar_preferencias_leves:
                            continue

                        # Asigna hueco
                        self.asignaciones[ocupado] = modulo['id']

                        # Marca grupo ocupado
                        if ciclo_id:
                            self.ocupacion_grupos[(ciclo_id, dia, hora)] = modulo['id']

                        bloque = {'dia': dia, 'hora': hora, 'profesor_id': profesor_id}
                        self.profesores_por_modulo[modulo['id']].append(bloque)

                        horas_pendientes -= 1
                        asignado = True
                        break

                if not asignado:
                    intentos_sin_exito += 1
                    # Aborta tras fallos reiterados
                    if intentos_sin_exito > 100:
                        nombre_profe = "Desconocido"
                        for p in self.profesores:
                            if p['id'] == profesor_id:
                                nombre_profe = p['nombre']
                                break

                        mensaje = f"No hay hueco para asignar '{modulo['nombre']}' al profesor {nombre_profe}"

                        # Imprime el mensaje de error en la consola
                        print(mensaje)

                        # Guarda el mensaje de error en una lista
                        self.conflictos.append(mensaje)

                        return False
        return True
    
    def contar_horas_modulo_dia(self, modulo_id, dia):
        # Cuenta horas diarias del módulo
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
