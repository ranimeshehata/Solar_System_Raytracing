import json
from pyrr import Vector3


def parse_json(path="input\scene_config.json"):
    with open(path, "r") as file:
        data = json.load(file)

    time = data["time"]
    camera_eye = Vector3(data["camera"]["position"])
    camera_target = Vector3(data["camera"]["look_at"])
    camera_up = Vector3(data["camera"]["up"])

    return time, camera_eye, camera_target, camera_up
