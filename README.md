# API de Monitoreo de Sensores y Análisis de Bitácoras

Este proyecto de FastAPI proporciona una API para interactuar con datos de sensores y realizar análisis de bitácoras utilizando modelos de machine learning y procesamiento de lenguaje natural (PLN).

## Descripción General

La API permite:

- **Obtener datos históricos de diversos sensores**: Corriente, presión de agua, salida de agua, generación de gas, temperatura ambiental, temperaturas internas de la bomba, vibración axial y voltaje de barra. Se devuelven los últimos 40 registros de cada tipo de sensor.
- **Realizar predicciones sobre los valores de los sensores**: Utiliza modelos de machine learning pre-entrenados para clasificar los valores de los sensores como "Normal" o "Anomalía" y actualiza la clasificación en la base de datos.
- **Analizar bitácoras de operación**: Emplea modelos de lenguaje grande (LLMs) a través de Langchain para analizar bitácoras textuales, identificar posibles fallas relacionadas con las bombas HRSG y generar alertas o avisos.

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y de alto rendimiento para construir APIs con Python.
- **SQLAlchemy**: Toolkit SQL y ORM para interactuar con la base de datos.
- **Joblib**: Biblioteca para la serialización eficiente de objetos Python, utilizada para cargar los modelos de machine learning.
- **Pandas**: Biblioteca para el análisis y manipulación de datos, utilizada para la entrada de los modelos de predicción.
- **Langchain**: Framework para desarrollar aplicaciones impulsadas por modelos de lenguaje.
- **Modelos de Machine Learning (scikit-learn)**: Modelos pre-entrenados (guardados con Joblib) para la clasificación de datos de sensores.
- **Base de Datos (Especificar la base de datos utilizada)**: La API interactúa con una base de datos para almacenar y recuperar datos de sensores y bitácoras.

## Requisitos

Asegúrate de tener Python 3.7+ instalado.

## Instalación

1. **Clona el repositorio (si aplica):**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <NOMBRE_DEL_PROYECTO>

## Instalación
### Prerrequisitos
- Python 3.10 o superior
- pip instalado
- Virtualenv (opcional pero recomendado)

### Pasos de Instalación
1. Clonar el repositorio:
   ```sh
   git clone https://github.com/tu_usuario/tu_repositorio.git
   cd tu_repositorio
   ```
2. Crear y activar un entorno virtual (opcional):
   ```sh
   python -m venv env
   source env/bin/activate  # En Windows: env\Scripts\activate
   ```
3. Instalar las dependencias:
   ```sh
   pip install -r requirements.txt
   ```
4. Configurar variables de entorno:
   ```sh
   cp .env.example .env
   # Edita el archivo .env con los valores necesarios
   ```
5. Ejecutar la aplicación:
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```



## Contribución
1. Hacer un fork del repositorio
2. Crear una nueva rama (`feature/nueva_funcionalidad`)
3. Hacer commit de los cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Subir la rama (`git push origin feature/nueva_funcionalidad`)
5. Abrir un Pull Request

## Licencia
Este proyecto está bajo la licencia **MIT**.

