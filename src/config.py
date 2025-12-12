# --- CONSTANTES ---
# Estilo visual CSS "Green Tonic"
GREEN_TONIC_STYLE = """
QMainWindow, QDialog {
    background-color: white;
}

/* --- Botones Generales (Azul Corporativo) --- */
QPushButton {
    background-color: #1565C0; /* Azul fuerte profesional */
    color: white;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 600;
    border: 1px solid #0D47A1; /* Borde azul oscuro */
}
QPushButton:hover {
    background-color: #1976D2; /* Azul un poco más claro */
    border: 1px solid #1565C0;
}
QPushButton:pressed {
    background-color: #0D47A1; /* Azul muy oscuro al pulsar */
    padding-top: 10px;
    padding-bottom: 6px;
}

QPushButton#btn_agregar_modulo, QPushButton#btn_agregar_profe, QPushButton#btn_exportar_csv {
    background-color: #F1F8E9; /* Fondo verde muy pálido */
    color: #2E7D32;            /* Texto verde fuerte */
    border: 2px solid #2E7D32; /* Borde verde fuerte */
    font-size: 14px;
}

/* HOVER (Verde) */
QPushButton#btn_agregar_modulo:hover, QPushButton#btn_agregar_profe:hover,
QPushButton#btn_exportar_csv:hover {
    border: 3px solid #43A047; 
    background-color: #DCEDC8; /* Verde un poco más intenso al pasar el ratón */
}

/* PRESSED (Verde) */
QPushButton#btn_agregar_modulo:pressed, QPushButton#btn_agregar_profe:pressed,
QPushButton#btn_exportar_csv:pressed {
    background-color: #1B5E20; /* Verde oscuro sólido al hacer clic */
    
}

/* --- Botones Superiores (Acciones Principales: Agregar/Editar) --- */
QPushButton#btn_editar_modulo, QPushButton#btn_editar_profe,
QPushButton#btn_preferencias, QPushButton#btn_generar_auto {
    background-color: #F5F9FF; /* Fondo azulado muy pálido */
    color: #1565C0;            /* Texto azul */
    border: 2px solid #1565C0; /* Borde azul */
    font-size: 14px;
}

/* --- HOVER para Botones Superiores --- */
QPushButton#btn_editar_modulo:hover, QPushButton#btn_editar_profe:hover,
QPushButton#btn_preferencias:hover, QPushButton#btn_generar_auto:hover {
    border: 3px solid #1976D2; 
    background-color: #E3F2FD; /* Fondo azul cielo suave */
}

/* --- ESTADO PRESSED --- */
QPushButton#btn_editar_modulo:pressed, QPushButton#btn_editar_profe:pressed,
QPushButton#btn_preferencias:pressed, QPushButton#btn_generar_auto:pressed {
    background-color: #0D47A1; /* Azul oscuro sólido */
    
}

/* --- Botones de Acción Peligrosa (SE MANTIENEN ROJOS POR SEGURIDAD) --- */
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
    background-color: #c3e0f7;
    alternate-background-color: #F0F7FF; /* Filas alternas azul muy suave */
    gridline-color: #99A9C8;             /* Líneas de rejilla azul claro */
    border: 1px solid #90CAF9;           /* Borde general azul suave */
    border-radius: 4px;
}
QTableWidget::item:hover {
    background-color: #BBDEFB; /* Al pasar el ratón: Azul cielo */
    color: #0D47A1;            /* Texto azul oscuro */
}
QHeaderView::section {
    background-color: #1565C0; /* Cabecera Azul Corporativo */
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
    background-color: #64B5F6; /* Selección: Azul vibrante */
    color: #000000;
}

/* --- Menú Lateral (Sidebar) --- */
QPushButton#btn_profesores, QPushButton#btn_modulos, QPushButton#btn_horarios {
    background-color: #263238; /* Fondo oscuro (Blue Grey) se ve muy bien con azul */
    color: #eceff1;
    text-align: left;
    padding-left: 20px;
    border: none;
    border-radius: 0px;
    font-size: 22px;
    height: 50px;
    margin: 0px;
}
QPushButton#btn_profesores:checked, QPushButton#btn_modulos:checked, QPushButton#btn_horarios:checked {
    background-color: #1565C0; /* ACTIVO: Azul Corporativo */
    border-left: 6px solid #42A5F5; /* Línea de acento azul claro */
    font-weight: bold;
}
QPushButton#btn_profesores:hover, QPushButton#btn_modulos:hover, QPushButton#btn_horarios:hover {
    background-color: #37474f; 
}

/* --- Inputs y Combos --- */
QLineEdit, QComboBox, QSpinBox, QTimeEdit {
    border: 2px solid #90CAF9; /* Borde azul suave por defecto */
    border-radius: 6px;
    padding: 6px;
    background-color: white;
    font-size: 14px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {
    border: 2px solid #1565C0; /* Borde azul fuerte al escribir */
}

/* --- Títulos y Etiquetas --- */
QLabel#menu_principal {
    color: #263238;
    font-size: 26px;
}
QLabel#label_titulo, QLabel[text^="Modulos de"], QLabel[text^="Tabla de Profesores"], QLabel[text^="Horario de"] { 
    font-size: 22px;
    font-weight: bold;
    color: #0D47A1; /* Títulos en azul oscuro elegante */
}
"""
# Reemplazando las credenciales reales de Supabase/PostgreSQL en forma de dict
DB_CONFIG = {
    'host': 'tu_host_db',
    'database': 'tu_db_name',
    'user': 'tu_user',
    'password': 'tu_password'
}
