import torch
from torch.utils.data import Dataset
import numpy as np
import os
from pathlib import Path
import cv2
import pydicom
import h5py
import pandas as pd
from typing import Dict, Tuple, List
import albumentations as A
from albumentations.pytorch import ToTensorV2

class MedicalImagePreprocessor:
    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        self.transform = self._get_transforms()
        
    def _get_transforms(self):
        return A.Compose([
            A.Resize(height=self.target_size[0], width=self.target_size[1]),
            A.Normalize(mean=[0.485], std=[0.229]),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.GaussNoise(p=0.2),
            ToTensorV2(),
        ])

class KaggleCTDataset(Dataset):
    """Dataset class for Kaggle COVID-19 CT scans"""
    def __init__(self, data_path: str, split: str = 'train'):
        self.data_path = Path(data_path)
        self.split = split
        self.preprocessor = MedicalImagePreprocessor()
        self.images, self.labels = self._load_dataset()

    def _load_dataset(self) -> Tuple[List[str], List[int]]:
        annotations_file = self.data_path / 'metadata.csv'
        df = pd.read_csv(annotations_file)
        
        if self.split == 'train':
            df = df.sample(frac=0.8, random_state=42)
        else:
            df = df.sample(frac=0.2, random_state=42)

        image_paths = [str(self.data_path / 'ct_scan_images' / f) for f in df['filename']]
        labels = df['label'].map({'normal': 0, 'covid': 1}).tolist()
        
        return image_paths, labels

    def __len__(self) -> int:
        return len(self.images)

    def __getitem__(self, idx: int) -> Dict:
        image_path = self.images[idx]
        label = self.labels[idx]

        # Load and preprocess image
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        image = self.preprocessor.transform(image=image)['image']

        return {
            'image': image,
            'label': torch.tensor(label, dtype=torch.long),
            'path': image_path
        }

class FastMRIDataset(Dataset):
    """Dataset class for FastMRI brain/knee dataset"""
    def __init__(self, data_path: str, type: str = 'brain', split: str = 'train'):
        self.data_path = Path(data_path)
        self.type = type
        self.split = split
        self.preprocessor = MedicalImagePreprocessor()
        self.files = self._get_files()

    def _get_files(self) -> List[str]:
        pattern = f"*.h5"
        files = list(self.data_path.glob(pattern))
        
        if self.split == 'train':
            return files[:int(0.8 * len(files))]
        return files[int(0.8 * len(files)):]

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, idx: int) -> Dict:
        file_path = self.files[idx]
        
        with h5py.File(file_path, 'r') as hf:
            # Load image data
            if 'kspace' in hf:
                # Convert k-space to image
                kspace = hf['kspace'][()]
                image = np.fft.ifft2(kspace)
                image = np.abs(image)
            else:
                image = hf['reconstruction_rss'][()]

            # Get slice from middle of volume
            if len(image.shape) == 3:
                slice_idx = image.shape[0] // 2
                image = image[slice_idx]

            # Normalize and preprocess
            image = (image - image.min()) / (image.max() - image.min())
            image = (image * 255).astype(np.uint8)
            image = self.preprocessor.transform(image=image)['image']

            # Get metadata if available
            metadata = {}
            if 'ismrmrd_header' in hf:
                metadata = hf['ismrmrd_header'][()]

            return {
                'image': image,
                'metadata': metadata,
                'path': str(file_path)
            }

def get_dataloaders(
    ct_path: str,
    mri_path: str,
    batch_size: int = 32,
    num_workers: int = 4
):
    """Create dataloaders for both CT and MRI datasets"""
    # CT Dataset
    ct_train = KaggleCTDataset(ct_path, split='train')
    ct_val = KaggleCTDataset(ct_path, split='val')

    # MRI Dataset
    mri_train = FastMRIDataset(mri_path, split='train')
    mri_val = FastMRIDataset(mri_path, split='val')

    dataloaders = {
        'ct': {
            'train': torch.utils.data.DataLoader(
                ct_train,
                batch_size=batch_size,
                shuffle=True,
                num_workers=num_workers
            ),
            'val': torch.utils.data.DataLoader(
                ct_val,
                batch_size=batch_size,
                shuffle=False,
                num_workers=num_workers
            )
        },
        'mri': {
            'train': torch.utils.data.DataLoader(
                mri_train,
                batch_size=batch_size,
                shuffle=True,
                num_workers=num_workers
            ),
            'val': torch.utils.data.DataLoader(
                mri_val,
                batch_size=batch_size,
                shuffle=False,
                num_workers=num_workers
            )
        }
    }
    
    return dataloaders