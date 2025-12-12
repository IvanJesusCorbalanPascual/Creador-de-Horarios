import os
from supabase import create_client, Client

# CREDENCIALES
URL = "https://lvcrigxkcyyeqbqfgruo.supabase.co"
KEY = "sb_secret_b_o0X_MZDs9IWdxSs-kuHA_W5mNG5dX"   

# Clase que maneja todas las operaciones con la base de datos con el cliente de Supabase
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
        # Devuelve los profesores asignados a un ciclo especifico
        try:
            # Seleccionamos la relacion. Supabase devuelve: [{'profesor_id': 1, 'profesores': {'nombre': ...}}]
            res = self.client.table("profesor_ciclo").select("profesor_id, profesores(*)").eq("ciclo_id", ciclo_id).execute()
            
            # Limpiamos la respuesta para devolver una lista de objetos profesor plana
            lista_profesores = []
            for item in res.data:
                if item.get('profesores'):
                    profe = item['profesores']
                    lista_profesores.append(profe)
            if lista_profesores:
               print("Cargando profesores...")
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
        Si existe este id, el profesor se actualizará, sino, se creará
        """

        try:
            if "id" in datos and datos["id"]: # Si existe un profesor con este id, se actualizan los nuevos datos
                # Almacenando la Primary Key de datos (id)
                pk = datos["id"]

                # Creando una copia de datos para no modificar el original hasta que termine la operacion
                datos_update = datos.copy()

                # Eliminando la PK de la copia para no actualizarla
                del datos_update["id"]
                print(f"Actualizando profesor ID {pk} con: {datos_update}")
                res = self.client.table("profesores").update(datos_update).eq("id", pk).execute()
                print(f"Respuesta Supabase (Update): {res}")
                if not res.data:
                    print(f"ADVERTENCIA: No se actualizó ningún registro con ID {pk}")
                return res
            
            else: # Si no hay id entones se crea / inserta un el nuevo profesor en la bd
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
            # Eliminar relaciones en otras tablas antes de borrar el profesor
            self.client.table("profesor_ciclo").delete().eq("profesor_id", id_profesor).execute()
            self.client.table("competencia_profesor").delete().eq("profesor_id", id_profesor).execute()
            self.client.table("preferencias").delete().eq("profesor_id", id_profesor).execute()
            self.client.table("horario_generado").delete().eq("profesor_id", id_profesor).execute()

            # Finalmente, eliminar el profesor
            res = self.client.table("profesores").delete().eq("id", id_profesor).execute()
            print(f"Profesor borrado: {res.data}")
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
        
    def obtener_modulos_por_ciclo(self, ciclo_id: int):
        try:
            res = self.client.table("modulos")\
                .select("*, profesores(nombre, color_hex)")\
                .eq("ciclo_id", ciclo_id)\
                .execute()
           
            lista_final = []
            for m in res.data:
                # Obtenemos el nombre del dict anidado si existe, sino, es None
                nombre_profe = "Sin Asignar"
                if m.get('profesores'):
                    nombre_profe = m['profesores'].get('nombre', "Sin Asignar")
                
                item = {
                    'id': m['id'],
                    'nombre': m['nombre'],
                    'horas_semanales': m['horas_semanales'],
                    'horas_max_dia': m.get('horas_max_dia', 0),
                    'profesor_id': m.get('profesor_id'),
                    'nombre_profesor': nombre_profe,
                    'color_profesor': m.get('profesores').get('color_hex')      
                }
                lista_final.append(item)
                
            return lista_final

        except Exception as e:
            print(f"Error al obtener módulos del ciclo {ciclo_id}: {e}")
            return []
        
    def obtener_profesores_por_modulo(self, modulo_id: int):
        # Devuelve la lista de nombres de profesores que pueden impartir un módulo
        try:
            # Consulta: de competencia, trae el nombre del profesor que coincide con el modulo_id
            query = "profesor_id, profesores(nombre)"

            res = self.client.table("competencia_profesor")\
                .select(query)\
                .eq("modulo_id", modulo_id)\
                .execute()
            
            # Limpiamos la respuesta para que sea fácil de usar en PyQt
            lista_profes = []
            for item in res.data:
                if item.get('profesores'): # Verificar que la relación existe
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
            # Remove id from datos if present to avoid changing PK
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

    # --- COMPETENCIAS ---
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

    def eliminar_preferencia(self, id_preferencias: int):
        try:
            res = self.client.table("preferencias").delete().eq("id", id_preferencias).execute()
            return res.data
        except Exception as e:
            print(f"Error al intentar eliminar una preferencia: {e}")
            return None
        
    # --- HORARIOS ---
    def guardar_horario_generado(self, lista_horarios, ids_modulos_afectados):
        # Recibe una lista de diccionarios para insertarla de golpe en la bd
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

    def actualizar_movimiento_horario(self, id_horario_generado: int, nuevo_dia: int, nueva_hora: str, nueva_hora_fin: str):
        try:
            # Usa el id de la fila para el movimiento
            res = self.client.table("horario_generado")\
            .update({"dia_semana": nuevo_dia, "hora_inicio": nueva_hora, "hora_fin": nueva_hora_fin})\
            .eq("id", id_horario_generado)\
            .execute()

            # Si devuelve datos funciono correctamente
            return len(res.data) > 0
        except Exception as e:
            print(f"Error al mover la clase en la BD: {e}")
            return False

    # --- EXPORTACIÓN ---
    def obtener_datos_exportacion(self, ciclo_id=None):
        try:
            # Pedimos el ID del ciclo dentro de la relación para poder verificarlo luego
            query = (
                "dia_semana, hora_inicio, hora_fin,"
                "modulos (nombre, ciclos (nombre, id))," 
                "profesores (nombre)"
            )

            # Limpia los saltos de línea y espacios para que funcione la consulta
            query_limpia = query.replace('\n', '').replace(' ', '')
            
            # 1. Consulta a BD
            res = self.client.table("horario_generado").select(query_limpia)
            if ciclo_id:
                res = res.eq('modulos.ciclo_id', ciclo_id)
            
            resultado = res.execute()
            datos_crudos = resultado.data or []
            
            # --- CORRECCIÓN: FILTRO DE SEGURIDAD EN PYTHON ---
            # Esto elimina las filas "fantasma" donde el módulo ya no existe (None)
            datos_limpios = []
            
            if ciclo_id:
                for fila in datos_crudos:
                    # Verificamos que la estructura esté completa
                    modulo = fila.get('modulos')
                    if modulo and modulo.get('ciclos'):
                        # Comprobamos que el ID del ciclo coincida exactamente
                        if modulo['ciclos'].get('id') == ciclo_id:
                            datos_limpios.append(fila)
            else:
                # Si no se filtró por ciclo, devolvemos todo lo que tenga datos válidos
                datos_limpios = [d for d in datos_crudos if d.get('modulos')]

            return datos_limpios
        
        except Exception as e:
            print(f"Error obteniendo datos exportación: {e}")
            return []
        
# Instancia única para usar en el resto del programa
db = DBManager()