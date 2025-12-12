import json
import os

class ConfigManager:
    def __init__(self, config_file="horarios_config.json"):
        self.config_file = config_file
        # Ahora usamos diccionarios para flexibilidad
        self.horas_default = [
            {"inicio": "08:30:00", "fin": "09:25:00"},
            {"inicio": "09:25:00", "fin": "10:20:00"},
            {"inicio": "10:20:00", "fin": "11:15:00"},
            {"inicio": "11:45:00", "fin": "12:40:00"},
            {"inicio": "12:40:00", "fin": "13:35:00"},
            {"inicio": "13:35:00", "fin": "14:30:00"}
        ]
        self.horas = self.cargar_horas()

    def cargar_horas(self):
        """Carga las horas desde el archivo JSON, o usa las por defecto."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    raw_horas = data.get("horas", [])
                    
                    # Migración simple: Si son strings, conviértelos a objetos
                    horas_procesadas = []
                    if raw_horas and isinstance(raw_horas[0], str):
                         from datetime import datetime, timedelta
                         for h in raw_horas:
                             try:
                                d = datetime.strptime(h, "%H:%M:%S")
                                fin = (d + timedelta(hours=1)).strftime("%H:%M:%S")
                                horas_procesadas.append({"inicio": h, "fin": fin})
                             except:
                                 pass
                         return horas_procesadas
                    
                    return raw_horas if raw_horas else self.horas_default
            except Exception as e:
                print(f"Error cargando config: {e}")
                return self.horas_default
        else:
            self.guardar_horas(self.horas_default)
            return self.horas_default

    def guardar_horas(self, lista_horas):
        """Guarda la lista de horas en el archivo JSON."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({"horas": lista_horas}, f, indent=4)
            self.horas = lista_horas
            return True
        except Exception as e:
            print(f"Error guardando config: {e}")
            return False

    def obtener_horas(self):
        return self.horas
