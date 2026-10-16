#!/usr/bin/python3
"""Fabric script that distributes an archive to the web servers"""
import os
from fabric.api import env, put, run, settings

env.hosts = ['100.24.4.34', '44.201.163.226']


def do_deploy(archive_path):
    """Deploys the archive to the web servers.

    Returns False if the archive does not exist or any step fails,
    otherwise True.
    """
    if not os.path.isfile(archive_path):
        return False
    name = os.path.basename(archive_path)
    base = os.path.splitext(name)[0]
    release = "/data/web_static/releases/{}".format(base)
    commands = [
        "rm -rf {}".format(release),
        "mkdir -p {}/".format(release),
        "tar -xzf /tmp/{} -C {}/".format(name, release),
        "rm /tmp/{}".format(name),
        "mv {0}/web_static/* {0}/".format(release),
        "rm -rf {}/web_static".format(release),
        "rm -rf /data/web_static/current",
        "ln -s {}/ /data/web_static/current".format(release),
    ]
    try:
        with settings(warn_only=True):
            if put(archive_path, "/tmp/{}".format(name)).failed:
                return False
            for command in commands:
                if run(command).failed:
                    return False
    except Exception:
        return False
    print("New version deployed!")
    return True
