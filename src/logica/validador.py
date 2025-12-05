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

# --- ZONA DE PRUEBAS (Ejecutar este archivo directamente para probar) Hecho por Gemini, solo para testeo ---
if __name__ == "__main__":
    validador = Validador()
    
    print("\n🔬 INICIANDO PRUEBAS DE LÓGICA DE HORARIOS")
    print("===========================================")

    # ---------------------------------------------------------
    # PRUEBA 1: SOLAPAMIENTOS (Choques de hora)
    # ---------------------------------------------------------
    print("\n[TEST 1] Comprobando Solapamientos de Horario:")

    # CASO A: Choque claro (8:00-10:00 vs 09:00-11:00)
    # Resultado esperado: True
    res_a = validador.existe_solapamiento("08:00:00", "10:00:00", "09:00:00", "11:00:00")
    print(f"  A. Choque parcial (Esperado: True): {res_a}")

    # CASO B: Clases seguidas (8:00-09:00 vs 09:00-10:00)
    # Resultado esperado: False (Una acaba cuando la otra empieza, no chocan)
    res_b = validador.existe_solapamiento("08:00:00", "09:00:00", "09:00:00", "10:00:00")
    print(f"  B. Clases contiguas (Esperado: False): {res_b}")

    # CASO C: Una dentro de otra (08:00-12:00 vs 09:00-10:00)
    # Resultado esperado: True
    res_c = validador.existe_solapamiento("08:00:00", "12:00:00", "09:00:00", "10:00:00")
    print(f"  C. Inclusión total (Esperado: True): {res_c}")

    # ---------------------------------------------------------
    # PRUEBA 2: LÍMITE DE HORAS (Carga de trabajo)
    # ---------------------------------------------------------
    print("\n[TEST 2] Comprobando Límites Diarios:")

    # CASO D: Suma exacta (Lleva 4h, añade 2h, Máximo 6h)
    # Resultado esperado: True
    ok, msg = validador.comprobar_limite_diario(4, 2, 6)
    print(f"  D. Límite exacto (Esperado: True): {ok} -> Mensaje: {msg}")

    # CASO E: Se pasa (Lleva 5h, añade 2h, Máximo 6h)
    # Resultado esperado: False
    ok, msg = validador.comprobar_limite_diario(5, 2, 6)
    print(f"  E. Exceso de horas (Esperado: False): {ok} -> Mensaje: {msg}")

    print("\n===========================================")
    print("FIN DE LAS PRUEBAS. Si los resultados coinciden con lo 'Esperado', tu lógica es sólida.")