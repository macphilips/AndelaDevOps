import os

import docker
from docker import errors


def create_db_image(db_image):
    try:
        client = docker.from_env()
        print('Creating Database Image')
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        client.images.build(path=curr_dir, rm=True, quiet=False, tag=db_image)
        print('Image created.')
    except errors.BuildError:
        print('Error Building Database Image')
        exit(code=2)
