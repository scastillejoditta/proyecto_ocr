import sys
import os
import argparse
from .ocr_pipeline import OCRPipeline

def process_single_image(pipeline, image_path, output_path=None, verbose=False):
    if not os.path.exists(image_path):
        print(f"Error: La imagen {image_path} no existe.")
        return

    print(f"Procesando: {image_path}")
    text = pipeline.process_image(image_path, verbose=verbose)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Resultado guardado en: {output_path}")
    else:
        print("\n--- TEXTO EXTRAÍDO ---\n")
        print(text)
        print("\n" + "="*30 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Aplicar OCR sobre imágenes o carpetas.")
    parser.add_argument("--imagen", type=str, help="Ruta de una imagen individual.")
    parser.add_argument("--carpeta", type=str, help="Ruta de una carpeta de imágenes.")
    parser.add_argument("--salida", type=str, help="Archivo .txt para guardar el resultado (solo para imagen individual) o carpeta de salida.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostrar detalles de confianza y posición.")
    parser.add_argument("--lang", type=str, default="en", help="Idioma para el OCR (default: en).")

    args = parser.parse_args()

    if not args.imagen and not args.carpeta:
        parser.print_help()
        print("\nError: Debe especificar --imagen o --carpeta")
        return

    pipeline = OCRPipeline(lang=args.lang)

    if args.imagen:
        process_single_image(pipeline, args.imagen, args.salida, args.verbose)
    
    elif args.carpeta:
        if not os.path.isdir(args.carpeta):
            print(f"Error: {args.carpeta} no es un directorio válido.")
            return
        
        output_dir = args.salida if args.salida else "outputs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Creada carpeta de salida: {output_dir}")

        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
        files = [f for f in os.listdir(args.carpeta) if f.lower().endswith(image_extensions)]
        
        if not files:
            print(f"No se encontraron imágenes en {args.carpeta}")
            return

        print(f"Encontradas {len(files)} imágenes en {args.carpeta}")
        for filename in files:
            image_path = os.path.join(args.carpeta, filename)
            output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.txt")
            process_single_image(pipeline, image_path, output_file, args.verbose)

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    main()

