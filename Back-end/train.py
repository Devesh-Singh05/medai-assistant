from ultralytics import YOLO
import os
import multiprocessing

# Get absolute path to current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    # Load the trained model from the last checkpoint
    model = YOLO('runs/detect/lung_cancer_detection/weights/last.pt')  
    
    # Continue training from where you left off
    model.train(
        data=os.path.join(current_dir, 'datasets', 'Images', 'data.yaml'),
        epochs=200,  # Increase total epochs (will train for 100 more)
        imgsz=640,
        batch=16,
        workers=0,
        name='lung_cancer_detection',
        exist_ok=True,  # Important: allows resuming in the same folder
        resume=True,    # Resume training from last checkpoint
        val=True,
    )

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
