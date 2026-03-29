import yaml
import os


def load_config(filename=None):
    if filename is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(current_dir, "..", "config", "config.yaml")

    with open(filename, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            return config
        except yaml.YAMLError as exc:
            print(exc)


app_config = load_config()
