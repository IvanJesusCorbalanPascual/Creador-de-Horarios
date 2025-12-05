import os
from supabase import create_client, Client

# CONSTANTES
URL = "https://lvcrigxkcyyeqbqfgruo.supabase.co"
KEY = "sb_publishable_AghBIqMcP2jEpnT2DiGYUA_2U2dLRy3"

class DBManager:
    def __init__(self):
        self.client: Client = create_client(URL, KEY)
        print("Cliente de Supabase Inicializado")

    # --- CICLOS ---
    def obtener_ciclos(self):
            # Devuelve todos los ciclos (DAM1, DAW2, etc...)
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
        
    # --- PROFESORES ---
    def obtener_profesores(self):
        try:
            return self.client.table("profesores").select("*").execute().data
        except Exception as e:
            print(f"Error obtener_profesores: {e}")
            return []

    def obtener_profesores_por_ciclo(self, ciclo_id: int):
        # Devuelve los profesores asignados a un ciclo especifico
        try:
            # Seleccionamos la relacion. Supabase devuelve: [{'profesor_id': 1, 'profesores': {'nombre': ...}}]
            res = self.client.table("profesor_ciclo").select("profesor_id, profesores(*)").eq("ciclo_id", ciclo_id).execute()
            
            # Limpiamos la respuesta para devolver una lista de objetos profesor plana
            lista_profesores = []
            for item in res.data:
                if item.get('profesores'):
                    # Flatten the dict
                    profe = item['profesores']
                    lista_profesores.append(profe)
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
        """
        Permite añadir o editar un profesor manualmente pasandole un diccionario
        'nombre': '...', 'horas_max_dia': '...', etc... (DEBE COINCIDIR)
        Si existe este id, se actualizará, sino se creará
        """
        try:
            if "id" in datos and datos["id"]:
                return self.client.table("profesores").update(datos).eq("id", datos["id"]).execute()
            else:
                return self.client.table("profesores").insert(datos).execute()
        except Exception as e:
            print(f"Error al Crear / Editar el profesor: {e}")
            return None
            
    def eliminar_profesor(self, id_profesor: int):
        try:
            res = self.client.table("profesores").delete().eq("id", id_profesor).execute()
            return res.data
        except Exception as e:
            print(f"Error al eliminar el profesor: {e}")
            return None

    # --- MÓDULOS ---
    def obtener_modulos(self):
        # Devuelve la informacion del modulo
        try:
            return self.client.table("modulos").select("*, ciclos(nombre)").execute().data
        except Exception as e:
            print(f"Error al obtener los datos de los modulos: {e}")
            return []
        
    def crear_modulo(self, datos: dict):
        try:
            res = self.client.table("modulos").insert(datos).execute()
            return res.data
        except Exception as e:
            print(f"Error al crear el modulo: {e}")
            return None

    # --- COMPETENCIA ---
    def asignar_competencia(self, profesor_id: int, modulo_id: int):
        # Asigna un modulo a un profesor
        try:
            datos = {"profesor_id": profesor_id, "modulo_id": modulo_id}
            res = self.client.table("competencia_profesor").insert(datos).execute()
            return res.data
        except Exception as e:
            print(f"Error al asignar un modulo al profesor: {e}")
            return None

    def obtener_competencias_profesor(self, profesor_id: int):
        # Devuelve los modulos que puede dar un profesor
        try:
            # Trae info de la tabla modulos a través de la relación
            query = "modulo_id, modulos(*, ciclos(nombre))"
            res = self.client.table("competencia_profesor")\
                .select(query)\
                .eq("profesor_id", profesor_id)\
                .execute()
            # Limpiando la respuesta para devolver solo la lista de módulos
            return [item['modulos'] for item in res.data if item['modulos']]
        except Exception as e:
            print(f"Error obtener_competencias: {e}")
            return []

    # --- PREFERENCIAS ---
    def agregar_preferencia(self, datos: dict):
        """
        datos: {
            'profesor_id': 1, 
            'dia_semana': 0, (0=Lunes según tu lógica)
            'hora_inicio': '08:00', 
            'hora_fin': '10:00', 
            'nivel_prioridad': 1,
            'motivo': 'Médico'
        }
        """
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
        
    def guardar_horario_generado(self, lista_asignaciones: list):
        # Recibe una lista de diccionarios para insertarla de golpe en la bd
        try:
            res = self.client.table("horario_generado").insert(lista_asignaciones).execute()
            return res.data
        except Exception as e:
            print(f"Error guardando el horario generado: {e}")
            return None

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
            modulos(nombre, ciclos(nombre))
            """
            return self.client.table("horario_generado").select(query).execute().data
        except Exception as e:
            print(f"Error al obtener el horario generado: {e}")
            return []

# Instancia única para usar en el resto del programa
db = DBManager()