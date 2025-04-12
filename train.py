from ultralytics import YOLO
import os
import multiprocessing

# Get absolute path to current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    # Use yolo11m.pt as requested
    model = YOLO('yolo11m.pt')  
    
    model.train(
        # Data config - using relative path to work in any environment
        data=os.path.join(current_dir, 'datasets', 'Images', 'data.yaml'),
        epochs=100,
        imgsz=640,
        batch=16,
        workers=0,                # For Windows compatibility
        
        # Training strategy
        name='lung_cancer_detection',
        patience=20,
        cos_lr=True,
        lr0=0.01,
        lrf=0.001,
        
        # Memory and performance options
        cache=False,
        amp=True,
        
        # Optimizer settings
        optimizer='AdamW',
        weight_decay=0.0005,
        
        # Augmentation for medical imaging
        augment=True,
        mixup=0.1,
        mosaic=1.0,
        fliplr=0.5,              # Only horizontal flip for medical images
        scale=0.5,               # Scale variation
        
        # Loss function tuning (optimized for single class)
        box=7.5,                 # High box weight for accurate localization
        cls=0.3,                 # Reduced for single class
        dfl=1.5,
        
        # Validation and saving
        val=True,
        save_period=10,
        save=True,
        
        # Warmup
        warmup_epochs=3.0,
        
        exist_ok=True,
        plots=True,
    )

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main() 