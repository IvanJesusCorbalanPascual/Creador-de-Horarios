from src.bd.bd_manager import db

# Clase de testing para probar la conexion a la bd
#db.crear_ciclo("ASIR1")
print("Datos recibidos:", db.obtener_modulos_por_ciclo(1))
