# Pipeline OCR para Libros Antiguos y Modernos

Sistema de reconocimiento óptico de caracteres (OCR) diseñado para procesar páginas de libros escaneadas o fotografiadas, tanto antiguos como modernos. Utiliza **EasyOCR** para extraer texto con alta precisión, incluyendo preprocesamiento adaptativo de imágenes.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Uso](#uso)
  - [Script de inferencia](#script-de-inferencia)
- [Configuración](#configuración)
- [Preprocesamiento de Imágenes](#preprocesamiento-de-imágenes)
- [Salidas Generadas](#salidas-generadas)
- [Solución de Problemas](#solución-de-problemas)
- [Autores](#autores)

## ✨ Características

- ✅ **Soporte multi-idioma**: Español, inglés, y más de 80 idiomas
- ✅ **Preprocesamiento adaptativo**: Configuración automática según tipo de libro (moderno/antiguo)
- ✅ **Corrección automática**: 
  - Corrección de inclinación (deskew)
  - Eliminación de bordes de escaneo
  - Mejora de contraste adaptativa
  - Reducción de ruido
- ✅ **Procesamiento por lotes**: Procesar libros completos automáticamente
- ✅ **Métricas de calidad**: Confianza promedio, conteo de palabras, detecciones
- ✅ **Múltiples formatos de salida**: JSON, TXT, resumen estadístico
- ✅ **Logging detallado**: Seguimiento completo del proceso
- ✅ **Imágenes de debug**: Guardar imágenes preprocesadas para validación

## 🔧 Requisitos

### Software
- Python 3.7 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

### Hardware
- **CPU**: Procesador de 2+ núcleos (recomendado)
- **RAM**: Mínimo 4GB (8GB recomendado para libros grandes)
- **GPU**: Opcional, pero mejora significativamente el rendimiento
- **Espacio**: ~2GB para modelos de EasyOCR + espacio para datos

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/scastillejoditta/proyecto_ocr.git
cd proyecto_ocr
```

### 2. Crear ambiente virtual

**Windows (Git Bash):**
```bash
python -m venv venv
source venv/Scripts/activate
```

**Windows (CMD):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install easyocr opencv-python numpy pillow
```

### 4. Verificar instalación

```bash
python -c "import easyocr; print('✓ Instalación exitosa')"
```

**Nota**: La primera vez que ejecutes EasyOCR, descargará los modelos automáticamente (~100-200MB por idioma).

## 📁 Estructura del Proyecto

```
proyecto_ocr/
├── README.md                    # Este archivo
├── .gitignore                   # Archivos ignorados por Git
│
├── src/                         # Código fuente
│   ├── ocr_pipeline.py         # Clase principal del pipeline OCR
│   ├── inferencia.py           # Script de pruebas e inferencia
│   └── utils.py                # Utilidades auxiliares (opcional)
│
├── test_data/                   # Datos de prueba (no incluidos en Git)
│   ├── single_page/            # Imágenes individuales para pruebas
│   └── book_images/            # Múltiples páginas de un libro
│
├── output/                      # Resultados generados (no incluidos en Git)
│   ├── single_test/            # Resultados de páginas individuales
│   └── book_test/              # Resultados de libros completos
│
└── venv/                        # Ambiente virtual (no incluido en Git)
```

## 🚀 Uso

### Script de inferencia

El proyecto incluye un script interactivo para pruebas rápidas:

```bash
# Activar ambiente virtual
source venv/Scripts/activate  # Git Bash
# O: venv\Scripts\activate    # Windows CMD

# Ejecutar script de inferencia
python src/inferencia.py

# Elegir una opción:
# 1. Probar con una sola imagen
# 2. Probar con libro completo
# 3. Mostrar estructura del proyecto

# Elegir el tipo de libro al que pertenecen las imágenes, corresponde al hiperparámetro book_type:
# 1. Libro moderno (impreso reciente, buen estado)
# 2. Libro antiguo (deteriorado, manchas, papel amarillento)

```

## ⚙️ Configuración

### Parámetros del Pipeline

| Parámetro | Descripción | Valores | Default |
|-----------|-------------|---------|---------|
| `languages` | Idiomas para OCR | Lista: `['es', 'en', 'fr', ...]` | `['es', 'en']` |
| `book_type` | Tipo de libro | `'modern'` o `'ancient'` | Lo ingresa el usuario |
| `use_gpu` | Usar GPU para aceleración | `True` o `False` | `False` |
| `log_level` | Nivel de logging | `logging.DEBUG`, `INFO`, `WARNING` | `logging.INFO` |

### Configuraciones específicas por tipo

#### Libros Modernos (`book_type='modern'`)
- Contraste moderado
- Binarización Otsu
- Denoise ligero
- Mejor para: libros impresos recientes, buen estado

#### Libros Antiguos (`book_type='ancient'`)
- Contraste agresivo (CLAHE)
- Binarización adaptativa
- Denoise intenso
- Morfología para limpieza
- Mejor para: libros deteriorados, manchas, papel amarillento

### Idiomas soportados

EasyOCR soporta más de 80 idiomas. Ejemplos:

```python
# Español
languages=['es']

# Español e inglés
languages=['es', 'en']

# Francés
languages=['fr']

# Alemán
languages=['de']

# Ver lista completa en: https://www.jaided.ai/easyocr/
```

## 🖼️ Preprocesamiento de Imágenes

El pipeline aplica las siguientes técnicas:

1. **Redimensionamiento**: Optimiza imágenes muy grandes (>2000px)
2. **Conversión a escala de grises**: Facilita el procesamiento
3. **Mejora de contraste**: CLAHE adaptativo
4. **Binarización**: Otsu (moderno) o Adaptativa (antiguo)
5. **Reducción de ruido**: Fast Non-Local Means Denoising
6. **Corrección de inclinación**: Rotación automática
7. **Eliminación de bordes**: Recorte de márgenes de escaneo

## 📊 Salidas Generadas

### Para una sola página:

```
output/single_test/
├── page_001_preprocessed.png   # Imagen preprocesada (opcional)
└── ...
```

### Para libro completo:

```
output/book_test/
├── results.json                # Metadatos completos en JSON
├── full_text.txt              # Texto completo extraído
├── summary.txt                # Resumen estadístico
└── page_001_preprocessed.png # Imágenes preprocesadas (opcional)
```

### Contenido de `results.json`:

```json
{
  "book_info": {
    "total_pages": 10,
    "successful_pages": 10,
    "failed_pages": 0,
    "processing_date": "2026-02-14T12:35:23",
    "book_type": "modern",
    "languages": ["es", "en"]
  },
  "statistics": {
    "total_detections": 850,
    "total_words": 2340,
    "average_words_per_page": 234.0,
    "average_confidence": 0.92
  },
  "pages": [
    {
      "page_number": 1,
      "filename": "page_001.jpg",
      "text": "Texto extraído...",
      "metrics": {
        "detection_count": 85,
        "word_count": 234,
        "average_confidence": 0.93
      }
    }
  ]
}
```

## 🐛 Solución de Problemas

### Error: "No se pudo leer la imagen"

**Causa**: Ruta incorrecta, archivo corrupto o con caracteres especiales en su nombre.

**Solución**:
1. Cambiar el nombre del archivo y volver a correr inferencia.py

2. Si el error persiste, revisar el archivo:

```python
from pathlib import Path
import cv2

# Verificar que existe
image_path = Path('test_data/single_page/imagen.jpg')
print(f"Existe: {image_path.exists()}")

# Probar lectura
img = cv2.imread(str(image_path))
if img is None:
    print("Archivo corrupto o formato no soportado")
```

### Error: "No module named 'easyocr'"

**Causa**: Ambiente virtual no activado o EasyOCR no instalado

**Solución**:
```bash
# Activar ambiente
source venv/Scripts/activate  # Git Bash
# venv\Scripts\activate        # Windows CMD

# Instalar EasyOCR
pip install easyocr

# Verificar
pip show easyocr
```

### Error: Memory Error / Out of Memory

**Causa**: Imágenes muy grandes o muchas páginas

**Solución**:
1. Procesar en lotes más pequeños
2. Reducir resolución de imágenes antes de procesar
3. Desactivar `save_preprocessed=False`
4. Aumentar RAM o usar GPU

### Baja confianza en resultados (<70%)

**Solución**:
1. Cambiar `book_type` de `'modern'` a `'ancient'` o viceversa
2. Verificar imagen preprocesada
3. Mejorar calidad de imagen fuente (mayor resolución, mejor iluminación)
4. Ajustar manualmente parámetros de preprocesamiento

### Primera ejecución muy lenta

**Causa**: EasyOCR descargando modelos

**Solución**: 
- Es normal la primera vez
- Los modelos se guardan en `~/.EasyOCR/`
- Ejecuciones posteriores serán mucho más rápidas

## 👥 Autores

- **Sara Castillejo** - *Desarrollo inicial* - [scastillejoditta](https://github.com/scastillejoditta)
- **Stefany Mojica** - *Desarrollo inicial* - [stefymojica](https://github.com/stefymojica)
- **Alexander Pineda** - *Desarrollo inicial* - [alexpineda](https://github.com/tu-usuario)

## 📧 Contacto

Para preguntas o sugerencias, contactar a: scastillejo@urosario.edu.co

---

**Proyecto desarrollado como parte de ML Aplicado - MACC 2026** proyecto_ocr
Sistema de Reconocimiento Óptico de Caracteres (OCR) capaz de ex- traer texto desde imágenes de páginas de libros.
