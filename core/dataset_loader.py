import json
from pathlib import Path


def load_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data

def find_json_files(folder_path):
    folder = Path(folder_path)

    return list(folder.rglob("*.json"))

def is_frontal_pose(pose):
    if pose is None:
        return False

    return (
        abs(pose["yaw"]) <= 10
        and abs(pose["pitch"]) <= 10
        and abs(pose["roll"]) <= 10
    )

def find_image_path(data, image_root):
    image_name = data["rawfile"]["name"]

    image_root = Path(image_root)

    matches = list(image_root.rglob(image_name))
    if len(matches) == 0:
        return None
    
    return matches[0]



def is_target_sample(data):
    gender = data["label_gt"]["metadata"]["gender"]
    expression = data["label_gt"]["exp"]
    pose = data["label_gt"]["pose"]

    return (gender == "male" 
        and expression == "none"
        and is_frontal_pose(pose))



