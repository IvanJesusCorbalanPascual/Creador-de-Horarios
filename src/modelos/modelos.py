# Constantes de prioridad
PRIORIDAD_NO = 0 # Normal, el profesor puede
PRIORIDAD_CRITICA = 1 # Rojo, el profesor no pupede
PRIORIDAD_PREFERENCIA = 2 # Amarillo, el profesor prefiere que no

class Ciclo:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    def __str__(self): # Metodo toString
        return self.nombre

class Profesor:
    def __init__(self, id, nombre, color_hex, horas_max_dia, horas_max_semana):
        self.id = id
        self.nombre = nombre
        self.color_hex = color_hex
        self.horas_max_dia = horas_max_dia
        self.horas_max_semana = horas_max_semana

    def __str__(self): # Metodo toString
        return self.nombre

class Modulo:
    def __init__(self, id, nombre, ciclo_id, horas_semanales, horas_max_dia):
        self.id = id
        self.nombre = nombre
        self.ciclo_id = ciclo_id
        self.horas_semanales = horas_semanales   
        self.horas_max_dia = horas_max_dia

    def __str__(self): # Metodo toString
        return self.nombre
    
class Competencia:
    def __init__(self, id, profesor_id, modulo_id):
        self.id = id
        self.profesor_id = profesor_id
        self.modulo_id = modulo_id

class Preferencia:
    def __init__(self, id, profesor_id, dia_semana, hora_inicio, hora_fin, nivel_prioridad, motivo):
        self.id = id
        self.profesor_id = profesor_id
        self.dia_semana = dia_semana
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.nivel_prioridad = nivel_prioridad
        self.motivo = motivo
    
class Horario:
    def __init__(self, id, profesor_id, modulo_id, dia_semana, hora_inicio, hora_fin):
        self.id = id
        self.profesor_id = profesor_id
        self.modulo_id = modulo_id
        self.dia_semana = dia_semana
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin

    # Metodo para calcular cuanto dura una clase en minutos
    def duracion_minutos(self):
        inicio_min = self.hora_inicio.hour * 60 + self.hora_inicio.minute
        fin_min = self.hora_fin.hour * 60 +self.hora_fin.minute
        return fin_min - inicio_min