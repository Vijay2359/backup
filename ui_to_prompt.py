import json
import sys

def convert_ui_to_prompt(ui_json):
    prompt = {}

    node_map = {str(node["id"]): node for node in ui_json["nodes"]}

    for node_id, node in node_map.items():
        class_type = node.get("type")
        inputs = {}

        # Widgets (direct values like text, seed, width/height)
        if "widgets_values" in node:
            if class_type == "CheckpointLoaderSimple":
                inputs["ckpt_name"] = node["widgets_values"][0]
            elif class_type == "CLIPTextEncode":
                inputs["text"] = node["widgets_values"][0]
            elif class_type == "EmptyLatentImage":
                inputs["width"] = node["widgets_values"][0]
                inputs["height"] = node["widgets_values"][1]
                inputs["batch_size"] = node["widgets_values"][2]
            elif class_type == "KSampler":
                inputs["seed"] = node["widgets_values"][0]
                inputs["steps"] = node["widgets_values"][2]
                inputs["cfg"] = node["widgets_values"][6]

        # Connections (links from other nodes)
        if "inputs" in node:
            for input_def in node["inputs"]:
                link = input_def.get("link")
                if link is not None and link >= 0:
                    for l in ui_json["links"]:
                        if l[0] == link:  # found link
                            from_node = str(l[1])
                            output_index = l[2]
                            inputs[input_def["name"]] = [from_node, output_index]

        prompt[node_id] = {
            "class_type": class_type,
            "inputs": inputs
        }

    return prompt


def main(infile, outfile):
    with open(infile, "r") as f:
        ui_json = json.load(f)
    prompt_json = convert_ui_to_prompt(ui_json)
    with open(outfile, "w") as f:
        json.dump(prompt_json, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ui_to_prompt_fixed.py <ui.json> <workflow_api.json>")
    else:
        main(sys.argv[1], sys.argv[2])
