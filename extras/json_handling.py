import json


def load_json(json_path):
    try:
        with open(json_path, "r") as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        print("No saved data found")
        return None


def save_json(data, json_path):
    with open(json_path, "w") as file:
        json.dump(data, file, indent=2)
