import numpy as np
from PIL import Image


def get_preprocess_func(env_name):
    if "Breakout" in env_name:
        return _preprocess_breakout
    elif "Pacman" in env_name:
        return _preprocess_mspackman
    else:
        raise NotImplementedError(
           f"Frame processor not implemeted for {env_name}")


def _preprocess_breakout(frame):
    image = Image.fromarray(frame)
    image = image.crop((0, 34, 160, 200)).resize((96, 96))
    image_scaled = np.array(image) / 255.0
    return image_scaled.astype(np.float32)


def _preprocess_mspackman(frame):
    image = Image.fromarray(frame)
    image = image.crop((0, 0, 160, 170)).resize((96, 96))
    image_scaled = np.array(image) / 255.0
    return image_scaled.astype(np.float32)