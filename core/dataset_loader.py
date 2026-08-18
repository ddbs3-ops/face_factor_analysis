import json
from pathlib import Path
from core.schemas import SelectedSample

def load_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_json_files(folder_path):
    folder = Path(folder_path)
    return sorted(folder.rglob("*.json"))

def build_image_index(image_root):
    image_root = Path(image_root)
    return {
        image_path.name: image_path
        for image_path in image_root.rglob("*.png")
    }

def is_exact_frontal_pose(pose):
    return (
        pose is not None
        and pose["yaw"] == 0
        and pose["pitch"] == 0
        and pose["roll"] == 0
    )

def select_first_frontal_samples(json_files, image_root):
    image_index = build_image_index(image_root)

    selected_ids = set()
    selected_samples = []

    for json_path in json_files:
        data = load_json(json_path)

        person_id = data["rawfile"]["id"]

        if person_id in selected_ids:
            continue

        gender = data["label_gt"]["metadata"]["gender"]
        pose = data["label_gt"]["pose"]

        if gender != "male":
            continue

        if not is_exact_frontal_pose(pose):
            continue

        image_name = data["rawfile"]["name"]
        image_path = image_index.get(image_name)

        if image_path is None:
            continue

        selected_ids.add(person_id)
        selected_samples.append(
            SelectedSample(
                image_path=image_path,
                person_id=person_id,
                gt_yaw=pose["yaw"],
                gt_pitch=pose["pitch"],
                gt_roll=pose["roll"],
            )
        )

    return selected_samples
