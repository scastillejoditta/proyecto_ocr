from paddleocr import PaddleOCR
from .utils import preprocess_image

class OCRPipeline:
    def __init__(self, lang="en"):
        self.ocr = PaddleOCR(lang=lang)

    def process_image(self, image_path, verbose=False):
        result = self.ocr.ocr(image_path)
        
        if not result or len(result) == 0:
            return ""
        
        ocr_result = result[0]
        
        if 'rec_texts' not in ocr_result:
            return ""
        
        texts = ocr_result['rec_texts']
        scores = ocr_result.get('rec_scores', [])
        polys = ocr_result.get('rec_polys', [])
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Total de líneas detectadas: {len(texts)}")
            print(f"{'='*60}\n")
            
            for i, text in enumerate(texts):
                conf = scores[i] if i < len(scores) else None
                poly = polys[i] if i < len(polys) else None
                
                if conf is not None:
                    print(f"Línea {i + 1}: '{text}' (confianza: {conf:.3f})")
                else:
                    print(f"Línea {i + 1}: '{text}'")
                
                if poly is not None and verbose:
                    print(f"  Posición: {poly}")
        
        return "\n".join(texts)
