import csv
class ExportadorManager:
    def __init__(self):
        pass

    def exportar_horario_csv(self, ruta_archivo, datos):
        if not datos:
            print("No se han podido cargar bien los datos")
            return False
        
        # Definimos los encabezados para el csv
        encabezados = [
            "Día", 
            "Hora Inicio", 
            "Hora Fin", 
            "Ciclo", 
            "Módulo", 
            "Profesor"
        ]

        # Diccionario para mas tarde convertir el "1" a "Lunes", es como un traductor
        mapa_dias = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes"}
        try: 
            # utf-8-sig para que en Excel se muestren bien los caracteres y las tildes
            with open(ruta_archivo, mode='w', newline='', encoding='utf-8-sig') as archivo:
                writer = csv.writer(archivo, delimiter=';')

                writer.writerow(encabezados)

                # Bucle que carga el archivo csv con los datos pasados
                for fila in datos:
                    dia_num = fila.get('dia_semana')
                    dia_txt = mapa_dias.get(dia_num, "Desconocido")

                    hora_ini = fila.get('hora_inicio')
                    hora_fin = fila.get('hora_fin')
                    
                    modulo = fila.get('modulos') or {} # Si la base de datos devolviese "None", Python coge un diccionario vacío para evitar errores
                    # Intenta sacar el nombre. Si el diccionario estaba vacío, devuelve el texto "Sin Modulo".
                    nombre_modulo = modulo.get('nombre', "Sin Modulo")

                    ciclo = modulo.get('ciclos') or {}
                    nombre_ciclo = ciclo.get('nombre', "Sin Ciclo")

                    # Datos del Profesor (Anidados)
                    profe = fila.get('profesores') or {}
                    nombre_profe = profe.get('nombre', "Sin Profesor")

                    # Escribe la fila en el archivo CSV
                    writer.writerow([
                        dia_txt, 
                        hora_ini, 
                        hora_fin, 
                        nombre_ciclo, 
                        nombre_modulo, 
                        nombre_profe
                    ])

            return True, "Horario exportado con éxito."

        except Exception as e:
            return False, f"Error al escribir el archivo: {e}"
        