import docker


def create_app_image(app_instance='db_mongo'):
    client = docker.from_env()
    client.images.build(path='.', rm=True, quiet=False, tag=app_instance)
