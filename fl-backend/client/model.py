import torch
import torch.nn as nn
import torchvision.models as models

class Encoder(nn.Module):
    def __init__(self, in_channels=1):
        super().__init__()
        # Use EfficientNet-B0 as backbone
        self.backbone = models.efficientnet_b0(pretrained=True)
        
        # Modify first layer to accept single channel
        self.backbone._conv_stem = nn.Conv2d(
            in_channels, 32, 
            kernel_size=3, 
            stride=2, 
            padding=1, 
            bias=False
        )

    def forward(self, x):
        # Get intermediary features
        features = []
        
        # Stem
        x = self.backbone._conv_stem(x)
        x = self.backbone._bn0(x)
        x = self.backbone._swish(x)
        features.append(x)
        
        # Blocks
        for idx, block in enumerate(self.backbone._blocks):
            x = block(x)
            if idx in [5, 10, 15]:  # Get features at different scales
                features.append(x)
                
        # Head
        x = self.backbone._conv_head(x)
        x = self.backbone._bn1(x)
        x = self.backbone._swish(x)
        features.append(x)
        
        return features

class DecoderBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)
        return x

class DualModalityModel(nn.Module):
    def __init__(self, ct_classes=2, mri_classes=2):
        super().__init__()
        self.ct_encoder = Encoder(in_channels=1)
        self.mri_encoder = Encoder(in_channels=1)
        
        # CT-specific heads
        self.ct_classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(1280, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, ct_classes)
        )
        
        self.ct_segmentation = nn.Sequential(
            DecoderBlock(1280, 512),
            nn.ConvTranspose2d(512, 256, 2, stride=2),
            DecoderBlock(256, 256),
            nn.ConvTranspose2d(256, 128, 2, stride=2),
            DecoderBlock(128, 128),
            nn.ConvTranspose2d(128, 64, 2, stride=2),
            DecoderBlock(64, 64),
            nn.Conv2d(64, 1, 1)
        )
        
        # MRI-specific heads
        self.mri_classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(1280, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, mri_classes)
        )
        
        self.mri_segmentation = nn.Sequential(
            DecoderBlock(1280, 512),
            nn.ConvTranspose2d(512, 256, 2, stride=2),
            DecoderBlock(256, 256),
            nn.ConvTranspose2d(256, 128, 2, stride=2),
            DecoderBlock(128, 128),
            nn.ConvTranspose2d(128, 64, 2, stride=2),
            DecoderBlock(64, 64),
            nn.Conv2d(64, 1, 1)
        )

    def forward(self, x, modality='ct'):
        if modality == 'ct':
            features = self.ct_encoder(x)
            classification = self.ct_classifier(features[-1])
            segmentation = self.ct_segmentation(features[-1])
        else:
            features = self.mri_encoder(x)
            classification = self.mri_classifier(features[-1])
            segmentation = self.mri_segmentation(features[-1])
        
        return {
            'classification': classification,
            'segmentation': segmentation,
            'features': features[-1]
        }

    def get_gradients(self):
        """Get model gradients for federated learning"""
        grads = []
        for param in self.parameters():
            if param.grad is not None:
                grads.append(param.grad.data.clone())
        return grads

    def set_gradients(self, gradients):
        """Set model gradients for federated learning"""
        for g, param in zip(gradients, self.parameters()):
            if param.grad is not None:
                param.grad.data = g.clone()

    def add_noise(self, noise_scale=0.001):
        """Add differential privacy noise to parameters"""
        with torch.no_grad():
            for param in self.parameters():
                noise = torch.randn_like(param) * noise_scale
                param.add_(noise)