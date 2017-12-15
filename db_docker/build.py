import docker


def create_app_image(app_instance='app'):
    client = docker.from_env()
    client.images.build(path='.', rm=True, quiet=False, tag=app_instance)
