import os
import shutil
import random
import yaml
from pathlib import Path

# Set the paths
dataset_dir = Path('/home/datasets/Images')
train_img_dir = dataset_dir / 'train' / 'images'
train_lbl_dir = dataset_dir / 'train' / 'labels'
valid_img_dir = dataset_dir / 'valid' / 'images'
valid_lbl_dir = dataset_dir / 'valid' / 'labels'

# Create validation directories if they don't exist
valid_img_dir.mkdir(parents=True, exist_ok=True)
valid_lbl_dir.mkdir(parents=True, exist_ok=True)

# Get list of training images
train_images = list(train_img_dir.glob('*.jpg')) + list(train_img_dir.glob('*.png'))
print(f"Total training images: {len(train_images)}")

# Define validation split (10% of training)
valid_split = 0.1
num_valid = int(len(train_images) * valid_split)
print(f"Moving {num_valid} images to validation set")

# Randomly select images for validation
random.seed(42)  # For reproducibility
valid_images = random.sample(train_images, num_valid)

# Move images and corresponding labels to validation
for img_path in valid_images:
    # Get image filename
    img_filename = img_path.name
    
    # Move image
    shutil.move(str(img_path), str(valid_img_dir / img_filename))
    
    # Get and move label (if exists)
    label_filename = img_path.stem + '.txt'
    label_path = train_lbl_dir / label_filename
    if label_path.exists():
        shutil.move(str(label_path), str(valid_lbl_dir / label_filename))

# Count final images
final_train_count = len(list(train_img_dir.glob('*.jpg'))) + len(list(train_img_dir.glob('*.png')))
final_valid_count = len(list(valid_img_dir.glob('*.jpg'))) + len(list(valid_img_dir.glob('*.png')))

print(f"Final training images: {final_train_count}")
print(f"Final validation images: {final_valid_count}")

# Update data.yaml if needed
yaml_path = dataset_dir / 'data.yaml'
if yaml_path.exists():
    with open(yaml_path, 'r') as f:
        yaml_data = yaml.safe_load(f)
    
    # Update paths if needed
    if 'val' not in yaml_data or not yaml_data['val']:
        yaml_data['val'] = './valid/images'
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f, sort_keys=False)
        print(f"Updated {yaml_path} with validation path")
    else:
        print(f"Validation path already exists in {yaml_path}")

print("Done! Validation set created successfully.") 