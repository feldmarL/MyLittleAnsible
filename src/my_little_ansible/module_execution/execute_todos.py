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
    logger.info("key_path: %s\n", key_path)
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

def select_todo(todo):
    """ Launch todos execution on specified host.

    Args:
        host (Host): Host on which execute th todos list.
        todos (list(Todo)): The list of todos to execute on host.
        logger (Logger): The main created logger to log.
    """
    match todo.module:
        case "copy":
            return copy
        case "apt":
            return apt
        case "service":
            return service
        case "sysctl":
            return sysctl
        case "command":
            return command
        case "template":
            return template
        case _:
            logger.error("Unrecognized module %s, skipping.", todo.module)
            return None

def map_host_to_client(hosts):
    """Create an SSH connection to every hosts an return the SSH client
    and hosts infos mapped in a tuple.

    Args:
        hosts (list(Host)): List of hosts.

    Returns:
        list(tuple(Host, SSHClient)): List of every SSH client and hosts infos mapped in tuples.
    """
    host_to_client = []

    for host in hosts:
        for _ in range(3):
            state, client = ssh_conn(host)
            if state:
                host_to_client.append((host, client))
                break
        else:
            logger.info("Could not connect to host %s, skipping todos execution.")
            logger.error("Failed to connect to %s, skipping todos execution.", host.ip)
            logger.error("Used %s authentication.",
                         "password" if host.use_password_auth else "ssh key")

    return host_to_client

def execution(todos, hosts):
    """Todo execution entrypoint.

    Args:
        todos (list(Todo)): List of todos.
        hosts (list(Host)): List of hosts.
    """
    host_to_client = map_host_to_client(hosts)

    for index, todo in enumerate(todos):
        todo_function = select_todo(todo)
        if todo_function is None:
            continue
        for host, client in host_to_client:
            status = todo_function(client, todo.params, host.ip, host.ssh_password)
            logger.info("Done todo [%i], module: %s on %s: %s\n",
                        index, todo.module, host.ip, status.upper())
