import docker
import os
from file_utils import BASE_DIR, OUTPUT_DIR, MODEL_DIR

client = docker.from_env()
HOST_UID = os.getuid()
HOST_GID = os.getgid()

# 👇 Use your Docker Hub image names here
CONVERT_JSON_IMAGE = "vijay2359/convert-json-py:latest"
COMFY_RUNNER_IMAGE = "vijay2359/comfy-runner:latest"


def run_container_a(json_filename, py_filename):
    """Run Container A: Convert JSON -> Python"""
    client.containers.run(
        CONVERT_JSON_IMAGE,
        command=[
            "--input_file", f"/shared/input/{json_filename}",
            "--output_file", f"/shared/output/{py_filename}",
            "--queue", "1"
        ],
        volumes={
            BASE_DIR: {"bind": "/shared", "mode": "rw"}
        },
        user=f"{HOST_UID}:{HOST_GID}",
        remove=True
    )


def run_container_b(py_filename):
    """Run Container B: Execute Python -> Generate image"""
    client.containers.run(
        COMFY_RUNNER_IMAGE,
        command=[
            "bash", "-c",
            # Run CPU patch first, then generated Python file
            f"python /workspace/ComfyUI/output/cpu_patch.py && python /workspace/ComfyUI/output/{py_filename}"
        ],
        volumes={
            # Mount output folder where Python + images exist
            OUTPUT_DIR: {"bind": "/workspace/ComfyUI/output", "mode": "rw"},

            # ✅ Mount the entire checkpoints directory
            MODEL_DIR: {"bind": "/workspace/ComfyUI/models/checkpoints", "mode": "ro"},
        },
        user=f"{HOST_UID}:{HOST_GID}",
        remove=True
    )
