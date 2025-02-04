import argparse
import torch
import json
import sys
from pathlib import Path
from server import FederatedServer
from model import MedicalImageAnalyzer

def setup_args():
    parser = argparse.ArgumentParser(description='Federated Learning Server CLI')
    parser.add_argument('--mode', type=str, required=True, choices=['train', 'inference'])
    parser.add_argument('--client_id', type=int, help='Client ID for training')
    parser.add_argument('--update_path', type=str, help='Path to model update file')
    parser.add_argument('--image_path', type=str, help='Path to image for inference')
    parser.add_argument('--image_type', type=str, choices=['ct', 'mri'], help='Type of medical image')
    return parser.parse_args()

def load_model():
    model = MedicalImageAnalyzer()
    model_path = Path(__file__).parent / 'checkpoints' / 'latest.pt'
    if model_path.exists():
        model.load_state_dict(torch.load(model_path))
    return model

def handle_training(args):
    # Initialize server and model
    model = load_model()
    server = FederatedServer(model)
    
    # Load client update
    with open(args.update_path, 'r') as f:
        client_update = json.load(f)
    
    # Process update
    server.add_client_update(args.client_id, client_update)
    if server.check_round_completion():
        aggregated_model = server.complete_round()
        
        # Save updated model
        save_path = Path(__file__).parent / 'checkpoints' / 'latest.pt'
        save_path.parent.mkdir(exist_ok=True)
        torch.save(aggregated_model, save_path)
        
        print(json.dumps({
            'status': 'success',
            'round': server.current_round,
            'message': 'Model updated successfully'
        }))
    else:
        print(json.dumps({
            'status': 'pending',
            'message': 'Update received, waiting for more clients'
        }))

def handle_inference(args):
    # Load model
    model = load_model()
    model.eval()
    
    # Load and preprocess image
    from data_loader import MedicalImagePreprocessor
    preprocessor = MedicalImagePreprocessor()
    
    if args.image_type == 'ct':
        import pydicom
        image = pydicom.dcmread(args.image_path).pixel_array
        tensor = preprocessor.preprocess_ct(image)
    else:
        import nibabel as nib
        image = nib.load(args.image_path).get_fdata()
        tensor = preprocessor.preprocess_mri(image)
    
    # Run inference
    with torch.no_grad():
        predictions, features = model(tensor.unsqueeze(0), args.image_type)
        probabilities = torch.softmax(predictions, dim=1)
        
        result = {
            'prediction': predictions.argmax(dim=1).item(),
            'confidence': probabilities.max().item(),
            'features': features.tolist()
        }
        
        print(json.dumps(result))

def main():
    args = setup_args()
    try:
        if args.mode == 'train':
            handle_training(args)
        else:
            handle_inference(args)
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'message': str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()