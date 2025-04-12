import glob
from PIL import Image
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import yaml
import cv2

class DatasetAnalyzer:
    def __init__(self, dataset_path='datasets/Images'):
        self.dataset_path = Path(dataset_path)
        self.train_path = self.dataset_path / 'train'
        self.valid_path = self.dataset_path / 'valid'
        self.test_path = self.dataset_path / 'test'
        
        # Load data.yaml
        with open(self.dataset_path / 'data.yaml', 'r') as f:
            self.yaml_data = yaml.safe_load(f)
            
    def analyze_split(self, split_path, split_name=""):
        """Analyze a specific data split (train/valid/test)"""
        images = list(split_path.glob('images/*.jpg'))
        labels = list(split_path.glob('labels/*.txt'))
        
        print(f"\n=== {split_name} Set Analysis ===")
        print(f"Number of images: {len(images)}")
        print(f"Number of labels: {len(labels)}")
        
        # Image analysis
        sizes = []
        aspects = []
        instances_per_img = []
        total_instances = 0
        bbox_sizes = []
        
        for img_path in images:
            # Image properties
            img = cv2.imread(str(img_path))
            h, w = img.shape[:2]
            sizes.append((w, h))
            aspects.append(w/h)
            
            # Label analysis
            label_path = split_path / 'labels' / (img_path.stem + '.txt')
            if label_path.exists():
                with open(label_path) as f:
                    lines = f.readlines()
                    instances_per_img.append(len(lines))
                    total_instances += len(lines)
                    
                    # Analyze bounding boxes
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            _, x, y, w, h = map(float, parts[:5])
                            bbox_sizes.append((w, h))
            else:
                instances_per_img.append(0)
        
        # Print statistics
        print("\nImage Statistics:")
        print(f"Average image size: {np.mean(sizes, axis=0)}")
        print(f"Average aspect ratio: {np.mean(aspects):.2f}")
        
        print("\nInstance Statistics:")
        print(f"Total instances: {total_instances}")
        print(f"Average instances per image: {np.mean(instances_per_img):.2f}")
        print(f"Max instances in one image: {max(instances_per_img)}")
        print(f"Images with no instances: {instances_per_img.count(0)}")
        
        # Plot distributions
        self.plot_distributions(instances_per_img, bbox_sizes, split_name)
        
        return {
            'total_images': len(images),
            'total_instances': total_instances,
            'avg_instances': np.mean(instances_per_img),
            'instances_distribution': instances_per_img,
            'bbox_sizes': bbox_sizes
        }
    
    def plot_distributions(self, instances_per_img, bbox_sizes, split_name):
        """Create visualizations of the data distribution"""
        plt.figure(figsize=(15, 5))
        
        # Instances per image distribution
        plt.subplot(131)
        sns.histplot(instances_per_img)
        plt.title(f'{split_name} Instances per Image')
        plt.xlabel('Number of Instances')
        plt.ylabel('Count')
        
        # Bounding box sizes
        if bbox_sizes:
            plt.subplot(132)
            bbox_w, bbox_h = zip(*bbox_sizes)
            plt.scatter(bbox_w, bbox_h, alpha=0.5)
            plt.title('Bounding Box Dimensions')
            plt.xlabel('Width (relative)')
            plt.ylabel('Height (relative)')
            
            # Box areas
            plt.subplot(133)
            areas = [w*h for w, h in bbox_sizes]
            sns.histplot(areas)
            plt.title('Bounding Box Areas')
            plt.xlabel('Area (relative)')
            plt.ylabel('Count')
        
        plt.tight_layout()
        
        # Save plot
        save_dir = Path('dataset_analysis')
        save_dir.mkdir(exist_ok=True)
        plt.savefig(save_dir / f'{split_name.lower()}_distribution.png')
        plt.close()
    
    def check_data_issues(self):
        """Check for common dataset issues"""
        print("\n=== Data Quality Checks ===")
        
        issues = []
        
        # Check YAML configuration
        print("\nChecking data.yaml configuration...")
        required_keys = ['train', 'val', 'test', 'nc', 'names']
        for key in required_keys:
            if key not in self.yaml_data:
                issues.append(f"Missing {key} in data.yaml")
        
        # Check for corrupt images
        print("Checking for corrupt images...")
        for split in ['train', 'valid', 'test']:
            split_path = self.dataset_path / split / 'images'
            if split_path.exists():
                for img_path in split_path.glob('*.jpg'):
                    try:
                        img = Image.open(img_path)
                        img.verify()
                    except:
                        issues.append(f"Corrupt image found: {img_path}")
        
        # Check label format
        print("Checking label format...")
        for split in ['train', 'valid', 'test']:
            label_path = self.dataset_path / split / 'labels'
            if label_path.exists():
                for label_file in label_path.glob('*.txt'):
                    with open(label_file) as f:
                        for i, line in enumerate(f):
                            try:
                                parts = line.strip().split()
                                if len(parts) < 5:
                                    issues.append(f"Invalid label format in {label_file}, line {i+1}")
                                class_id = int(parts[0])
                                if class_id >= self.yaml_data['nc']:
                                    issues.append(f"Invalid class ID in {label_file}: {class_id}")
                            except:
                                issues.append(f"Error parsing {label_file}, line {i+1}")
        
        # Report issues
        if issues:
            print("\nIssues found:")
            for issue in issues:
                print(f"- {issue}")
        else:
            print("\nNo issues found!")
        
        return issues

def main():
    analyzer = DatasetAnalyzer()
    
    # Analyze each split
    train_stats = analyzer.analyze_split(analyzer.train_path, "Training")
    valid_stats = analyzer.analyze_split(analyzer.valid_path, "Validation")
    test_stats = analyzer.analyze_split(analyzer.test_path, "Test")
    
    # Check for data issues
    issues = analyzer.check_data_issues()
    
    # Save analysis report
    report = {
        'train': train_stats,
        'valid': valid_stats,
        'test': test_stats,
        'issues': issues
    }
    
    # Save summary
    save_dir = Path('dataset_analysis')
    save_dir.mkdir(exist_ok=True)
    
    with open(save_dir / 'analysis_report.txt', 'w') as f:
        f.write("=== Dataset Analysis Report ===\n\n")
        for split_name, stats in report.items():
            if split_name != 'issues':
                f.write(f"\n{split_name.upper()} SET:\n")
                f.write(f"Total images: {stats['total_images']}\n")
                f.write(f"Total instances: {stats['total_instances']}\n")
                f.write(f"Average instances per image: {stats['avg_instances']:.2f}\n")
        
        if issues:
            f.write("\nISSUES FOUND:\n")
            for issue in issues:
                f.write(f"- {issue}\n")

if __name__ == "__main__":
    main() 