"""
Script de inferencia para el pipeline OCR
Maneja correctamente las rutas en Windows
"""
from ocr_pipeline import BookOCRPipeline
from pathlib import Path
import logging
import sys

# Obtener rutas del proyecto de forma compatible con Windows
SCRIPT_DIR = Path(__file__).parent.resolve()  # src/
PROJECT_ROOT = SCRIPT_DIR.parent.resolve()    # raíz del proyecto

# Directorios de datos
TEST_DATA_DIR = PROJECT_ROOT / 'test_data'
SINGLE_PAGE_DIR = TEST_DATA_DIR / 'single_page'
BOOK_IMAGES_DIR = TEST_DATA_DIR / 'book_images'
OUTPUT_DIR = PROJECT_ROOT / 'output'

def ask_book_type():
    """Preguntar al usuario el tipo de libro"""
    print("\n¿Qué tipo de imagen o libro vas a procesar?")
    print("1. Libro moderno (impreso reciente, buen estado)")
    print("2. Libro antiguo (deteriorado, manchas, papel amarillento)")
    
    while True:
        choice = input("\nSelecciona una opción (1 o 2): ").strip()
        
        if choice == '1':
            return 'modern'
        elif choice == '2':
            return 'ancient'
        else:
            print("❌ Opción inválida. Por favor ingresa 1 o 2.")

