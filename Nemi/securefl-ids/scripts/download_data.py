#!/usr/bin/env python3
"""
Download and prepare UNSW-NB15 dataset
"""
import os
import sys
import pandas as pd
import numpy as np
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def download_unsw_nb15(sample=False):
    """
    Download UNSW-NB15 dataset or create sample
    
    Note: Full dataset available at https://research.unsw.edu.au/projects/unsw-nb15-dataset
    For this implementation, we create a synthetic sample for demonstration
    """
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    output_file = os.path.join(data_dir, "UNSW_NB15_training-set.csv")
    
    if os.path.exists(output_file):
        print(f"Dataset already exists at {output_file}")
        return output_file
    
    print("UNSW-NB15 dataset download:")
    print("=" * 60)
    print("For the full dataset, download from:")
    print("https://research.unsw.edu.au/projects/unsw-nb15-dataset")
    print("\nFor this demonstration, creating a synthetic sample...")
    print("=" * 60)
    
    # Create synthetic sample matching UNSW-NB15 characteristics
    # 49 features (simplified to 20 key features for demo)
    num_samples = 5000 if sample else 50000
    num_features = 20
    
    np.random.seed(42)
    
    # Generate synthetic features
    data = {}
    
    # Duration and protocol features
    data['dur'] = np.random.exponential(scale=10, size=num_samples)
    data['proto'] = np.random.choice(['tcp', 'udp', 'icmp'], size=num_samples)
    data['state'] = np.random.choice(['FIN', 'INT', 'CON', 'REQ'], size=num_samples)
    
    # Packet and byte features
    data['spkts'] = np.random.poisson(lam=50, size=num_samples)
    data['dpkts'] = np.random.poisson(lam=40, size=num_samples)
    data['sbytes'] = np.random.exponential(scale=1000, size=num_samples)
    data['dbytes'] = np.random.exponential(scale=800, size=num_samples)
    
    # Rate features
    data['rate'] = np.random.uniform(0, 1000, size=num_samples)
    data['sttl'] = np.random.randint(0, 255, size=num_samples)
    data['dttl'] = np.random.randint(0, 255, size=num_samples)
    
    # Load and inter-arrival time
    data['sload'] = np.random.uniform(0, 1e6, size=num_samples)
    data['dload'] = np.random.uniform(0, 1e6, size=num_samples)
    data['sinpkt'] = np.random.exponential(scale=100, size=num_samples)
    data['dinpkt'] = np.random.exponential(scale=100, size=num_samples)
    
    # Window and TCP features
    data['swin'] = np.random.randint(0, 65535, size=num_samples)
    data['dwin'] = np.random.randint(0, 65535, size=num_samples)
    data['tcprtt'] = np.random.exponential(scale=50, size=num_samples)
    data['synack'] = np.random.exponential(scale=20, size=num_samples)
    data['ackdat'] = np.random.exponential(scale=20, size=num_samples)
    
    # Service and connection features
    data['ct_srv_src'] = np.random.randint(0, 100, size=num_samples)
    
    # Labels: 80% normal, 20% attack
    normal_ratio = 0.8
    num_normal = int(num_samples * normal_ratio)
    
    labels = np.zeros(num_samples, dtype=int)
    labels[num_normal:] = 1
    
    # Shuffle
    shuffle_idx = np.random.permutation(num_samples)
    for key in data:
        if isinstance(data[key], np.ndarray):
            data[key] = data[key][shuffle_idx]
    labels = labels[shuffle_idx]
    
    data['label'] = labels
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Encode categorical features
    df['proto'] = df['proto'].map({'tcp': 0, 'udp': 1, 'icmp': 2})
    df['state'] = df['state'].map({'FIN': 0, 'INT': 1, 'CON': 2, 'REQ': 3})
    
    # Save
    df.to_csv(output_file, index=False)
    print(f"\nDataset created: {output_file}")
    print(f"Samples: {len(df)}, Features: {len(df.columns)-1}")
    print(f"Normal: {(df['label']==0).sum()}, Attack: {(df['label']==1).sum()}")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(description='Download UNSW-NB15 dataset')
    parser.add_argument('--sample', action='store_true', 
                       help='Create small sample (5K samples) for quick testing')
    args = parser.parse_args()
    
    download_unsw_nb15(sample=args.sample)
    print("\nDataset ready for experiments!")


if __name__ == '__main__':
    main()
