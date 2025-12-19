import os
import uuid
from flask import request, render_template_string, send_file
from file_utils import INPUT_DIR, OUTPUT_DIR, patch_generated_py, get_new_images
from docker_utils import run_container_a, run_container_b


def init_routes(app):
    @app.route('/')
    def home():
        return """
        <h2>Upload your JSON workflow</h2>
        <form method="POST" action="/upload" enctype="multipart/form-data">
          <input type="file" name="json_file" />
          <input type="submit" value="Upload & Generate Image" />
        </form>
        """

    @app.route('/upload', methods=['POST'])
    def upload_json():
        if 'json_file' not in request.files:
            return "No file part", 400

        file = request.files['json_file']
        if file.filename == '':
            return "No selected file", 400

        # Unique job ID
        job_id = str(uuid.uuid4())
        json_filename = f"{job_id}.json"
        json_path = os.path.join(INPUT_DIR, json_filename)
        file.save(json_path)
        os.chmod(json_path, 0o644)

        py_filename = f"{job_id}.py"
        py_path = os.path.join(OUTPUT_DIR, py_filename)

        # --- Step 1: Convert JSON -> Python
        try:
            run_container_a(json_filename, py_filename)
        except Exception as e:
            return f"<h3 style='color:red;'>Container A failed:</h3><pre>{str(e)}</pre>"

        # Apply CPU patch
        patch_generated_py(py_path)

        # Existing images before generation
        existing_images = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png")]

        # --- Step 2: Run Comfy (Python -> Image)
        try:
            run_container_b(py_filename)
        except Exception as e:
            return f"<h3 style='color:red;'>Container B failed:</h3><pre>{str(e)}</pre>"

        # Detect newly generated images
        generated_images = get_new_images(existing_images)
        if not generated_images:
            return "<h3 style='color:red;'>Image generation failed</h3>"

        image_path = generated_images[0]
        image_filename = os.path.basename(image_path)

        return render_template_string(f"""
        <h2>✅ Image Generated Successfully</h2>
        <img src="/output/{image_filename}" 
             style="max-width:80%; border:2px solid #ccc; border-radius:8px;" />
        <br><br>
        <a href="/">⬅️ Generate another</a>
        """)

    @app.route('/output/<path:filename>')
    def serve_output(filename):
        """Serve generated image files."""
        return send_file(os.path.join(OUTPUT_DIR, filename))
