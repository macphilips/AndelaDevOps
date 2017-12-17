# Andela DevOps Assessment
Andela Learning Community powered by Microsoft Advanced (DevOps) Track Assessment

## Challenge

This challenge is to give us an idea of your DevOps experience.

Given an application source code in a git repository, write a script (bash, python, etc) to set up application and database on different nodes to communication using any technology containers or VM (virtual machine).

Essentially we should be able to run said script and have the setup and application running properly locally.

To achieve this we have provided you a working [source code](https://github.com/macphilips/UserManager) to perform CRUD (create, read, update and delete) operation.
## Requirements
* Python 2.7+
* Docker
* Docker SDK for Python

## Installation
Visit [Docker's website](https://docs.docker.com/engine/installation/) to download and install docker on your PC.

Install [Docker SDK](https://github.com/docker/docker-py) using pip
```
$ pip install docker
$ pip install pypiwin32
```

## Usage
Assuming you've correctly installed Docker on your PC and Docker SDK.

```
$ git clone https://github.com/macphilips/AndelaDevOps
$ cd AndelaDevOps
$ python startup.py [options]
```
### Options
* ``run`` (default): This option is used run the create and start the both the application and database containers, or start the containers if it has been created. Use ``run-app`` to run the application container only and ``run-db`` to run database.
* ``build``: This option is used to build the docker image file both the application server and database. Use ``build-app`` to build application server image file only and ``build-db`` for database image file.
* ``init``: This option is used to setup, build, and run the Application Server (NodeJS) and Database (MongoDB) Image. The script first cleans any running instance of the application server and database. then it builds image files for the application server and database. Then create and starts container for the application server and database.
* ``stop``: Stops running application server and database container. Use ``stop-app`` to stop application server container and ``stop-db`` for database container.
* ``clean``: Stops running application server and database container. Use ``clean-app`` to stop application server container and ``clean-db`` for database container.


## Issues
In case you run into this error while try to build Docker images using the SDK

````
$ python startup.py init

Docker.errors.DockerException: Credentials store error: StoreError('docker-credential-wincred not installed or not available in PATH',)}
````
### Fix

To fix this error locate ``%USERPROFILE%/.docker/config.json`` OR `` C:\Users\<username>\.docker\config.json`` and Remove the line `` "credsStore": "wincred"``. [Click here](https://github.com/docker/docker-credential-helpers/issues/24), for more info