def test_single_image():
    """Probar con una sola imagen"""
    print("\n" + "="*60)
    print("PRUEBA: Procesando una sola imagen")
    print("="*60)
    
    # Preguntar tipo de libro
    book_type = ask_book_type()
    print(f"✓ Tipo seleccionado: {book_type}")
    
    # Verificar que existe la carpeta
    if not SINGLE_PAGE_DIR.exists():
        print(f"❌ No existe la carpeta: {SINGLE_PAGE_DIR}")
        SINGLE_PAGE_DIR.mkdir(parents=True, exist_ok=True)
        print("✓ Carpeta creada. Por favor, agrega imágenes y ejecuta de nuevo.")
        return None
    
    # Buscar la primera imagen disponible
    image_files = list(SINGLE_PAGE_DIR.glob("*.jpg")) + \
                  list(SINGLE_PAGE_DIR.glob("*.jpeg")) + \
                  list(SINGLE_PAGE_DIR.glob("*.png")) + \
                  list(SINGLE_PAGE_DIR.glob("*.tif"))
    
    if not image_files:
        print(f"❌ No se encontraron imágenes en: {SINGLE_PAGE_DIR}")
        print("Formatos soportados: .jpg, .jpeg, .png, .tif")
        return None
    
    # Usar la primera imagen encontrada
    image_path = image_files[0]
    print(f"📄 Procesando imagen: {image_path.name}")
    print(f"📂 Ruta completa: {image_path}")
    
    # Verificar que la imagen existe
    if not image_path.exists():
        print(f"❌ El archivo no existe: {image_path}")
        return None
    
    # Crear pipeline según el tipo de libro
    print("\nInicializando pipeline OCR...")
    pipeline = BookOCRPipeline(
        languages=['es', 'en'],
        book_type=book_type,
        use_gpu=False,
        log_level=logging.INFO
    )
    
    # Crear directorio de salida
    output_path = OUTPUT_DIR / 'single_test'
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        # Procesar imagen - IMPORTANTE: convertir Path a string
        result = pipeline.extract_text_from_image(
            image_path=str(image_path),  # Convertir a string
            preprocess=True,
            save_preprocessed=True,
            output_dir=str(output_path)  # Convertir a string
        )
    # Mostrar resultados
        print("\n" + "="*60)
        print("RESULTADOS")
        print("="*60)
        print("\n--- TEXTO EXTRAÍDO ---")
        print(result['text'])
        print("\n--- MÉTRICAS ---")
        print(f"✓ Detecciones: {result['metrics']['detection_count']}")
        print(f"✓ Palabras: {result['metrics']['word_count']}")
        print(f"✓ Confianza promedio: {result['metrics']['average_confidence']:.2%}")
        print(f"\n📁 Resultados guardados en: {output_path}")
        print(f"   - Imagen preprocesada: {image_path.stem}_preprocessed.png")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error al procesar la imagen: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_multiple_pages():
    """Probar con múltiples páginas (libro completo)"""
    print("\n" + "="*60)
    print("PRUEBA: Procesando libro completo")
    print("="*60)
    
    # Verificar que existe la carpeta
    if not BOOK_IMAGES_DIR.exists():
        print(f"❌ No existe la carpeta: {BOOK_IMAGES_DIR}")
        BOOK_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        print("✓ Carpeta creada. Por favor, agrega imágenes y ejecuta de nuevo.")
        return None
    
    # Contar imágenes
    image_files = list(BOOK_IMAGES_DIR.glob("*.jpg")) + \
                  list(BOOK_IMAGES_DIR.glob("*.jpeg")) + \
                  list(BOOK_IMAGES_DIR.glob("*.png")) + \
                  list(BOOK_IMAGES_DIR.glob("*.tif"))
    
    if not image_files:
        print(f"❌ No se encontraron imágenes en: {BOOK_IMAGES_DIR}")
        return None
    
    print(f"📚 Encontradas {len(image_files)} páginas")
    
    # Crear pipeline
    print("\nInicializando pipeline OCR...")
    pipeline = BookOCRPipeline(
        languages=['es', 'en'],
        book_type='modern',
        use_gpu=False,
        log_level=logging.INFO
    )
    
    # Crear directorio de salida
    output_path = OUTPUT_DIR / 'book_test'
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Procesar libro - IMPORTANTE: convertir Path a string
        results = pipeline.process_book(
            images_dir=str(BOOK_IMAGES_DIR),
            output_dir=str(output_path),
            save_preprocessed=True
        )
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("RESUMEN FINAL")
        print("="*60)
        print(f"✓ Páginas procesadas: {results['book_info']['successful_pages']}/{results['book_info']['total_pages']}")
        print(f"✓ Total palabras: {results['statistics']['total_words']}")
        print(f"✓ Promedio palabras/página: {results['statistics']['average_words_per_page']:.1f}")
        print(f"✓ Confianza promedio: {results['statistics']['average_confidence']:.2%}")
        print(f"\n📁 Resultados guardados en: {output_path}")
        print(f"   - results.json")
        print(f"   - full_text.txt")
        print(f"   - summary.txt")
        
        # Mostrar primeras líneas del texto
        print("\n--- PRIMERAS 500 CARACTERES ---")
        print(results['full_text'][:500])
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error al procesar el libro: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def show_project_structure():
    """Mostrar estructura del proyecto"""
    print("\n" + "="*60)
    print("ESTRUCTURA DEL PROYECTO")
    print("="*60)
    print(f"📁 Raíz del proyecto: {PROJECT_ROOT}")
    print(f"📁 Carpeta src: {SCRIPT_DIR}")
    print(f"📁 Test data: {TEST_DATA_DIR}")
    
    # Verificar carpetas
    single_exists = SINGLE_PAGE_DIR.exists()
    book_exists = BOOK_IMAGES_DIR.exists()
    output_exists = OUTPUT_DIR.exists()
    
    print(f"   └─ Single page: {SINGLE_PAGE_DIR}")
    print(f"      {'✓ Existe' if single_exists else '✗ No existe'}")
    
    if single_exists:
        images = list(SINGLE_PAGE_DIR.glob("*.*"))
        print(f"      Archivos: {len(images)}")
        for img in images[:3]:  # Mostrar primeros 3
            print(f"         - {img.name}")
        if len(images) > 3:
            print(f"         ... y {len(images) - 3} más")
    
    print(f"\n   └─ Book images: {BOOK_IMAGES_DIR}")
    print(f"      {'✓ Existe' if book_exists else '✗ No existe'}")
    
    if book_exists:
        images = list(BOOK_IMAGES_DIR.glob("*.*"))
        print(f"      Archivos: {len(images)}")
    
    print(f"\n📁 Output: {OUTPUT_DIR}")
    print(f"   {'✓ Existe' if output_exists else '✗ No existe'}")
    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PIPELINE OCR - MENÚ DE PRUEBAS")
    print("="*60)
    
    # Mostrar estructura
    show_project_structure()
    
    # Menú de opciones
    print("\nSelecciona una opción:")
    print("1. Probar con una sola imagen")
    print("2. Probar con libro completo (múltiples páginas)")
    print("3. Mostrar estructura del proyecto")
    print("0. Salir")
    
    try:
        opcion = input("\nOpción: ").strip()
        
        if opcion == '1':
            result = test_single_image()
            if result:
                print("\n✓ ¡Prueba completada exitosamente!")
            else:
                print("\n✗ La prueba no se completó")
                
        elif opcion == '2':
            result = test_multiple_pages()
            if result:
                print("\n✓ ¡Prueba completada exitosamente!")
            else:
                print("\n✗ La prueba no se completó")
                
        elif opcion == '3':
            show_project_structure()
            
        elif opcion == '0':
            print("\n👋 ¡Hasta luego!")
            
        else:
            print("\n❌ Opción no válida")
            
    except KeyboardInterrupt:
        print("\n\n👋 Interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)