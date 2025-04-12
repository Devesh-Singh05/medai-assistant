# YOLO Object Detection

This project uses Ultralytics YOLO for object detection, segmentation, and classification tasks.

## Installation

YOLO is already installed in this environment. If you need to install it in another environment, use:

```bash
pip install ultralytics
```

## Usage

The `train.py` script demonstrates basic YOLO functionality:

1. Loading a pre-trained model
2. Running inference on an example image
3. Examples of training, validation, and model export (commented out by default)

To run the example:

```bash
python train.py
```

## Working with Custom Data

To train YOLO on your own dataset:

1. Organize your data according to YOLO format:
   - Images in a folder
   - Labels in a folder with the same name as the images but with .txt extension
   - Each label file contains one line per object: `class x_center y_center width height`

2. Create a YAML file describing your dataset:
   ```yaml
   path: /path/to/dataset
   train: images/train
   val: images/val
   test: images/test
   
   # Classes
   names:
     0: person
     1: car
     # Add more classes as needed
   ```

3. Uncomment and modify the training section in `train.py`:
   ```python
   results = model.train(
       data='path/to/your/dataset.yaml',
       epochs=100,
       imgsz=640,
       device='0',  # Use 'cpu' for CPU training
       project='runs',
       name='train',
   )
   ```

## Available Models

Ultralytics provides various pre-trained models:

- YOLOv8n, YOLOv8s, YOLOv8m, YOLOv8l, YOLOv8x (from smallest to largest)
- YOLO11n, YOLO11s, YOLO11m, YOLO11l, YOLO11x (newer models)

For specialized tasks:
- Detection: `yolov8n.pt`, `yolo11n.pt`
- Segmentation: `yolov8n-seg.pt`
- Classification: `yolov8n-cls.pt`
- Pose Estimation: `yolov8n-pose.pt`

## Documentation

For more information, visit the [Ultralytics YOLO Documentation](https://docs.ultralytics.com/). 