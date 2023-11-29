"""
Python module to connect to remost host and launch todo execution on it.
"""

from os import path
from socket import error as SocketError

from paramiko import (AuthenticationException, AutoAddPolicy,
                        BadHostKeyException, RSAKey, SSHClient, SSHException)

from .modules.tools import logger
from .modules.apt_module import apt
from .modules.copy_module import copy
from .modules.service_module import service
from .modules.sysctl_module import sysctl
from .modules.command_module import command
from .modules.template_module import template

def ssh_conn(host):
    """ Initiate SSH connexion with specified host.

    Args:
        host (Host): Host type from data_classes containing every infos needed to connect.

    Returns:
        SSHClient: The SSH client we need to use to send commands to distant host.
    """
    key_path = path.abspath(host.ssh_private_key_path)
    logger.info(f"key_path: {key_path}\n")
    if path.isfile(key_path):
        key = RSAKey.from_private_key_file(key_path)
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())

    state = False

    try:
        if host.use_password_auth:
            logger.debug("Trying to connect using password.\n")
            client.connect(host.ip, host.port, host.ssh_user, host.ssh_password)
            state = True
        else:
            logger.debug("Trying to connect using pkey.\n")
            client.connect(host.ip, host.port, host.ssh_user, pkey = key)
            state = True
    except BadHostKeyException:
        logger.error("The server's host key could not be verified.")
    except AuthenticationException:
        logger.error("Authentication failed.")
    except SSHException:
        logger.error("Error while connecting or establishing an SSH session.")
    except SocketError:
        logger.error("Socket error occurred while connecting.")

    return state, client


def execution(host, todos):
    """ Launch todos execution on specified host.

    Args:
        host (Host): Host on which execute th todos list.
        todos (list(Todo)): The list of todos to execute on host.
        logger (Logger): The main created logger to log.
    """
    for _ in range(3):
        state, client = ssh_conn(host)
        if state:
            break
    else:
        logger.info(f"Could not connect to host {host.ip}, skipping todos execution.")
        logger.error(f"Failed to connect to {host.ip}, skipping todos execution.")
        logger.error(f"Used password authentication: {host.use_password_auth}.")
        return


    for index, todo in enumerate(todos):
        match todo.module:
            case "copy":
                status = copy(client, todo.params)
            case "apt":
                status = apt(client, todo.params, host.ssh_password, host.ip)
            case "service":
                status = service(client, todo.params, host.ssh_password, host.ip)
            case "sysctl":
                status = sysctl(client, todo.params, host.ssh_password, host.ip)
            case "command":
                status = command(client, todo.params, host.ip)
            case "template":
                status = template(client, todo.params, host.ip)
            case _:
                logger.error(f"Unrecognized module {todo.module}, skipping.")
                return

        logger.info(f"Done todo {index}, module: {todo.module} on {host.ip}: {status.upper()}\n")

    client.close()
