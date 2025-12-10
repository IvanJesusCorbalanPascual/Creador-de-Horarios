
# --- CONSTANTES ---
# Estilo visual CSS "Green Tonic"
GREEN_TONIC_STYLE = """
/* --- Estilo Base (Fondo General) --- */
QMainWindow, QDialog {
    background-color: #f0f7f4;
}

/* --- Botones Generales (Por defecto) --- */
QPushButton {
    background-color: #2e7d32;
    color: white;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 600;
    border: 1px solid #1b5e20;
}
QPushButton:hover {
    background-color: #43a047;
    border: 1px solid #2e7d32;
}
QPushButton:pressed {
    background-color: #1b5e20;
    padding-top: 10px;
    padding-bottom: 6px;
}

/* --- Botones Superiores (Acciones Principales: Agregar/Editar/Preferencias) --- */
/* AQUI ESTABA EL ERROR: Faltaba añadir #btn_preferencias a la lista */
QPushButton#btn_agregar_modulo, QPushButton#btn_editar_modulo, 
QPushButton#btn_agregar_profe, QPushButton#btn_editar_profe,
QPushButton#btn_preferencias {
    background-color: #f0f7f4; /* O 'white' si prefieres contraste total */
    color: #2e7d32; /* Texto verde */
    border: 2px solid #2e7d32; /* Borde verde más grueso */
    font-size: 14px;
}

/* --- HOVER para Botones Superiores --- */
QPushButton#btn_agregar_modulo:hover, QPushButton#btn_editar_modulo:hover,
QPushButton#btn_agregar_profe:hover, QPushButton#btn_editar_profe:hover,
QPushButton#btn_preferencias:hover {
    border: 3px solid #43a047; /* Un borde un poco más grueso al pasar el ratón */
    background-color: #e8f5e9; /* Un fondo verde muy suave opcional */
}

/* --- ESTADO PRESSED (Al hacer clic) --- */
QPushButton#btn_agregar_modulo:pressed, QPushButton#btn_editar_modulo:pressed,
QPushButton#btn_agregar_profe:pressed, QPushButton#btn_editar_profe:pressed, 
QPushButton#btn_preferencias:pressed {
    background-color: #1b5e20; /* Color oscuro al presionar */
    color: white; /* Texto blanco para que se lea bien */
}

/* --- Botones de Acción Peligrosa (Eliminar/Borrar) --- */
QPushButton#btn_eliminar_modulo, QPushButton#btn_borrar_profe, QPushButton[text="Eliminar este ciclo"] {
    background-color: #ffebee; 
    color: #c62828; 
    border: 2px solid #c62828;
    margin: 5px;
}
QPushButton#btn_eliminar_modulo:hover, QPushButton#btn_borrar_profe:hover, QPushButton[text="Eliminar este ciclo"]:hover {
    border: 3px solid #c62828;
    background-color: #ffcdd2;
}

/* --- Tablas (QTableWidget) --- */
QTableWidget {
    background-color: white;
    alternate-background-color: #f1f8e9; 
    gridline-color: #c8e6c9;
    border: 1px solid #81c784;
    border-radius: 4px;
}
QHeaderView::section {
    background-color: #2e7d32;
    color: white;
    padding: 8px;
    border: none;
    font-weight: bold;
    font-size: 14px;
}
QTableWidget::item {
    padding: 5px;
}
QTableWidget::item:selected {
    background-color: #a5d6a7; 
    color: #1b5e20;
}

/* --- Menú Lateral (Botones de Navegación) --- */
QPushButton#btn_profesores, QPushButton#btn_modulos, QPushButton#btn_horarios {
    background-color: #263238; 
    color: #eceff1;
    text-align: left;
    padding-left: 20px;
    border: none;
    border-radius: 0px;
    font-size: 16px;
    height: 50px;
    margin: 0px;
}
QPushButton#btn_profesores:checked, QPushButton#btn_modulos:checked, QPushButton#btn_horarios:checked {
    background-color: #2e7d32; 
    color: white;
    border-left: 6px solid #aed581; 
    font-weight: bold;
}
QPushButton#btn_profesores:hover, QPushButton#btn_modulos:hover, QPushButton#btn_horarios:hover {
    background-color: #37474f; 
}

/* --- Inputs y Combos --- */
QLineEdit, QComboBox, QSpinBox, QTimeEdit {
    border: 2px solid #a5d6a7; 
    border-radius: 6px;
    padding: 6px;
    background-color: white;
    font-size: 14px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {
    border: 2px solid #2e7d32; 
}

/* --- Títulos y Etiquetas --- */
QLabel {
    color: #263238;
    font-size: 18px; /* Un tamaño base más razonable, títulos aparte */
}
QLabel#label_titulo, QLabel[text^="Modulos de"], QLabel[text^="Tabla de Profesores"], QLabel[text^="Horario de"] { 
    font-size: 22px;
    font-weight: bold;
    color: #1b5e20;
}
"""

# Reemplazando las credenciales reales de Supabase/PostgreSQL en forma de dict
DB_CONFIG = {
    'host': 'tu_host_db',
    'database': 'tu_db_name',
    'user': 'tu_user',
    'password': 'tu_password'
}
