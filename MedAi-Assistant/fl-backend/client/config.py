from pathlib import Path

class Config:
    # Data paths
    DATA_DIR = Path("data")
    CT_DATA_PATH = DATA_DIR / "ct" / "covid_ct"
    MRI_DATA_PATH = DATA_DIR / "mri" / "fastmri"
    
    # Training parameters
    BATCH_SIZE = 32
    NUM_EPOCHS = 50
    LEARNING_RATE = 1e-4
    WEIGHT_DECAY = 1e-5
    
    # Model parameters
    CT_CLASSES = 2  # Normal, COVID
    MRI_CLASSES = 2  # Normal, Abnormal
    IMAGE_SIZE = (224, 224)
    
    # Federated Learning parameters
    MIN_CLIENTS = 3
    CLIENT_FRACTION = 0.8
    LOCAL_EPOCHS = 5
    
    # Privacy parameters
    DP_NOISE_SCALE = 0.001
    DP_L2_NORM_CLIP = 1.0
    
    # Optimization parameters
    OPTIMIZER = {
        'name': 'Adam',
        'params': {
            'lr': LEARNING_RATE,
            'weight_decay': WEIGHT_DECAY,
            'betas': (0.9, 0.999),
            'eps': 1e-8
        }
    }
    
    # Loss weights
    LOSS_WEIGHTS = {
        'classification': 1.0,
        'segmentation': 1.0
    }
    
    # Data augmentation parameters
    AUGMENTATION = {
        'horizontal_flip_prob': 0.5,
        'vertical_flip_prob': 0.5,
        'rotate_prob': 0.5,
        'rotate_limit': 45,
        'noise_prob': 0.2
    }
    
    # Checkpointing
    CHECKPOINT_DIR = Path("checkpoints")
    SAVE_FREQUENCY = 5  # Save every 5 epochs
    
    # Logging
    LOG_DIR = Path("logs")
    LOG_FREQUENCY = 100  # Log every 100 batches
    
    # Device settings
    USE_CUDA = True
    NUM_WORKERS = 4
    
    # Metrics
    METRICS = {
        'classification': ['accuracy', 'precision', 'recall', 'f1'],
        'segmentation': ['dice', 'iou']
    }
    
    # Early stopping
    EARLY_STOPPING = {
        'patience': 10,
        'min_delta': 0.001
    }