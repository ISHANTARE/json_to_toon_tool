import os
import shutil

root_dir = os.path.dirname(os.path.abspath(__file__))

# 1. DELETE
to_delete = [
    "download_samples.py", "pytest_out.txt", "test_out.txt",
    "benchmark_results.csv", "results.csv", "real_results.csv",
    "output.toon", "sample.json", "timeseries.toon"
]

for f in to_delete:
    path = os.path.join(root_dir, f)
    if os.path.exists(path):
        os.remove(path)
        print(f"Deleted: {f}")

# 2. CREATE DIRS
research_dir = os.path.join(root_dir, "research_paper")
project_dir = os.path.join(root_dir, "project")

os.makedirs(research_dir, exist_ok=True)
os.makedirs(project_dir, exist_ok=True)

# 3. MOVE TO RESEARCH PAPER
to_research = [
    "efficiency_ranking_cited.png", "latency_comparison.png",
    "model_accuracy_cited.png", "tokens_comparison.png",
    "plot_accuracy_benchmarks.py", "plot_results.py"
]

for f in to_research:
    src = os.path.join(root_dir, f)
    dst = os.path.join(research_dir, f)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved to research_paper: {f}")

# 4. MOVE TO PROJECT
to_project = [
    "mini_toon", "web", "tests", "samples", "real_samples",
    "README.md", "server.py", "toon_cli.py", "benchmark_tokens.py", "test_llm.py"
]

for item in to_project:
    src = os.path.join(root_dir, item)
    dst = os.path.join(project_dir, item)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved to project: {item}")

print("Cleanup complete!")
