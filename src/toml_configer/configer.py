import pathlib

import rtoml

default_permission_file_path = pathlib.Path("permissions.per")


def _load_permissions(permission_file_path: str):
    permissions = {}
    if not pathlib.Path(permission_file_path).exists():
        open(permission_file_path, "x").close()

    with open(permission_file_path, "r") as f:
        for line in f.read().replace(" ", "").split("\n"):
            if line != "":
                key, value = line.split("=")
                permissions.update({key: value})
    return permissions


def _get_permission(permissions: dict, key: str):
    if key in permissions:
        return permissions[key].split(",")
    else:
        return "r"


def load(config_file_path: str):
    with open(config_file_path, "r") as f:
        config = rtoml.load(f)
    if "permissions" not in config:
        print("Warning: No permissions file found. Creating default permissions.")
        if not default_permission_file_path.exists():
            open(default_permission_file_path, "w").close()
        config.update({"permissions": {"file": str(default_permission_file_path)}})
        save(config, config_file_path)
    elif "file" not in config["permissions"]:
        print("Warning: No permissions file found. Creating default permissions.")
        if not default_permission_file_path.exists():
            open(default_permission_file_path, "w").close()
        config["permissions"].update({"file": str(default_permission_file_path)})
        save(config, config_file_path)
    return config


def save(config: dict, config_file_path: str):
    with open(config_file_path, "w") as f:
        rtoml.dump(config, f)
    return config


def _generate_list_tree(config: list, depth=0, out="", space_count=50):
    for item in config:
        if type(item) == dict:
            out += f"{'   ' * depth}- {config.index(item)}: \n"
            out = _generate_dict_tree(item, depth + 1, out, space_count)
        elif type(item) == list:
            out += f"{'   ' * depth}- {config.index(item)}: \n"
            out = _generate_list_tree(item, depth + 1, out, space_count)
        else:
            line = f"{'   ' * depth}- {item} \n"
            out += line
    return out


def _generate_dict_tree(config: dict, depth=0, out="", space_count=50):
    for key, value in config.items():
        if type(value) == dict:
            out += f"{'   ' * depth}- {key}: \n"
            out = _generate_dict_tree(value, depth + 1, out, space_count)
        elif type(value) == list:
            out += f"{'   ' * depth}- {key}: \n"
            out = _generate_list_tree(value, depth + 1, out, space_count)
        else:
            line = f"{'   ' * depth}- {key}: $t$ {value} \n"
            out += line.replace(
                "$t$", " " * (space_count - len(line) + len(str(value)))
            )
    return out


def get(config: dict, key: str = "", generate_tree: bool = False):
    key = "config." + key
    if key == "config.":
        key = "config"
    key_parts = key.split(".")
    prev = config
    for part in key_parts:
        if part in prev:
            prev = prev[part]
        else:
            exit(f"Error in get: Key {key} not found.")
    c = prev

    if generate_tree:
        if type(c) == dict:
            return _generate_dict_tree(c)
        elif type(c) == list:
            return _generate_list_tree(c)

    return c


def set(config: dict, key: str, value: str):
    permissions = _load_permissions(config["permissions"]["file"])

    key = "config." + key
    if key == "config.":
        key = "config"
    key_parts = key.split(".")
    prev = config
    path = ""
    for part in key_parts[:-1]:
        path += f"{part}."
        if part not in prev:
            if "a" not in _get_permission(permissions, path[:-1]):
                exit(
                    f"Error in set: You dont have this permission - '{path[:-1]} = a'."
                )
            prev.update({part: {}})
        prev = prev[part]

    if key_parts[-1] in prev:
        if "w" not in _get_permission(permissions, key):
            exit(f"Error in set: You dont have this permission - '{key} = w'.")
        prev[key_parts[-1]] = value
    else:
        if "a" not in _get_permission(permissions, path[:-1]):
            exit(f"Error in set: You dont have this permission - '{path[:-1]} = a'.")
        prev.update({key_parts[-1]: value})

    return config


def remove(config: dict, key: str):
    permissions = _load_permissions(config["permissions"]["file"])

    key = "config." + key
    if key == "config.":
        key = "config"
    key_parts = key.split(".")
    prev = config
    for part in key_parts[:-1]:
        if part in prev:
            prev = prev[part]
        else:
            exit(f"Error in remove: Key {key} not found.")

    if key_parts[-1] in prev and type(prev) == dict:
        if "d" not in _get_permission(permissions, key):
            exit(f"Error in delete: You dont have this permission - '{key} = d'.")
        prev.pop(key_parts[-1])
    else:
        exit(f"Error in remove: Key {key} not found.")

    return config
