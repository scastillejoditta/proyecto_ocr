"""
Pipeline de OCR para procesamiento de páginas de libros antiguos y modernos.
Utiliza EasyOCR para extraer texto de imágenes escaneadas o fotografiadas.

Autor: grupo 6 de la Maestría en Matemáticas aplicadas y ciencias de la computación
Fecha: 2026-02-14
"""

import cv2
import numpy as np
import easyocr
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import json
import logging
from datetime import datetime


class BookOCRPipeline:
    """
    Pipeline completo de OCR para procesamiento de libros antiguos y modernos.
    
    Características:
    - Preprocesamiento adaptativo según tipo de libro
    - Corrección de perspectiva e inclinación
    - Detección y extracción de texto con EasyOCR
    - Métricas de confianza por página
    - Exportación de resultados en múltiples formatos
    
    Attributes:
        languages (list): Lista de idiomas para reconocimiento OCR
        book_type (str): Tipo de libro ('modern' o 'ancient')
        reader (easyocr.Reader): Instancia del lector EasyOCR
        use_gpu (bool): Usar GPU si está disponible
        logger (logging.Logger): Logger para registro de eventos
    """
    
    def __init__(
        self, 
        languages: List[str] = ['es', 'en'],
        book_type: str = 'modern',
        use_gpu: bool = False,
        log_level: int = logging.INFO
    ):
        """
        Inicializar el pipeline de OCR.
        
        Args:
            languages: Lista de códigos de idioma para OCR (ej: ['es', 'en'])
            book_type: 'modern' para libros modernos, 'ancient' para libros antiguos
            use_gpu: True para usar GPU (requiere CUDA), False para CPU
            log_level: Nivel de logging (logging.INFO, logging.DEBUG, etc.)
        """
        self.languages = languages
        self.book_type = book_type
        self.use_gpu = use_gpu
        
        # Configurar logging
        self._setup_logging(log_level)
        
        # Inicializar EasyOCR
        self.logger.info(f"Inicializando EasyOCR con idiomas: {languages}")
        self.logger.info(f"Modo: {'GPU' if use_gpu else 'CPU'}")
        
        try:
            self.reader = easyocr.Reader(
                languages, 
                gpu=use_gpu,
                verbose=False
            )
            self.logger.info("EasyOCR inicializado correctamente")
        except Exception as e:
            self.logger.error(f"Error al inicializar EasyOCR: {str(e)}")
            raise
        
        # Configuraciones específicas por tipo de libro
        self.config = self._get_config_by_type()
        
    def _setup_logging(self, log_level: int):
        """Configurar el sistema de logging."""
        self.logger = logging.getLogger('BookOCRPipeline')
        self.logger.setLevel(log_level)
        
        # Handler para consola
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _get_config_by_type(self) -> Dict:
        """
        Obtener configuración específica según el tipo de libro.
        
        Returns:
            Diccionario con parámetros de configuración
        """
        configs = {
            'modern': {
                'contrast_enhancement': 1.2,
                'denoise_strength': 10,
                'binarization_method': 'otsu',
                'min_text_size': 10,
                'text_threshold': 0.7,
                'low_text': 0.4
            },
            'ancient': {
                'contrast_enhancement': 2.0,
                'denoise_strength': 15,
                'binarization_method': 'adaptive',
                'min_text_size': 8,
                'text_threshold': 0.6,
                'low_text': 0.3
            }
        }
        return configs.get(self.book_type, configs['modern'])
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocesar imagen según el tipo de libro.
        
        Args:
            image: Imagen en formato numpy array (BGR)
            
        Returns:
            Imagen preprocesada
        """
        self.logger.debug("Iniciando preprocesamiento de imagen")
        
        # Convertir a escala de grises
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Mejora de contraste con CLAHE
        clahe = cv2.createCLAHE(
            clipLimit=self.config['contrast_enhancement'], 
            tileGridSize=(8, 8)
        )
        enhanced = clahe.apply(gray)
        
        # Binarización
        if self.config['binarization_method'] == 'otsu':
            _, binary = cv2.threshold(
                enhanced, 0, 255, 
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
        else:  # adaptive
            binary = cv2.adaptiveThreshold(
                enhanced, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11, 2
            )
        
        # Reducción de ruido
        denoised = cv2.fastNlMeansDenoising(
            binary, 
            h=self.config['denoise_strength']
        )
        
        self.logger.debug("Preprocesamiento completado")
        return denoised
    
    def deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Corregir la inclinación de la imagen.
        
        Args:
            image: Imagen en escala de grises
            
        Returns:
            Imagen corregida
        """
        self.logger.debug("Corrigiendo inclinación de imagen")
        
        # Detectar coordenadas de píxeles no vacíos
        coords = np.column_stack(np.where(image > 0))
        
        # Calcular ángulo de inclinación
        angle = cv2.minAreaRect(coords)[-1]
        
        # Ajustar ángulo
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Aplicar rotación
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        self.logger.debug(f"Imagen rotada {angle:.2f} grados")
        return rotated
    
    def remove_borders(self, image: np.ndarray) -> np.ndarray:
        """
        Eliminar bordes negros de escaneo.
        
        Args:
            image: Imagen en escala de grises
            
        Returns:
            Imagen recortada
        """
        self.logger.debug("Eliminando bordes")
        
        # Encontrar contornos
        contours, _ = cv2.findContours(
            image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        if contours:
            # Obtener el contorno más grande
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Recortar con margen pequeño
            margin = 10
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(image.shape[1] - x, w + 2 * margin)
            h = min(image.shape[0] - y, h + 2 * margin)
            
            cropped = image[y:y+h, x:x+w]
            self.logger.debug(f"Imagen recortada: {w}x{h}")
            return cropped
        
        return image
    
    def extract_text_from_image(
        self, 
        image_path: Union[str, Path],
        preprocess: bool = True,
        save_preprocessed: bool = False,
        output_dir: Optional[Union[str, Path]] = None
    ) -> Dict:
        """
        Extraer texto de una imagen de página de libro.
        
        Args:
            image_path: Ruta a la imagen
            preprocess: Aplicar preprocesamiento
            save_preprocessed: Guardar imagen preprocesada
            output_dir: Directorio para guardar imagen preprocesada
            
        Returns:
            Diccionario con texto extraído, confianza y metadatos
        """
        image_path = Path(image_path)
        self.logger.info(f"Procesando imagen: {image_path.name}")
        
        # Leer imagen
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"No se pudo leer la imagen: {image_path}")
        
        # Redimensionar si es muy grande
        height, width = image.shape[:2]
        max_dimension = 2000
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            self.logger.debug(f"Imagen redimensionada a {new_width}x{new_height}")
        
        # Preprocesar
        processed_image = image
        if preprocess:
            processed_image = self.preprocess_image(image)
            processed_image = self.deskew_image(processed_image)
            processed_image = self.remove_borders(processed_image)
            
            # Guardar imagen preprocesada
            if save_preprocessed and output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                preprocessed_path = output_path / f"{image_path.stem}_preprocessed.png"
                cv2.imwrite(str(preprocessed_path), processed_image)
                self.logger.debug(f"Imagen preprocesada guardada en: {preprocessed_path}")
        
        # Ejecutar OCR con EasyOCR
        self.logger.debug("Ejecutando OCR con EasyOCR")
        results = self.reader.readtext(
            processed_image,
            detail=1,
            paragraph=False,
            min_size=self.config['min_text_size'],
            text_threshold=self.config['text_threshold'],
            low_text=self.config['low_text']
        )
        
        # Procesar resultados
        detections = []
        confidences = []
        
        for bbox, text, confidence in results:
            detections.append({
                'text': text,
                'confidence': float(confidence),
                'bbox': bbox
            })
            confidences.append(confidence)
        
        # Ordenar detecciones de arriba a abajo, izquierda a derecha
        detections_sorted = sorted(
            detections, 
            key=lambda x: (x['bbox'][0][1], x['bbox'][0][0])
        )
        
        # Construir texto completo
        full_text = ' '.join([d['text'] for d in detections_sorted])
        
        # Calcular métricas
        avg_confidence = np.mean(confidences) if confidences else 0.0
        word_count = len(full_text.split())
        
        self.logger.info(f"OCR completado: {len(detections)} detecciones, confianza promedio: {avg_confidence:.2%}")
        
        return {
            'image_path': str(image_path),
            'text': full_text,
            'detections': detections_sorted,
            'metrics': {
                'detection_count': len(detections),
                'average_confidence': float(avg_confidence),
                'word_count': word_count,
                'image_dimensions': {
                    'width': width,
                    'height': height
                }
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def process_book(
        self,
        images_dir: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        save_preprocessed: bool = False,
        file_extensions: List[str] = ['jpg', 'jpeg', 'png', 'tif', 'tiff']
    ) -> Dict:
        """
        Procesar un libro completo (múltiples páginas).
        
        Args:
            images_dir: Directorio con imágenes de páginas
            output_dir: Directorio para guardar resultados
            save_preprocessed: Guardar imágenes preprocesadas
            file_extensions: Extensiones de archivo a procesar
            
        Returns:
            Diccionario con resultados completos del libro
        """
        images_path = Path(images_dir)
        self.logger.info(f"Procesando libro desde: {images_path}")
        
        # Encontrar todas las imágenes
        image_files = []
        for ext in file_extensions:
            image_files.extend(images_path.glob(f"*.{ext}"))
            image_files.extend(images_path.glob(f"*.{ext.upper()}"))
        
        image_files = sorted(set(image_files))
        
        if not image_files:
            raise ValueError(f"No se encontraron imágenes en {images_dir}")
        
        self.logger.info(f"Encontradas {len(image_files)} páginas")
        
        # Procesar cada página
        pages = []
        full_text_parts = []
        total_detections = 0
        total_words = 0
        
        for i, img_path in enumerate(image_files, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Procesando página {i}/{len(image_files)}")
            self.logger.info(f"{'='*60}")
            
            try:
                result = self.extract_text_from_image(
                    img_path,
                    preprocess=True,
                    save_preprocessed=save_preprocessed,
                    output_dir=output_dir
                )
                
                page_data = {
                    'page_number': i,
                    'filename': img_path.name,
                    'text': result['text'],
                    'metrics': result['metrics'],
                    'detection_count': result['metrics']['detection_count'],
                    'confidence': result['metrics']['average_confidence']
                }
                
                pages.append(page_data)
                full_text_parts.append(f"\n\n--- PÁGINA {i} ---\n\n{result['text']}")
                
                total_detections += result['metrics']['detection_count']
                total_words += result['metrics']['word_count']
                
                self.logger.info(f"✓ Página {i} procesada exitosamente")
                self.logger.info(f"  Detecciones: {result['metrics']['detection_count']}")
                self.logger.info(f"  Palabras: {result['metrics']['word_count']}")
                self.logger.info(f"  Confianza: {result['metrics']['average_confidence']:.2%}")
                
            except Exception as e:
                self.logger.error(f"✗ Error procesando página {i}: {str(e)}")
                pages.append({
                    'page_number': i,
                    'filename': img_path.name,
                    'error': str(e)
                })
        
        # Compilar resultados finales
        successful_pages = [p for p in pages if 'error' not in p]
        
        results = {
            'book_info': {
                'total_pages': len(image_files),
                'successful_pages': len(successful_pages),
                'failed_pages': len(image_files) - len(successful_pages),
                'processing_date': datetime.now().isoformat(),
                'book_type': self.book_type,
                'languages': self.languages
            },
            'statistics': {
                'total_detections': total_detections,
                'total_words': total_words,
                'average_words_per_page': total_words / len(successful_pages) if successful_pages else 0,
                'average_confidence': np.mean([p['confidence'] for p in successful_pages]) if successful_pages else 0
            },
            'pages': pages,
            'full_text': ''.join(full_text_parts)
        }
        
        # Guardar resultados
        if output_dir:
            self._save_results(results, output_dir)
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info("PROCESAMIENTO COMPLETADO")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Páginas exitosas: {results['book_info']['successful_pages']}/{results['book_info']['total_pages']}")
        self.logger.info(f"Total de palabras: {results['statistics']['total_words']}")
        self.logger.info(f"Confianza promedio: {results['statistics']['average_confidence']:.2%}")
        
        return results
    
    def _save_results(self, results: Dict, output_dir: Union[str, Path]):
        """
        Guardar resultados en archivos.
        
        Args:
            results: Diccionario con resultados
            output_dir: Directorio de salida
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Guardar JSON con metadatos completos
        json_path = output_path / 'results.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Resultados JSON guardados en: {json_path}")
        
        # Guardar texto completo
        text_path = output_path / 'full_text.txt'
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(results['full_text'])
        self.logger.info(f"Texto completo guardado en: {text_path}")
        
        # Guardar resumen
        summary_path = output_path / 'summary.txt'
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("RESUMEN DE PROCESAMIENTO OCR\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Fecha: {results['book_info']['processing_date']}\n")
            f.write(f"Tipo de libro: {results['book_info']['book_type']}\n")
            f.write(f"Idiomas: {', '.join(results['book_info']['languages'])}\n\n")
            f.write(f"Total de páginas: {results['book_info']['total_pages']}\n")
            f.write(f"Páginas exitosas: {results['book_info']['successful_pages']}\n")
            f.write(f"Páginas con errores: {results['book_info']['failed_pages']}\n\n")
            f.write(f"Total de palabras: {results['statistics']['total_words']}\n")
            f.write(f"Promedio palabras/página: {results['statistics']['average_words_per_page']:.1f}\n")
            f.write(f"Confianza promedio: {results['statistics']['average_confidence']:.2%}\n\n")
            f.write("=" * 60 + "\n\n")
            f.write("DETALLE POR PÁGINA:\n\n")
            
            for page in results['pages']:
                if 'error' not in page:
                    f.write(f"Página {page['page_number']}: ")
                    f.write(f"{page['metrics']['word_count']} palabras, ")
                    f.write(f"confianza {page['confidence']:.2%}\n")
                else:
                    f.write(f"Página {page['page_number']}: ERROR - {page['error']}\n")
        
        self.logger.info(f"Resumen guardado en: {summary_path}")


if __name__ == "__main__":
    # Ejemplo de uso básico
    print("Iniciando pipeline de OCR...")
    
    # Crear instancia del pipeline para libro moderno
    pipeline = BookOCRPipeline(
        languages=['es', 'en'],
        book_type='modern',
        use_gpu=False,
        log_level=logging.INFO
    )
    
    # Procesar una sola imagen
    # result = pipeline.extract_text_from_image('page_001.jpg')
    # print(f"\nTexto extraído:\n{result['text']}")
    
    # Procesar libro completo
    # results = pipeline.process_book(
    #     images_dir='./book_images',
    #     output_dir='./output',
    #     save_preprocessed=True
    # )
    
    print("\nPipeline listo para usar.")
    print("Descomenta las líneas de ejemplo para procesar imágenes.")