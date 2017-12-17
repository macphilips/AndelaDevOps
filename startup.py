import os
import time
from sys import argv

import docker
import re
from docker import errors
from docker.types import IPAMConfig
from docker.types import IPAMPool

import app_docker
import db_docker


def load_config():
    # TODO load from configuration file
    global app_host_name, db_host_name, curr_dir, db_ipv4_address, app_ipv4_address, db_port, app_port, db_name, db_image_tag, app_image_tag, db_instance_name, app_instance_name
    db_ipv4_address = '124.25.1.5'
    app_ipv4_address = '124.25.1.6'
    db_port = 27017
    app_port = 3000
    db_name = 'andela_db'
    db_image_tag = 'db_mongo'
    app_image_tag = 'app_img'
    db_instance_name = 'db_instance'
    app_instance_name = 'app_instance'
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    db_host_name = 'db.dev-ops.local'
    app_host_name = 'app.dev-ops.local'


def create_env_file():
    file_path = os.path.join(curr_dir, 'app_docker', 'env')
    try:
        print('Setting up environment for building application image')
        port = 'PORT=%d' % app_port
        db_url = "DB_URL='mongodb://%s:%d/%s'" % (db_host_name, db_port, db_name)
        print('Creating env file: \n%s' % file_path)
        fo = open(file_path, "w")
        fo.write('%s\n%s\n' % (port, db_url))
        fo.close()
    except IOError:
        print('Unable to create %s' % file_path)


def image_exist(client, image_name):
    try:
        client.images.get(image_name)
        return True
    except errors.ImageNotFound:
        return False


# noinspection PyRedundantParentheses
def get_ip_address(db_container):
    for result in db_container.exec_run(cmd='cat /etc/hosts', stream=True):
        for line in re.split('\\n', result):
            if (db_host_name in line):
                ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)
                if (ip):
                    return ip


# noinspection PyRedundantParentheses
def get_network_interface(client):
    name = 'devops_network'
    nets = client.networks.list(names=[name])

    for n in nets:
        if (n.name == name):
            return n

    print('Creating name network interface: %s' % name)
    ipam_pool = IPAMPool(
        subnet='124.25.0.0/16',
        iprange='124.25.0.0/24',
        gateway='124.25.0.254',
    )
    ipam_config = IPAMConfig(driver='default', pool_configs=[ipam_pool])
    return client.networks.create(name, driver="bridge", ipam=ipam_config)


# noinspection PyRedundantParentheses
def run_or_start_db_container(client):
    containers = client.containers.list(all=True, filters={'name': db_instance_name})  # Get running containers

    if (containers):
        db_container = containers[0]
        if (db_container.status == 'running'):
            print('\t%s Container is running' % db_instance_name)
        else:
            print('\tStarting %s container' % db_instance_name)
            db_container.start()
            time.sleep(30)
    else:
        if (not image_exist(client, db_image_tag)):
            print('Database Image not found in local repository.\nAttempting to create Database Image.')
            build_db_img()
        try:

            print('\tRunning %s container' % db_instance_name)
            db_container = client.containers.run(db_image_tag, name=db_instance_name,
                                                 tty=True,
                                                 hostname=db_host_name,
                                                 detach=True)
            time.sleep(30)
            ip = get_ip_address(db_container)
            if ip and len(ip) == 1:
                return ip
            else:
                network_bridge = get_network_interface(client)
                network_bridge.connect(db_container, ipv4_address=db_ipv4_address)

        except docker.errors.ContainerError:
            print('Error')
        except docker.errors.ImageNotFound:
            print('Database Image not fount in Local repository.\nTry running python startup.py build-db')


# noinspection PyRedundantParentheses
def run_or_start_app_container(client, ip=[]):
    containers = client.containers.list(all=True, filters={'name': app_instance_name})  # Get running containers

    if (containers):
        app_container = containers[0]
        if (app_container.status == 'running'):
            print('\t%s Container is running' % app_instance_name)
        else:
            print('\tStarting %s container' % app_instance_name)
            app_container.start()
            time.sleep(30)
    else:
        if (not image_exist(client, app_image_tag)):
            print('Database Image not found in local repository.\nAttempting to create Application Image.')
            build_app_img()
        try:

            network_bridge = get_network_interface(client)
            print('\tRunning %s container' % app_instance_name)

            if (ip):
                address_ = {db_host_name: ip[0]}
            else:
                address_ = {db_host_name: db_ipv4_address}

            app_container = client.containers.run(app_image_tag, name=app_instance_name,
                                                  ports={'3000/tcp': 3000},
                                                  hostname=app_host_name,
                                                  extra_hosts=address_,
                                                  tty=True,
                                                  detach=True)
            if (not ip):
                network_bridge.connect(app_container
                                       # , ipv4_address=app_ipv4_address
                                       )

            """
            print('Running command')
            for line in app_container.exec_run(cmd='cat /etc/hosts', stream=True):
                print(line)
            """
        except docker.errors.ContainerError:
            print('Error')
        except docker.errors.ImageNotFound:
            print('Application Image not fount in Local repository.\nTry running python startup.py build-app')


# noinspection PyRedundantParentheses
def run(client):
    ip = run_or_start_db_container(client)
    run_or_start_app_container(client, ip)


def build_app_img():
    # path = curr_dir + '\\app_docker'
    # create_image(client=client, path=path, tag=app_image_tag)
    create_env_file()
    app_docker.create_app_image(app_image_tag)


def build_db_img():
    # path = curr_dir + '\\db_docker'
    # create_image(client=client, path=path, tag=db_image_tag)
    db_docker.create_db_image(db_image_tag)


def build_image():
    build_db_img()
    build_app_img()


# noinspection PyRedundantParentheses
def clean_container(client, instance):
    db_container = stop_container(client, instance)
    if (db_container is not None):
        print('Removing %s container' % instance)
        db_container.remove()
        print('Removed')


# noinspection PyRedundantParentheses
def stop_container(client, instance):
    containers = client.containers.list(all=True, filters={'name': instance})
    if (containers):
        db_container = containers[0]
        if (db_container.status == 'running'):
            print('Stopping %s container' % instance)
            db_container.stop()
            print('Stopped')
        return db_container


# noinspection PyGlobalUndefined,PyRedundantParentheses
def main():
    load_config()
    _client = docker.from_env()

    if (__name__ == '__main__'):
        args = (argv[1:])

        if ('clean' in args):
            clean_container(_client, db_instance_name)
            clean_container(_client, app_instance_name)

        if ('clean-db' in args):
            print('Start Application Container ')
            clean_container(_client, db_instance_name)

        if ('clean-app' in args):
            print('Start Application Container ')
            clean_container(_client, app_instance_name)

            # if ('test' in args):
            # run_test()

        if ('init' in args):
            print('-init')
            build_image()
            run(_client)
            # run_test()
            return

        if ('build' in args):  # Example usage.

            build_image()

        if ('build-app' in args):
            build_app_img()

        if ('build-db' in args):
            build_db_img()

        if ('run' in args or len(argv) == 1):
            print('-run')
            run(_client)

        if ('run-db' in args):
            print('Start Database Container ')
            run_or_start_db_container(_client)

        if ('run-app' in args):
            print('Start Application Container ')
            run_or_start_app_container(_client)

        if ('stop' in args):
            stop_container(_client, db_instance_name)
            stop_container(_client, app_instance_name)

        if ('stop-db' in args):
            print('Start Application Container ')
            stop_container(_client, db_instance_name)

        if ('stop-app' in args):
            print('Start Application Container ')
            stop_container(_client, app_instance_name)


main()
