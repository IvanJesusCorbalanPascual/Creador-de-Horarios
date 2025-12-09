import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from logica.profesor_manager import ProfesorManager
from modelos.modelos import Profesor

# Mock db config (not used by the singleton db but required by constructor)
DB_CONFIG = {}

def verify_add_profesor():
    print("Verifying 'Add Professor' functionality...")
    manager = ProfesorManager(DB_CONFIG)
    
    # Test Data
    test_name = "Profesor Prueba Script"
    test_color = "#123456"
    
    # Create object
    p = Profesor(None, test_name, test_color, 4, 20)
    
    print(f"Adding professor: {test_name}")
    new_id = manager.add_profesor(p)
    
    if new_id:
        print(f"SUCCESS: Professor added with ID: {new_id}")
        
        # Verify cleaning up (delete)
        print(f"Cleaning up (deleting ID {new_id})...")
        if manager.delete_profesor(new_id):
             print("SUCCESS: Test professor deleted.")
        else:
             print("ERROR: Failed to delete test professor.")
             
    else:
        print("ERROR: Failed to add professor (returned None/False).")

if __name__ == "__main__":
    verify_add_profesor()
