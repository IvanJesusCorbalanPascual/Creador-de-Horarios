import os
from supabase import create_client, Client

# CONSTANTES
URL = "https://lvcrigxkcyyeqbqfgruo.supabase.co"
KEY = "sb_secret_b_o0X_MZDs9IWdxSs-kuHA_W5mNG5dX"

class DBManager:
    def __init__(self):
        self.client: Client = create_client(URL, KEY)
        print("Cliente de Supabase Inicializado")

    # --- CICLOS ---
    def obtener_ciclos(self):
            # Obtiene todos los ciclos (DAM1, etc.)
            try:
                return self.client.table("ciclos").select("*").execute().data
            except Exception as e:
                print(f"Error obtener_ciclos: {e}")
                return []
        
    def crear_ciclo(self, nombre: str):
        try:
            res = self.client.table("ciclos").insert({"nombre": nombre}).execute()
            return res.data
        except Exception as e:
            print(f"Error crear_ciclo: {e}")
            return None
        
    def eliminar_ciclo(self, id_ciclo: int):
        try:
            res = self.client.table("ciclos").delete().eq("id", id_ciclo).execute()
            return res.data
        except Exception as e:
            print(f"Error eliminar_ciclo: {e}")
            return None
        
    # --- PROFESORES ---
    def obtener_profesores(self):
        try:
            return self.client.table("profesores").select("*").execute().data
        except Exception as e:
            print(f"Error obtener_profesores: {e}")
            return []

    def obtener_profesores_por_ciclo(self, ciclo_id: int):
        # Obtiene profesores de un ciclo específico
        try:
            # Obtiene relación profesor-ciclo
            res = self.client.table("profesor_ciclo").select("profesor_id, profesores(*)").eq("ciclo_id", ciclo_id).execute()
            
            # Simplifica la lista de profesores
            lista_profesores = []
            for item in res.data:
                if item.get('profesores'):
                    # Extrae datos del profesor
                    profe = item['profesores']
                    lista_profesores.append(profe)
            if lista_profesores:
               print(f"DEBUG: Primer profesor cargado: {lista_profesores[0]}")
            return lista_profesores
        except Exception as e:
            print(f"Error obtener_profesores_por_ciclo: {e}")
            return []

    def asignar_profesor_a_ciclo(self, profesor_id: int, ciclo_id: int):
        try:
            datos = {"profesor_id": profesor_id, "ciclo_id": ciclo_id}
            return self.client.table("profesor_ciclo").insert(datos).execute()
        except Exception as e:
            print(f"Error al asignar profesor a ciclo: {e}")
            return None

    def eliminar_profesor_de_ciclo(self, profesor_id: int, ciclo_id: int):
        try:
            return self.client.table("profesor_ciclo").delete().eq("profesor_id", profesor_id).eq("ciclo_id", ciclo_id).execute()
        except Exception as e:
            print(f"Error al eliminar profesor de ciclo: {e}")
            return None

    def agregar_o_editar_profesor(self, datos: dict):
        # Añade o edita profesor ('nombre', 'horas_max_dia', etc.)
        try:
            if "id" in datos and datos["id"]: # Si tiene ID, actualiza
                # Guarda ID y copia datos para no modificar original
                pk = datos["id"]
                datos_update = datos.copy()
                del datos_update["id"]
                print(f"Actualizando profesor ID {pk} con: {datos_update}")
                res = self.client.table("profesores").update(datos_update).eq("id", pk).execute()
                print(f"Respuesta Supabase (Update): {res}")
                if not res.data:
                    print(f"ADVERTENCIA: No se actualizó ningún registro con ID {pk}")
                return res
            else: # Si no tiene ID, crea uno nuevo
                print(f"Creando profesor: {datos}")
                res = self.client.table("profesores").insert(datos).execute()
                print(f"Respuesta Supabase (Insert): {res}")
                return res
        except Exception as e:
            print(f"Error al Crear / Editar el profesor: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    def eliminar_profesor(self, id_profesor: int):
        try:
            # Borra relaciones antes de eliminar al profesor
            self.client.table("profesor_ciclo").delete().eq("profesor_id", id_profesor).execute()
            self.client.table("competencia_profesor").delete().eq("profesor_id", id_profesor).execute()
            self.client.table("preferencias").delete().eq("profesor_id", id_profesor).execute()
            self.client.table("horario_generado").delete().eq("profesor_id", id_profesor).execute()

            # Borra el profesor
            res = self.client.table("profesores").delete().eq("id", id_profesor).execute()
            print(f"Profesor borrado: {res.data}")
            return res.data
        except Exception as e:
            print(f"Error al eliminar el profesor: {e}")
            return None

    # --- MÓDULOS ---
    def obtener_modulos(self):
        # Obtiene datos de módulos
        try:
            return self.client.table("modulos").select("*, ciclos(nombre)").execute().data
        except Exception as e:
            print(f"Error al obtener los datos de los modulos: {e}")
            return []
        
    def obtener_modulos_por_ciclo(self, ciclo_id: int):
        try:
            res = self.client.table("modulos")\
                .select("*, profesores(nombre)")\
                .eq("ciclo_id", ciclo_id)\
                .execute()
           
            lista_final = []
            for m in res.data:
                # Obtiene nombre del profesor o 'Sin Asignar'
                nombre_profe = "Sin Asignar"
                if m.get('profesores'):
                    nombre_profe = m['profesores'].get('nombre', "Sin Asignar")
                
                item = {
                    'id': m['id'],
                    'nombre': m['nombre'],
                    'horas_semanales': m['horas_semanales'],
                    'horas_max_dia': m.get('horas_max_dia', 0),
                    'profesor_id': m.get('profesor_id'),
                    'nombre_profesor': nombre_profe      
                }
                lista_final.append(item)
                
            return lista_final

        except Exception as e:
            print(f"Error al obtener módulos del ciclo {ciclo_id}: {e}")
            return []
        
    def obtener_profesores_por_modulo(self, modulo_id: int):
        # Obtiene profesores capacitados para un módulo
        try:
            # Consulta competencias del módulo
            query = "profesor_id, profesores(nombre)"

            res = self.client.table("competencia_profesor")\
                .select(query)\
                .eq("modulo_id", modulo_id)\
                .execute()
            
            # Simplifica lista para UI
            lista_profes = []
            for item in res.data:
                if item.get('profesores'): # Verifica relación
                    profesor_data = {
                        'id': item['profesores']['id'],
                        'nombre': item['profesores']['nombre']
                    }
                    lista_profes.append(profesor_data)
                    
            return lista_profes
        except Exception as e:
            print(f"Error obtener_profesores_por_modulo: {e}")
            return []
        
    def crear_modulo(self, datos: dict):
        try:
            res = self.client.table("modulos").insert(datos).execute()
            return res.data
        except Exception as e:
            print(f"Error al crear el modulo: {e}")
            return None

    def actualizar_modulo(self, id_modulo: int, datos: dict):
        try:
            # Quita ID si existe para no duplicar
            if 'id' in datos:
                del datos['id']
            res = self.client.table("modulos").update(datos).eq("id", id_modulo).execute()
            return res.data
        except Exception as e:
            print(f"Error al actualizar el modulo: {e}")
            return None

    def eliminar_modulo(self, id_modulo: int):
        try:
            res = self.client.table("modulos").delete().eq("id", id_modulo).execute()
            return res.data
        except Exception as e:
            print(f"Error al eliminar el modulo: {e}")
            return None

    # --- COMPETENCIA ---
    def asignar_competencia(self, profesor_id: int, modulo_id: int):
        # Asigna módulo a profesor
        try:
            datos = {"profesor_id": profesor_id, "modulo_id": modulo_id}
            res = self.client.table("competencia_profesor").insert(datos).execute()
            return res.data
        except Exception as e:
            print(f"Error al asignar un modulo al profesor: {e}")
            return None

    def obtener_competencias_profesor(self, profesor_id: int):
        # Obtiene módulos que puede dar un profesor
        try:
            # Obtiene módulos y ciclos relacionados
            query = "modulo_id, modulos(*, ciclos(nombre))"
            res = self.client.table("competencia_profesor")\
                .select(query)\
                .eq("profesor_id", profesor_id)\
                .execute()
            # Extrae solo la lista de módulos
            return [item['modulos'] for item in res.data if item['modulos']]
        except Exception as e:
            print(f"Error obtener_competencias: {e}")
            return []

    # --- PREFERENCIAS ---
    def agregar_preferencia(self, datos: dict):
        # Ejemplo datos: {'profesor_id': 1, 'dia_semana': 0, ...}
        try:
            res = self.client.table("preferencias").insert(datos).execute()
            return res.data
        except Exception as e:
            print(f"Error en agregar preferencia: {e}")
            return None

    def obtener_preferencias(self, profesor_id=None):
        try:
            columnas = "id, profesor_id, dia_semana, nivel_prioridad, motivo, hora_inicio::text, hora_fin::text"

            query = self.client.table("preferencias").select(columnas)
            
            if profesor_id:
                query = query.eq("profesor_id", profesor_id)
            return query.execute().data
        except Exception as e:
            print(f"Error obteniendo las preferencias: {e}")
            return []
        
    def guardar_horario_generado(self, lista_horarios, ids_modulos_afectados):
        # Inserta lista de horarios generados
        try:
            if ids_modulos_afectados:
                self.client.table("horario_generado").delete().in_("modulo_id", ids_modulos_afectados).execute()

            if lista_horarios:
                self.client.table("horario_generado").insert(lista_horarios).execute()

            return None
        
        except Exception as e:
            print(f"Error intentando guardar los horarios: {e}")
            return str(e)

    def limpiar_horarios_anteriores(self):
        try:
            res = self.client.table("horario_generado").delete().neq("id",0).execute().data
            return res.data
        except Exception as e:
            print(f"Error limpiando el horario anterior: {e}")
            return []

    def obtener_horario_completo(self):
        try:
            query= """
            *,
            profesores(nombre, color_hex),
            modulos(nombre, ciclo_id, ciclos(nombre))
            """
            return self.client.table("horario_generado").select(query).execute().data
        except Exception as e:
            print(f"Error al obtener el horario generado: {e}")
            return []
        
    def eliminar_preferencia(self, id_preferencias: int):
        try:
            res = self.client.table("preferencias").delete().eq("id", id_preferencias).execute()
            return res.data
        except Exception as e:
            print(f"Error al intentar eliminar una preferencia: {e}")
            return None

# Instancia única para usar en el resto del programa
db = DBManager()