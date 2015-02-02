import os

app_root_path = os.path.dirname(__file__)

def path(*components):
    return os.path.join(app_root_path, *components)
