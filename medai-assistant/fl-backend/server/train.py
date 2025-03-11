import argparse
import asyncio
import json
import logging
from pathlib import Path
from server import FederatedServer
from database import get_db_session, TrainingMetrics, GlobalModel
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def train(args):
    # Initialize server and database
    server = FederatedServer(min_clients=args.min_clients)
    db = get_db_session()

    try:
        # Start training round
        await server.start_training_round()
        
        # Process client update
        client_update = {
            'client_id': args.client_id,
            'round': args.round
        }
        
        await server.add_client_update(args.client_id, client_update)
        
        # Save metrics to database
        metrics = TrainingMetrics(
            round=args.round,
            client_id=args.client_id,
            accuracy=client_update.get('accuracy', 0),
            loss=client_update.get('loss', 0),
            metrics=client_update
        )
        db.add(metrics)
        
        # If enough updates received, aggregate and save global model
        if len(server.client_updates) >= server.min_clients:
            await server.aggregate_updates()
            
            # Save global model
            model_path = f"checkpoints/global_model_round_{args.round}.pt"
            global_model = GlobalModel(
                round=args.round,
                model_path=model_path,
                metrics=server.global_metrics
            )
            db.add(global_model)
        
        db.commit()
        
        # Return current metrics
        print(json.dumps({
            'success': True,
            'metrics': server.get_training_metrics()
        }))

    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        print(json.dumps({
            'success': False,
            'error': str(e)
        }))
        db.rollback()
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description='Federated Learning Training Script')
    parser.add_argument('--client_id', type=str, required=True)
    parser.add_argument('--round', type=int, required=True)
    parser.add_argument('--min_clients', type=int, default=3)
    args = parser.parse_args()

    asyncio.run(train(args))

if __name__ == '__main__':
    main()