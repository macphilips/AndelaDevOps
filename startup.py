import os
import time

import docker
from docker.types import IPAMConfig
from docker.types import IPAMPool


def create_env_file():
    # Open a file
    fo = open("%s\\env" % path_to_app_dockerfile, "w")
    fo.write('%s%s' % (port, db_url))
    # Close opend file
    fo.close()


def create_network():
    global net
    ipam_pool = IPAMPool(
        subnet='124.25.0.0/16',
        #   subnet='124.42.0.0/16',
        iprange='124.25.0.0/24',
        #   iprange='124.42.0.0/24',
        gateway='124.25.0.254',
        # gateway='124.42.0.254',
    )
    ipam_config = IPAMConfig(driver='default', pool_configs=[ipam_pool])
    return client.networks.create('isolated_nw', driver="bridge", ipam=ipam_config)


db_ipv4_address = '124.25.1.5'
db_port = 27017
app_port = 3000
db_name = 'andela_db'

curr_dir = os.path.dirname(os.path.abspath(__file__))

path_to_db_dockerfile = '%s\%s' % (curr_dir, 'db_docker')
path_to_app_dockerfile = '%s\%s' % (curr_dir, 'app_docker')

file_db_dockerfile = '%s\%s\%s' % (curr_dir, 'db_docker', 'Dockerfile')
file_app_dockerfile = '%s\%s\%s' % (curr_dir, 'app_docker', 'Dockerfile')

port = 'PORT=%d\n' % app_port
db_url = "DB_URL='mongodb://%s:%d/%s'\n" % (db_ipv4_address, db_port, db_name)

client = docker.from_env()

create_env_file()

db_image_tag = 'db_mongo'
app_instance = 'app'
"""

db_file_obj = open(file_db_dockerfile, 'r')
client.images.build(fileobj=db_file_obj, rm=True, tag=db_image_tag)
db_file_obj.close()

app_file_obj = open(file_app_dockerfile, 'r')
client.images.build(fileobj=app_file_obj, rm=True, tag=app_instance)
app_file_obj.close()
"""

net = create_network()

db_container = client.containers.run(db_image_tag, name='db_instance', ports={'%d/tcp' % db_port: db_port}, tty=True,
                                     detach=True)

net.connect(db_container, ipv4_address=db_ipv4_address)

time.sleep(20)

app_container = client.containers.run(app_instance, name='app_instance', ports={'%d/tcp' % app_port: app_port},
                                      tty=True, detach=True)
net.connect(app_container)
