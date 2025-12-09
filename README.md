# 📅 Creador de Horarios - Green Tonic Edition

<div align="center">

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PyQt5](https://img.shields.io/badge/Qt-41CD52?style=for-the-badge&logo=Qt&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)

**Un gestor de cursos educativos robusto y elegante con generación automática de horarios.**

[Características] • [Instalación] • [Configuración] • [Uso]

</div>

---

## 📖 Descripción

**Creador de Horarios** es una aplicación de escritorio desarrollada en **Python** y **PyQt5** diseñada para facilitar la gestión académica de centros educativos. 

Permite administrar ciclos formativos (DAM, DAW, ASIR...), profesores y módulos, asignando restricciones horarias y visualizando la carga lectiva mediante un sistema de colores. Su característica estrella es el **Generador Automático**, capaz de calcular horarios óptimos evitando colisiones, y la capacidad de exportar los resultados finales a formato CSV.

Todo ello envuelto en una interfaz moderna con el estilo visual **"Green Tonic"** 🌿.

## ✨ Características Principales

* **🎨 Interfaz "Green Tonic":** Diseño visual cuidado en tonos verdes, con efectos *hover*, *zoom* en celdas y feedback visual claro.
* **🔄 Gestión de Ciclos:** Crea y elimina ciclos formativos completos de forma dinámica.
* **👨‍🏫 Gestión de Profesores:**
    * Asignación de colores personalizados para fácil identificación visual.
    * Control de horas máximas diarias y semanales.
    * Edición y borrado con validación de integridad referencial.
* **📚 Gestión de Módulos:**
    * Asignación de módulos a profesores específicos.
    * Control de carga horaria (horas/semana y horas/día).
* **⚡ Generador Automático:** Algoritmo inteligente que crea horarios respetando las restricciones de los profesores y evitando choques entre ciclos.
* **📊 Visualización de Horarios:** Grid interactivo que muestra las asignaturas, profesores y colores asignados.
* **💾 Persistencia en la Nube:** Todos los datos se sincronizan en tiempo real con una base de datos **PostgreSQL** alojada en **Supabase**.
* **scv Exportación:** Genera informes detallados en CSV listos para Excel.

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **Interfaz Gráfica:** PyQt5 (Qt Designer + Custom Stylesheets)
* **Base de Datos:** PostgreSQL (vía Supabase)
* **Cliente DB:** `supabase-py`

## 🚀 Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto en tu máquina local:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/tu-usuario/creador-de-horarios.git](https://github.com/tu-usuario/creador-de-horarios.git)
cd creador-de-horarios