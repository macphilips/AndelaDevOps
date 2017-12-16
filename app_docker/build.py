import os

import docker
from docker import errors


def create_app_image(app_img):
    try:
        client = docker.from_env()
        print('Creating Application Image')
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        client.images.build(path=curr_dir, rm=True, quiet=True, tag=app_img)
        print('Image Created')
    except errors.BuildError:
        print('Error Building Application Image')
