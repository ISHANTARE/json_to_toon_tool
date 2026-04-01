import matplotlib.pyplot as plt
import numpy as np
import os

def plot_big_o_complexity():
    # Simulate N nodes (payload size)
    N = np.linspace(10, 10000, 100)
    
    # JSON Parsing is roughly O(N) since it's a CFG Pushdown Automaton
    # C-extensions process it incredibly efficiently.
    json_time = N * 0.005 
    
    # TOON Parsing whitespace involves backtrack/state-checks. O(N log N)
    toon_time = N * np.log(N) * 0.01

    plt.figure(figsize=(10, 6))
    plt.plot(N, json_time, label='JSON (Compiled C-Extension O(N))', color='orange', linewidth=2.5)
    plt.plot(N, toon_time, label='TOON (Python State Machine O(N log N))', color='teal', linewidth=2.5)

    plt.title('Figure 5: Theoretical Parsing Latency Scaling (Big-O Complexity)')
    plt.xlabel('Payload Sequence Size (N tokens)')
    plt.ylabel('Simulated CPU Latency Factor')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Save directly in research_paper folder
    save_path = os.path.join('research_paper', 'complexity_scaling.png')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"Saved {save_path}")

def plot_financial_projections():
    queries = np.arange(0, 1_000_000_000, 100_000_000)
    
    # $0.150 per 1M tokens. 
    # JSON avg ~15,000 tokens per payload
    json_cost_per_query = (15000 / 1_000_000) * 0.150
    json_cumulative = queries * json_cost_per_query
    
    # TOON avg ~5,500 tokens per payload
    toon_cost_per_query = (5500 / 1_000_000) * 0.150
    toon_cumulative = queries * toon_cost_per_query
    
    plt.figure(figsize=(10, 6))
    
    plt.fill_between(queries, json_cumulative, toon_cumulative, color='lightgreen', alpha=0.3, label='Enterprise Capital Savings')
    plt.plot(queries, json_cumulative, label='Standard JSON API Invoice', color='red', linestyle='--', linewidth=2)
    plt.plot(queries, toon_cumulative, label='TOON Optimized API Invoice', color='green', linewidth=3)
    
    plt.title('Figure 6: RAG Cumulative API Cost Projection (GPT-4o-mini)')
    plt.xlabel('Total RAG Database Inferences (Billions)')
    plt.ylabel('Cumulative API Invoice Cost ($)')
    
    # Format X axis to show '100M', '200M' etc
    plt.xticks(queries, [f"{int(q/1_000_000)}M" for q in queries])
    
    # Format Y axis to show '$' and 'K' or 'M'
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels([f"${int(x/1000)}K" for x in current_values])

    plt.legend(loc='upper left')
    plt.grid(True, linestyle=':', alpha=0.8)
    
    save_path = os.path.join('research_paper', 'financial_projection.png')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"Saved {save_path}")

if __name__ == '__main__':
    plot_big_o_complexity()
    plot_financial_projections()
