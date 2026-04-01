import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_metrics(csv_file='real_results.csv'):
    if not os.path.exists(csv_file):
        print(f"File {csv_file} not found.")
        return

    df = pd.read_csv(csv_file)
    files = df['File'].unique()
    
    # We want a grouped bar chart for Tokens and latency
    
    # Token Graph
    plt.figure(figsize=(10, 6))
    width = 0.2
    formats = ['JSON (Pretty)', 'JSON (Compact)', 'YAML', 'TOON']
    
    for i, file in enumerate(files):
        subset = df[df['File'] == file]
        y_pos = [i + (j - 1.5)*width for j in range(len(formats))]
        
        for j, fmt in enumerate(formats):
            val = subset[subset['Format'] == fmt]['Tokens'].values
            if len(val) > 0:
                plt.bar(y_pos[j], val[0], width, label=fmt if i == 0 else "")
                
    plt.xticks(range(len(files)), [f.split('.')[0] for f in files], rotation=15)
    plt.ylabel('Token Count')
    plt.title('Token Efficiency by Format')
    plt.legend()
    plt.tight_layout()
    plt.savefig('tokens_comparison.png')
    plt.close()

    # Latency Graph
    plt.figure(figsize=(10, 6))
    for i, file in enumerate(files):
        subset = df[df['File'] == file]
        y_pos = [i + (j - 1.5)*width for j in range(len(formats))]
        
        for j, fmt in enumerate(formats):
            val = subset[subset['Format'] == fmt]['Time_ms'].values
            if len(val) > 0:
                plt.bar(y_pos[j], val[0], width, label=fmt if i == 0 else "")
                
    plt.xticks(range(len(files)), [f.split('.')[0] for f in files], rotation=15)
    plt.ylabel('Latency (ms)')
    plt.title('Parser Latency Comparison')
    plt.legend()
    plt.tight_layout()
    plt.savefig('latency_comparison.png')
    plt.close()
    
    print("Graphs saved as tokens_comparison.png and latency_comparison.png")

if __name__ == '__main__':
    plot_metrics()
