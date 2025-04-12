from ultralytics import YOLO
from pathlib import Path
import shutil
import os
import time
import logging
import gc
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

# Global variables
_model = None
_script_dir = Path(os.path.dirname(os.path.abspath(__file__)))

def clear_gpu_memory():
    """Clear GPU memory if available and working"""
    try:
        if torch.cuda.is_available() and torch.cuda.device_count() > 0:
            torch.cuda.empty_cache()
            gc.collect()
    except Exception as e:
        logging.warning(f"Error clearing GPU memory: {str(e)}")

def load_model():
    """Load and cache the YOLO model"""
    global _model
    if _model is None:
        # Clear any existing cached data
        clear_gpu_memory()

        model_path = _script_dir / 'best.pt'
        
        if not model_path.exists():
            error_msg = f"Model not found at {model_path}"
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        logging.info(f"Loading model from: {model_path}")
        _model = YOLO(str(model_path))
        logging.info("Model loaded and cached successfully")
    return _model

def predict_single_image(image_path):
    # Get or load cached model
    try:
        model = load_model()
    except Exception as e:
        logging.error(f"Failed to load model: {str(e)}")
        raise
    
    # Convert string to Path object
    img_path = Path(image_path)
    
    if not img_path.exists():
        error_msg = f"Image not found at {image_path}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    # Setup output directory
    logging.info(f"Processing image: {img_path.name}")
    runs_dir = _script_dir / 'runs'
    detect_dir = runs_dir / 'detect'
    predict_dir = detect_dir / 'predict'

    # Create output directories
    predict_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Using output directory: {predict_dir}")
    
    try:
        # Prepare output path
        result_path = predict_dir / img_path.name

        # Force CPU mode for consistent behavior
        logging.info("Using CPU for inference")
        torch.set_num_threads(4)  # Limit CPU threads for stability

        # Run inference with optimized settings
        logging.info("Starting inference with YOLO model...")
        results = model.predict(
            source=str(img_path),
            conf=0.25,           # Confidence threshold
            iou=0.45,           # Lower IoU threshold for faster processing
            line_width=2,       # Thinner lines
            boxes=True,         # Draw boxes
            save_txt=False,     # Don't save txt files
            save=True,          # Save results
            save_conf=True,     # Save confidence scores
            imgsz=384,         # Even smaller image size for faster CPU processing
            max_det=5,         # Limit max detections
            project=str(detect_dir),
            name='predict',
            exist_ok=True,
            device='cpu',      # Force CPU
            retina_masks=False, # Disable retina masks for speed
            half=False,        # No FP16 on CPU
            verbose=False      # Reduce output
        )

        # Clear any partial results
        if result_path.exists():
            result_path.unlink()

        # Save result with explicit path
        try:
            results[0].save(filename=str(result_path))
            logging.info(f"Manually saved result to {result_path}")
        except Exception as e:
            logging.error(f"Error saving result: {str(e)}")
            if result_path.exists():
                result_path.unlink()  # Remove partial file if it exists
            raise
        logging.info("Inference completed")
        
        # Verify the saved image with shorter retry times
        saved_img = predict_dir / img_path.name
        max_retries = 5
        retry_delay = 0.2  # seconds
        
        for attempt in range(max_retries):
            if saved_img.is_file():
                try:
                    # Try to open the file to verify it's readable
                    with open(saved_img, 'rb') as f:
                        f.read(1)
                    logging.info(f"Detection image saved and verified at: {saved_img}")
                    break
                except (IOError, OSError) as e:
                    logging.warning(f"Attempt {attempt + 1}: File not ready yet - {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    error_msg = f"Failed to verify saved image at {saved_img}"
                    logging.error(error_msg)
                    raise RuntimeError(error_msg)
            else:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                error_msg = f"Failed to save processed image at {saved_img}"
                logging.error(error_msg)
                raise RuntimeError(error_msg)
        
        # Print detection results
        for r in results:
            boxes = r.boxes
            num_detections = len(boxes)
            logging.info(f"Found {num_detections} tumor(s)")
            
            if num_detections > 0:
                for i, box in enumerate(boxes, 1):
                    conf = float(box.conf[0])
                    coords = box.xyxy[0].tolist()
                    logging.info(f"Tumor {i}: Confidence {conf:.2%}")
                    # Format results for the API
                    print(f"DETECTION:{conf:.4f}")  # Special marker for parsing in the API

        # Return the absolute path for the API
        abs_path = str(saved_img.resolve())
        print(f"PROCESSED_IMAGE:{abs_path}")  # Special marker for the processed image path
        return saved_img
        
    except Exception as e:
        logging.error(f"Error during prediction: {str(e)}")
        raise

def test_run():
    """Test function to verify script execution"""
    try:
        # Get any test image from the datasets folder
        test_dir = _script_dir / 'datasets/test/images'
        if not test_dir.exists():
            logging.error("Test directory not found at: datasets/test/images")
            logging.info("Please ensure the dataset is properly set up")
            return False

        test_images = list(test_dir.glob('*.jpg'))
        if not test_images:
            logging.error("No test images (*.jpg) found in test directory")
            logging.info("Please add some test images to datasets/test/images")
            return False
        
        test_image = test_images[0]  # Use first test image
        logging.info(f"Running test with image: {test_image}")
        
        result = predict_single_image(str(test_image))
        return result is not None and result.exists()
    except Exception as e:
        logging.error(f"Test run failed: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    try:
        if len(sys.argv) == 2:
            predict_single_image(sys.argv[1])
        else:
            if test_run():
                logging.info("Test run successful!")
                print("Test run successful! Script is working correctly.")
            else:
                logging.error("Test run failed!")
                print("Test run failed! Please check the logs for details.")
                sys.exit(1)
    finally:
        clear_gpu_memory()  # Clean up just in case
