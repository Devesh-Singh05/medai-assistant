from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
import os
import sys
import time

class LungCancerDetector:
    def __init__(self, model_path='runs/train/lung_cancer_detection/weights/best.pt'):
        """
        Initialize the lung cancer detector
        Args:
            model_path: Path to the trained YOLO model
        """
        print("\nInitializing Lung Cancer Detector...")
        print(f"Looking for model at: {model_path}")
        
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model not found at {model_path}. Please train the model first.")
        
        print("Loading model...")
        self.model = YOLO(model_path)
        print(f"✓ Model loaded successfully from: {model_path}")
        print(f"Model type: {self.model.type}")
        print(f"Model task: {self.model.task}")
    
    def predict_image(self, image_path, conf_threshold=0.25):
        """
        Perform lung cancer detection on a single image
        Args:
            image_path: Path to the image file
            conf_threshold: Confidence threshold for detections
        Returns:
            results: List of detections
            annotated_image: Image with bounding boxes drawn
        """
        print(f"\nProcessing image: {Path(image_path).name}")
        print(f"Confidence threshold: {conf_threshold}")
        
        # Run inference
        print("Running inference...")
        results = self.model(image_path, conf=conf_threshold)
        
        # Get the first result (single image)
        result = results[0]
        
        # Load the original image
        print("Loading image for visualization...")
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not load image at {image_path}")
        
        print(f"Image size: {image.shape}")
        
        # Draw bounding boxes and labels
        print("Drawing detections...")
        annotated_image = image.copy()
        detections = []
        
        for box in result.boxes:
            # Get box coordinates and confidence
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            
            # Convert coordinates to integers
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            
            # Draw rectangle
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Add confidence label
            label = f'Cancer: {conf:.2f}'
            cv2.putText(annotated_image, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Store detection details
            detections.append({
                'confidence': conf,
                'bbox': [x1, y1, x2, y2]
            })
        
        print(f"Found {len(detections)} detections")
        for i, det in enumerate(detections, 1):
            print(f"  Detection {i}: Confidence = {det['confidence']:.2f}")
        
        return results, annotated_image

def process_test_set():
    """
    Process all images in the test set and save results
    """
    print("\n" + "="*50)
    print("Starting Lung Cancer Detection on Test Set")
    print("="*50 + "\n")
    
    try:
        # Create output directory
        print("Step 1: Setting up output directory...")
        output_dir = Path('runs/detect/test_results')
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory created at: {output_dir}")
        
        # Initialize detector
        print("\nStep 2: Initializing detector...")
        try:
            detector = LungCancerDetector()
            print("✓ Detector initialized successfully")
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            print("Please run train.py first to train the model.")
            return
        
        # Process test images
        print("\nStep 3: Processing test images...")
        test_dir = Path('Images/test/images')
        if not test_dir.exists():
            print(f"❌ Error: Test directory not found at {test_dir}")
            return
        
        # Get list of test images
        test_images = list(test_dir.glob('*.jpg'))
        total_images = len(test_images)
        print(f"Found {total_images} images to process")
        
        # Initialize metrics
        total_detections = 0
        processing_times = []
        
        # Process each image
        for idx, img_path in enumerate(test_images, 1):
            try:
                print(f"\nProcessing image {idx}/{total_images}: {img_path.name}")
                start_time = time.time()
                
                # Perform detection
                results, annotated_image = detector.predict_image(str(img_path))
                
                # Save annotated image
                output_path = output_dir / f"detected_{img_path.name}"
                cv2.imwrite(str(output_path), annotated_image)
                
                # Update metrics
                num_detections = len(results[0].boxes)
                total_detections += num_detections
                
                # Calculate processing time
                processing_time = time.time() - start_time
                processing_times.append(processing_time)
                
                print(f"✓ Saved result to: {output_path}")
                print(f"  Processing time: {processing_time:.2f} seconds")
                
            except Exception as e:
                print(f"❌ Error processing {img_path.name}: {e}")
        
        # Print summary
        print("\n" + "="*50)
        print("Processing Summary")
        print("="*50)
        print(f"Total images processed: {total_images}")
        print(f"Total detections: {total_detections}")
        print(f"Average detections per image: {total_detections/total_images if total_images > 0 else 0:.2f}")
        print(f"Average processing time: {sum(processing_times)/len(processing_times):.2f} seconds per image")
        print(f"Results saved in: {output_dir}")
        print("="*50)
        
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        print("\nTraceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    process_test_set() 