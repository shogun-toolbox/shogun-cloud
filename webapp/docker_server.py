#!/usr/bin/env python
# coding=utf8

import docker
import datetime
from dateutil.tz import *
import dateutil.parser


class ContainerException(Exception):
    """
    There was some problem generating or launching a docker container
    for the user
    """
    pass


class DockerServer(object):
    def __init__(self, base_url, base_repository):
        self.docker_client = docker.Client(base_url=base_url)
        self.base_repository = base_repository

    def get_image(self, repo, tag=None):
        # TODO catch ConnectionError - requests.exceptions.ConnectionError
        if tag is None:
                tag = 'latest'
        for image in self.docker_client.images():
            repotag = image['RepoTags'][0].split(':')
            if repotag[0] == repo and repotag[1] == tag:
                return image
        raise ContainerException("No image found")
        return None

    def add_portmap(cont):
        if cont['Ports']:
            cont['portmap'] = {_['PrivatePort']: _['PublicPort'] for _ in cont['Ports']}

            # wait until services are up before returning container
            # TODO this could probably be factored better when next
            # service added
            # this should be done via ajax in the browser
            # this will loop and kill the server if it stalls on docker
            ipy_wait = True
            while ipy_wait:
                if ipy_wait:
                    try:
                        ipy_url = "http://{}:{}/".format(app.config['SERVICES_HOST'], cont['portmap'][8888])
                        requests.head(ipy_url)
                        ipy_wait = False
                    except requests.exceptions.ConnectionError:
                        pass

                time.sleep(.2)
                print 'waiting', app.config['SERVICES_HOST']
            return cont

    def get_container(self, cont_id, all=False):
        # TODO catch ConnectionError
        for cont in self.docker_client.containers(all=all):
            if cont_id in cont['Id']:
                return cont
        return None

    def get_container_uptime(self, container_id):
        started_at = dateutil.parser.parse(self.docker_client.inspect_container(container_id)['State']['StartedAt'])
        diff = datetime.datetime.now(started_at.tzinfo) - started_at

    def stop_container(self, container_id):
        self.docker_client.stop(container_id)

    def get_or_make_container(self, user):
        # TODO catch ConnectionError
        if user.container_id is None:
            image = self.get_image(self.base_repository)
            cont = self.docker_client.create_container(image['Id'],
                                                       None,
                                                       hostname="{}box".format(name.split('-')[0]),
                                                       ports=[8888])

            user.container_id = cont['Id']

        container = self.get_container(user.container_id, True)

        if container is None:
            # we may have had the container cleared out
            user.container_id = None
            print 'recurse'
            # recurse
            # TODO DANGER- could have a over-recursion guard?
            return self.get_or_make_container(user)

        if "Up" not in container['Status']:
            # if the container is not currently running, restart it
            # TODO check memory
            self.docker_client.start(container_id,
                                     port_bindings={8888: ('0.0.0.0',)})
            # refresh status
            container = self.get_container(user.container_id)
        container = self.add_portmap(container)
        return container
