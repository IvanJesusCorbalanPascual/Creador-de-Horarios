from datetime import datetime, time

class Validador:
    def __init__(self):
        # Define el formato que se usa en la base de datos (Hora, minutos, segundos)
        self.formato_hora = "%H:%M:%S" 


    # Comprueba si existe solapamiento entre asignaturas
    def existe_solapamiento(self, inicio1, fin1, inicio2, fin2):

        # Convierte el texto a objetos de tiempo
        texto_inicio1 = datetime.strptime(inicio1, self.formato_hora)
        texto_final1 = datetime.strptime(fin1, self.formato_hora)
        texto_inicio2 = datetime.strptime(inicio2, self.formato_hora)
        texto_final2 = datetime.strptime(fin2, self.formato_hora)


        if (texto_inicio1 < texto_final2) and (texto_final1 > texto_inicio2):
            return True # Existe solapamiento
        else:
            return False # Todo correcto
        
    # Comprueba al añadir una clase si pasamos el límite
    def comprobar_limite_diario(self, horas_actuales, nueva_duracion, maximo_permitido):
        total = horas_actuales + nueva_duracion

        if total > maximo_permitido:
            return False, f"Error: {total} supera el máximo de horas permitidas: {maximo_permitido}"
        
        return True, "Agregado correctamente."