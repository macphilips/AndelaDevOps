import os

import docker
from docker import errors


def create_app_image(app_img):
    client = docker.from_env()
    curr_dir = os.path.dirname(os.path.abspath(__file__))

    """
    try:
         print('Creating Application Image')
        fo = open(os.path.join(curr_dir, 'env'), 'r')
    except IOError:
         print('env file is required for creating the application image')
        exit(code=404)
    else:
    """
    try:
        client.images.build(path=curr_dir, rm=True, quiet=True, tag=app_img)
        print('Image Created')
    except errors.BuildError:
        print('Error Building Application Image')
        exit(code=1)
