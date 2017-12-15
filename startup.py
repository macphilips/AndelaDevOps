import httplib
import os
import time
import urllib

import docker
from docker.types import IPAMConfig
from docker.types import IPAMPool

import app_docker
import db_docker

db_ipv4_address = '124.25.1.5'
app_ipv4_address = '124.25.1.6'
db_port = 27017
app_port = 3000
db_name = 'andela_db'

curr_dir = os.path.dirname(os.path.abspath(__file__))
path_to_app_dockerfile = '%s\%s' % (curr_dir, 'app_docker')

port = 'PORT=%d\n' % app_port
db_url = "DB_URL='mongodb://%s:%d/%s'\n" % (db_ipv4_address, db_port, db_name)

db_image_tag = 'db_mongo'
app_instance = 'app'


def create_env_file():
    # Open a file
    fo = open("%s\\env" % path_to_app_dockerfile, "w")
    fo.write('%s%s' % (port, db_url))
    # Close opend file
    fo.close()


# noinspection PyRedundantParentheses
def create_network(client):
    name = 'isolated_nw'
    nets = client.networks.list(names=[name])

    for n in nets:
        if (n.name == 'isolated_nw'):
            print('Network %s bridge already exists' % name)
            return n

    print('Creating name network bridge: %s' % name)
    ipam_pool = IPAMPool(
        subnet='124.25.0.0/16',
        #   subnet='124.42.0.0/16',
        iprange='124.25.0.0/24',
        #   iprange='124.42.0.0/24',
        gateway='124.25.0.254',
        # gateway='124.42.0.254',
    )
    ipam_config = IPAMConfig(driver='default', pool_configs=[ipam_pool])
    return client.networks.create(name, driver="bridge", ipam=ipam_config)


# noinspection PyRedundantParentheses
def run_or_start_db_container(client, network_bridge):
    containers = client.containers.list()
    db_container = None
    db_instance_name = 'db_instance'
    for container in containers:
        if (container.name == db_instance_name):
            print ('\t%s Container is running' % db_instance_name)
            return

    containers = client.containers.list(all=True)

    for container in containers:
        if (container.name == db_instance_name):
            print ('\t%s Container has been stopped' % db_instance_name)
            db_container = container
            break

    if db_container is None:
        print ('\tRunning %s container' % db_instance_name)
        db_container = client.containers.run(db_image_tag, name=db_instance_name, ports={'%d/tcp' % db_port: db_port},
                                             tty=True,
                                             detach=True)

        network_bridge.connect(db_container, ipv4_address=db_ipv4_address)
        time.sleep(30)
    else:
        print ('\tStarting %s container' % db_instance_name)
        db_container.start()
        time.sleep(30)


# noinspection PyRedundantParentheses
def run_or_start_app_container(client, network_bridge):
    containers = client.containers.list()
    app_container = None
    app_instance_name = 'app_instance'

    for container in containers:
        if (container.name == app_instance_name):
            print ('\t%s Container is running' % app_instance_name)
            return

    containers = client.containers.list(all=True)

    for container in containers:
        if (container.name == app_instance_name):
            app_container = container

            print ('\t%s Container has been stopped' % app_instance_name)
            break

    if app_container is None:
        print ('\tRunning %s container' % app_instance_name)
        app_container = client.containers.run(app_instance, name=app_instance_name,
                                              ports={'%d/tcp' % app_port: app_port},
                                              tty=True, detach=True)

        network_bridge.connect(app_container, ipv4_address=app_ipv4_address)
    else:
        print ('\tStarting %s container' % app_instance_name)
        app_container.start()


# noinspection PyRedundantParentheses
def create_and_wire_container(client, network_bridge):
    run_or_start_db_container(client, network_bridge)
    run_or_start_app_container(client, network_bridge)


def build_image():
    db_docker.build.create_app_image()
    app_docker.build.create_app_image()


def run_test():
    host = 'localhost'
    endpoint = 'users'
    data_param = {
        'name': 'Morolari Titilope',
        'email': 'tmorolari@gmail.com',
        'github': 'https://github.com/macphilips'
    }
    endpoint_ = 'http://%s:%d/%s' % (host, app_port, endpoint)
    print endpoint_
    params = urllib.urlencode(data_param)
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = httplib.HTTPConnection(endpoint_)
    conn.request("GET", "", params, headers)
    response = conn.getresponse()
    print response.status, response.reason
    data = response.read()
    print data
    conn.close()


def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    print argv
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
        print argv
    return opts


# noinspection PyGlobalUndefined,PyRedundantParentheses
def main():
    _client = docker.from_env()
    _network_bridge = create_network(_client)

    if __name__ == '__main__':

        from sys import argv

        myargs = (argv[1:])
        if ('-init' in myargs):
            print ('-init')
            create_env_file()
            build_image()
            create_and_wire_container(_client, _network_bridge)
            run_test()
            return
        if ('-build' in myargs):  # Example usage.
            create_env_file()
            build_image()
        if ('-run' in myargs):
            print ('-run')
            create_and_wire_container(_client, _network_bridge)
        if ('-test' in myargs):
            run_test()


main()
