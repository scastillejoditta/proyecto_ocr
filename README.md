# Proyecto de Reconocimiento Óptico de Caracteres (OCR)

Este proyecto implementa un pipeline de OCR utilizando la librería **PaddleOCR** para extraer texto de imágenes de manera eficiente, con soporte para el idioma español.

## 1. Descripción General
El sistema permite procesar imágenes individuales o carpetas completas, realizando un preprocesamiento interno (vía PaddleOCR) para detectar y reconocer texto con alta precisión. Está optimizado para ejecutarse en entornos locales de manera rápida gracias a la gestión de dependencias con `uv`.

## 2. Requisitos del Sistema
- **Python**: 3.9 o superior.
- **Herramientas**: `uv`.

## 3. Instrucciones de Instalación

Siga estos pasos para configurar el entorno de desarrollo:

### Paso 1: Clonar el repositorio y entrar al directorio
```bash
cd proyecto_ocr
```

### Paso 2: Crear el entorno virtual (usando uv)
```bash
uv venv
source .venv/bin/activate  # En macOS/Linux
# o .venv\Scripts\activate  # En Windows
```

### Paso 3: Instalar dependencias
```bash
uv pip install -r requirements.txt
uv pip install -e .  # Instala el proyecto en modo editable
```

## 4. Instrucciones de Uso

El script `src/inferencia.py` es el punto de entrada principal.

### Procesar una sola imagen
```bash
python src/inferencia.py --imagen ruta/a/tu/imagen.png
```

### Procesar una imagen y guardar el resultado
```bash
python src/inferencia.py --imagen ruta/a/imagen.png --salida resultado.txt
```

### Procesar una carpeta completa de imágenes
```bash
python src/inferencia.py --carpeta ruta/de/carpeta --salida carpeta_resultados
```

## 5. Ejemplo de Entrada y Salida

**Entrada:**
Una imagen que contiene el texto "CAPÍTULO PRIMERO".

**Comando:**
```bash
python src/inferencia.py --imagen image.png
```

**Salida en consola:**
```text
Procesando: image.png

--- TEXTO EXTRAÍDO ---

CAPÍTULO PRIMERO
Llegué a Liverpool el 18 marzo de 1867...
```

## 6. Soluciones Alternativas
Existe una implementación alternativa utilizando **EasyOCR** en la rama `easyocr`.

Para consultar esta solución:
```bash
git checkout easyocr
```
