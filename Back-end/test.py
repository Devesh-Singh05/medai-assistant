from ultralytics import YOLO
import os
from pathlib import Path

def main():
    # Load your trained model
    model = YOLO('model.pt')
    
    # Directory containing test images
    test_dir = Path('datasets/test/images')  # Updated path based on your error message
    
    # Get all images from test directory
    image_files = [f for f in os.listdir(test_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    print(f"\nProcessing {len(image_files)} images...")
    
    for image_file in image_files:
        # Full path to image
        image_path = str(test_dir / image_file)
        
        # Run inference
        results = model.predict(
            source=image_path,
            conf=0.25,        # Confidence threshold
            iou=0.7,         # NMS IoU threshold
            save=True,       # Save results to runs/detect/predict
            save_txt=True,   # Save results in txt format
            save_conf=True,  # Save confidences
            show=False,      # Don't try to display (fixes the error)
            line_width=2     # Box thickness
        )
        
        print(f"\nResults for {image_file}:")
        for r in results:
            boxes = r.boxes
            print(f"Found {len(boxes)} detections")
            
            # Print details for each detection
            for box in boxes:
                conf = float(box.conf[0])
                coords = box.xyxy[0].tolist()  # get box coordinates
                print(f"Confidence: {conf:.2f}, Coordinates: {[round(x, 2) for x in coords]}")

    print("\nResults have been saved to 'runs/detect/predict'")
    print("- Annotated images are in the main folder")
    print("- Detection coordinates are in the 'labels' folder")

if __name__ == "__main__":
    main() 