import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pydicom
import nibabel as nib
from pathlib import Path
import cv2
import json
from typing import Dict, Tuple, List
import albumentations as A

class MedicalImageDataset(Dataset):
    def __init__(self, 
                 data_path: str,
                 modality: str,
                 transform=None,
                 mode='train'):
        self.data_path = Path(data_path)
        self.modality = modality
        self.mode = mode
        self.transform = transform or self._get_default_transforms()
        self.samples = self._scan_directory()
        
    def _scan_directory(self) -> List[Dict]:
        samples = []
        if self.modality == 'ct':
            # Scan for DICOM files
            for dcm_file in self.data_path.glob('**/*.dcm'):
                samples.append({
                    'path': str(dcm_file),
                    'label': self._get_label(dcm_file)
                })
        else:
            # Scan for NIfTI files
            for nii_file in self.data_path.glob('**/*.nii*'):
                samples.append({
                    'path': str(nii_file),
                    'label': self._get_label(nii_file)
                })
        return samples
    
    def _get_default_transforms(self):
        if self.mode == 'train':
            return A.Compose([
                A.RandomRotate90(p=0.5),
                A.HorizontalFlip(p=0.5),
                A.VerticalFlip(p=0.5),
                A.RandomBrightnessContrast(p=0.2),
                A.Normalize(mean=[0.485], std=[0.229]),
                A.Resize(224, 224)
            ])
        else:
            return A.Compose([
                A.Normalize(mean=[0.485], std=[0.229]),
                A.Resize(224, 224)
            ])
    
    def _load_ct_image(self, path: str) -> np.ndarray:
        dcm = pydicom.dcmread(path)
        image = dcm.pixel_array.astype(float)
        
        # Apply windowing
        if hasattr(dcm, 'WindowCenter') and hasattr(dcm, 'WindowWidth'):
            center = dcm.WindowCenter
            width = dcm.WindowWidth
            if isinstance(center, list):
                center = center[0]
            if isinstance(width, list):
                width = width[0]
            image = self._apply_windowing(image, center, width)
            
        return image
    
    def _load_mri_image(self, path: str) -> np.ndarray:
        nii = nib.load(path)
        image = nii.get_fdata()
        
        # Take middle slice for 3D volumes
        if len(image.shape) == 3:
            image = image[:, :, image.shape[2]//2]
            
        return image
    
    def _apply_windowing(self, image: np.ndarray, center: float, width: float) -> np.ndarray:
        min_value = center - width//2
        max_value = center + width//2
        image = np.clip(image, min_value, max_value)
        image = (image - min_value) / (max_value - min_value)
        return image
    
    def _get_label(self, file_path: Path) -> int:
        # Implement your labeling logic here
        # This could involve reading from an annotations file
        return 0
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        sample = self.samples[idx]
        
        # Load image based on modality
        if self.modality == 'ct':
            image = self._load_ct_image(sample['path'])
        else:
            image = self._load_mri_image(sample['path'])
        
        # Apply transformations
        if self.transform:
            augmented = self.transform(image=image)
            image = augmented['image']
        
        # Convert to tensor if not already
        if not isinstance(image, torch.Tensor):
            image = torch.from_numpy(image).float()
            
        # Add channel dimension if needed
        if image.ndim == 2:
            image = image.unsqueeze(0)
            
        return image, sample['label'], self.modality

class PatientDataManager:
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.patient_records = {}
        self._load_patient_records()
    
    def _load_patient_records(self):
        if (self.data_path / 'patient_records.json').exists():
            with open(self.data_path / 'patient_records.json', 'r') as f:
                self.patient_records = json.load(f)
    
    def save_patient_records(self):
        with open(self.data_path / 'patient_records.json', 'w') as f:
            json.dump(self.patient_records, f)
    
    def add_patient_record(self, 
                          patient_id: str,
                          patient_name: str,
                          image_path: str,
                          image_type: str,
                          analysis_result: Dict = None):
        if patient_id not in self.patient_records:
            self.patient_records[patient_id] = {
                'name': patient_name,
                'records': []
            }
            
        self.patient_records[patient_id]['records'].append({
            'image_path': image_path,
            'image_type': image_type,
            'upload_time': str(datetime.now()),
            'analysis_result': analysis_result
        })
        
        self.save_patient_records()
    
    def get_patient_history(self, patient_id: str) -> List[Dict]:
        if patient_id in self.patient_records:
            return self.patient_records[patient_id]['records']
        return []

def get_data_loaders(data_path: str,
                    batch_size: int = 32,
                    num_workers: int = 4) -> Tuple[DataLoader, DataLoader]:
    # Create datasets for both modalities
    ct_train_dataset = MedicalImageDataset(
        data_path=f"{data_path}/ct/train",
        modality='ct',
        mode='train'
    )
    
    mri_train_dataset = MedicalImageDataset(
        data_path=f"{data_path}/mri/train",
        modality='mri',
        mode='train'
    )
    
    # Combine datasets
    train_dataset = torch.utils.data.ConcatDataset([ct_train_dataset, mri_train_dataset])
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers
    )
    
    return train_loader