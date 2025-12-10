import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'src'))

from modelos.modelos import Profesor

def verify_fix():
    print("Verifying Profesor class fix...")
    try:
        # Intenta crear Profesor
        p = Profesor(1, "Test", "#FFFFFF", 5, 25)
        print(f"Profesor created successfully: {p.nombre}")
        
        # Verifica atributos
        if hasattr(p, 'color_hex'):
            print(f"Attribute 'color_hex' found: {p.color_hex}")
        else:
            print("ERROR: Attribute 'color_hex' NOT found!")
            
        if hasattr(p, 'modulos'):
            print("Attribute 'modulos' found.")
        else:
            print("ERROR: Attribute 'modulos' NOT found!")
            
        if hasattr(p, 'preferencias'):
            print("Attribute 'preferencias' found.")
        else:
            print("ERROR: Attribute 'preferencias' NOT found!")
            
    except TypeError as e:
        print(f"ERROR: Failed to create Profesor. {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error. {e}")

if __name__ == "__main__":
    verify_fix()
