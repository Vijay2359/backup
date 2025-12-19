import json
from pathlib import Path
import comfy.utils

# 1. Load workflow JSON
workflow_file = Path("my_workflow.json")
with open(workflow_file, "r") as f:
    workflow = json.load(f)

# 2. Run the workflow
results = comfy.utils.load_and_run(workflow)

# 3. Save the outputs
output_dir = Path("outputs_from_script")
output_dir.mkdir(exist_ok=True)

for i, result in enumerate(results):
    # If it's an image (ComfyUI "SaveImage" node output)
    if hasattr(result, "save"):
        save_path = output_dir / f"output_{i}.png"
        result.save(save_path)
        print(f"Saved image: {save_path}")
