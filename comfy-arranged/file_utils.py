import os
import time

BASE_DIR = os.path.abspath("shared")
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
MODEL_DIR = os.path.join(BASE_DIR, "models", "checkpoints")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# --- CPU patch for ComfyUI ---
CPU_PATCH = """\
# --- CPU patch for ComfyUI ---
import torch

_original_torch_device = torch.device
torch.cuda.is_available = lambda: False
torch.cuda.current_device = lambda: 0

class DummyProps:
    def __init__(self):
        self.name = "cpu"
        self.total_memory = 0
        self.major = 0
        self.minor = 0

torch.cuda.get_device_properties = lambda device=None: DummyProps()
torch.cuda.device_count = lambda: 0
torch.cuda.set_device = lambda x: None
torch.device = lambda x=None: _original_torch_device("cpu")

try:
    from main import load_extra_path_config
except ModuleNotFoundError:
    print("Skipping add_extra_model_paths: main not found")
# --------------------
"""

CPU_PATCH_FILE = os.path.join(OUTPUT_DIR, "cpu_patch.py")

# Write CPU patch once at startup
with open(CPU_PATCH_FILE, "w") as f:
    f.write(CPU_PATCH)
os.chmod(CPU_PATCH_FILE, 0o644)


def patch_generated_py(py_path):
    """Prepend CPU patch to generated Python script."""
    with open(py_path, "r") as f:
        original_code = f.read()
    patched_code = CPU_PATCH + "\n" + original_code
    with open(py_path, "w") as f:
        f.write(patched_code)
    os.chmod(py_path, 0o644)


def get_new_images(before_files, output_dir=OUTPUT_DIR, timeout=30):
    """Detect newly generated PNG files after ComfyUI run."""
    elapsed = 0
    while elapsed < timeout:
        current_files = [f for f in os.listdir(output_dir) if f.endswith(".png")]
        new_images = list(set(current_files) - set(before_files))
        if new_images:
            return [os.path.join(output_dir, f) for f in new_images]
        time.sleep(1)
        elapsed += 1
    return []

