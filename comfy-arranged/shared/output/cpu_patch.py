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
