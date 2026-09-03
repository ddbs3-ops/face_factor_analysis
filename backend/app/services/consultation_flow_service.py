import json
from pathlib import Path


FLOW_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "consultation_flow.json"
)


def load_consultation_flow():
    with FLOW_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)