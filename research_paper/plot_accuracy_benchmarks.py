import matplotlib.pyplot as plt
import numpy as np

def plot_efficiency_ranking():
    # Data from official TOON repository benchmarking (Xaviviro et al., 2024)
    formats = ['TOON', 'JSON Compact', 'YAML', 'JSON', 'XML']
    efficiency = [27.7, 23.7, 19.9, 16.4, 13.8]
    accuracy = [76.4, 73.7, 74.5, 75.0, 72.1]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:blue'
    ax1.set_xlabel('Serialization Format')
    ax1.set_ylabel('Efficiency Score (Acc % per 1K Tokens)', color=color)
    bars = ax1.bar(formats, efficiency, color=color, alpha=0.7)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Absolute Accuracy (%)', color=color)
    line = ax2.plot(formats, accuracy, color=color, marker='o', linewidth=2, linestyle='--')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Figure 3: Format Efficiency vs Accuracy\n(Data sourced from TOON Official Benchmark Suite)')
    fig.tight_layout()
    plt.savefig('efficiency_ranking_cited.png')
    plt.close()
    print("Saved efficiency_ranking_cited.png")

def plot_model_accuracy():
    # Data from official TOON repository benchmarking (Xaviviro et al., 2024)
    # 209-Question evaluation
    models = ['Claude-Haiku', 'Gemini-3-Flash', 'GPT-5-Nano', 'Grok-4-Fast']
    toon_acc = [59.8, 96.7, 90.9, 58.4]
    json_acc = [57.4, 97.1, 89.0, 56.5]

    x = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, toon_acc, width, label='TOON', color='teal')
    rects2 = ax.bar(x + width/2, json_acc, width, label='JSON (Pretty)', color='orange')

    ax.set_ylabel('Comprehension Accuracy (%)')
    ax.set_title('Figure 4: Multi-Model Zero-Shot Comprehension (209-Q Benchmark)\n(Data sourced from TOON Official Benchmark Suite)')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()

    fig.tight_layout()
    plt.savefig('model_accuracy_cited.png')
    plt.close()
    print("Saved model_accuracy_cited.png")

if __name__ == '__main__':
    plot_efficiency_ranking()
    plot_model_accuracy()
