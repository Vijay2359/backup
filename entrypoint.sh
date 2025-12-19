#!/bin/bash
set -e

INPUT_FILE="/workspace/ComfyUI/workflow_api.json"
OUTPUT_FILE="/workspace/ComfyUI/output/workflow_api.py"
OUTPUT_DIR="/workspace/ComfyUI/output"

CPU_PATCH=$(cat << 'EOF'
# --- CPU patch for ComfyUI ---
import torch

# Save original torch.device
_original_torch_device = torch.device

# Disable CUDA entirely
torch.cuda.is_available = lambda: False
torch.cuda.current_device = lambda: 0

# Create a Dummy CUDA properties object with expected attributes
class DummyProps:
    def __init__(self):
        self.name = "cpu"
        self.total_memory = 0
        self.major = 0  # CUDA compute capability major
        self.minor = 0  # CUDA compute capability minor

torch.cuda.get_device_properties = lambda device=None: DummyProps()
torch.cuda.device_count = lambda: 0
torch.cuda.set_device = lambda x: None

# Patch torch.device to always return CPU
torch.device = lambda x=None: _original_torch_device("cpu")
# -----------------------
EOF
)

prepend_cpu_patch() {
  echo "$CPU_PATCH" | cat - "$1" > "$1.patched"
  mv "$1.patched" "$1"
  echo "✅ CPU patch applied to $1"
}

case "$1" in
  convert)
    echo "👉 Running JSON → Python conversion"
    shift
    python /workspace/ComfyUI/custom_nodes/ComfyUI-to-Python-Extension/comfyui_to_python.py \
      --input_file "$INPUT_FILE" \
      --output_file "$OUTPUT_FILE" \
      "$@"
    prepend_cpu_patch "$OUTPUT_FILE"
    echo "✅ Conversion complete → $OUTPUT_FILE"
    ;;
  
  run)
    echo "👉 Running generated Python workflow"
    shift
    python "$OUTPUT_FILE" "@" 
    echo "✅ Workflow execution complete. Images should be in $OUTPUT_DIR"
    ;;
  
  convert-run)
    echo "👉 Converting JSON → Python..."
    python /workspace/ComfyUI/custom_nodes/ComfyUI-to-Python-Extension/comfyui_to_python.py \
      --input_file "$INPUT_FILE" \
      --output_file "$OUTPUT_FILE"
    prepend_cpu_patch "$OUTPUT_FILE"
    echo "✅ Conversion done and CPU patch applied"
    
    echo "👉 Running workflow..."
    python "$OUTPUT_FILE"
    echo "✅ Images stored in $OUTPUT_DIR"
    ;;
  
  *)
    echo "Usage:"
    echo "  comfi-both convert        # Only convert JSON → Python"
    echo "  comfi-both run            # Only run generated Python"
    echo "  comfi-both convert-run    # Convert + Run + Save images"
    exit 1
    ;;
esac
