#!/usr/bin/python3
"""Fabric script that creates and distributes an archive to web servers"""
import os
from datetime import datetime
from fabric.api import env, local, put, run, runs_once, settings

env.hosts = ['100.24.4.34', '44.201.163.226']


def do_pack():
    """Packs web_static into versions/web_static_<date>.tgz.

    Returns the archive path if it was generated, otherwise None.
    """
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    path = "versions/web_static_{}.tgz".format(stamp)
    with settings(warn_only=True):
        if local("mkdir -p versions").failed:
            return None
        print("Packing web_static to {}".format(path))
        if local("tar -cvzf {} web_static".format(path)).failed:
            return None
    return path


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


_pack_once = runs_once(do_pack)


def deploy():
    """Creates an archive (once) and deploys it to every web server.

    Returns False if no archive was created, otherwise the value
    returned by do_deploy.
    """
    archive_path = _pack_once()
    if archive_path is None:
        return False
    return do_deploy(archive_path)
