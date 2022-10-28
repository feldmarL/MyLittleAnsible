from sys import stdout
from os import path, system

from paramiko import SSHClient, AutoAddPolicy, RSAKey, BadHostKeyException, AuthenticationException, ssh_exception, common
#common.logging.basicConfig(level=common.DEBUG)
from socket import error as SocketError

from logging import Formatter, FileHandler, StreamHandler, getLogger, INFO, DEBUG, ERROR

from .copy_module import copy
from .apt_module import apt

def ssh_conn(host, logger):
    """Initiate SSH connexion with specified host.

    Args:
        host (Host): Host type from data_classes containing every infos needed to connect.

    Returns:
        SSHClient: The SSH client we need to use to send commands to distant host.
    """
    key_path = path.abspath(host.ssh_private_key_path)
    logger.info(f"key_path: {key_path}")
    if path.isfile(key_path):
        key = RSAKey.from_private_key_file(key_path)
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    
    try:
        if host.auth:
            logger.debug("Trying to connect using password.")
            client.connect(host.ip, host.port, host.ssh_user, host.ssh_password)
        else:
            logger.debug("Trying to connect using pkey.")
            client.connect(host.ip, host.port, host.ssh_user, pkey = key)
    except BadHostKeyException:
        logger.error("The server’s host key could not be verified.")
    except AuthenticationException:
        logger.error("Authentication failed.")
    except ssh_exception:
        logger.error("There was any error not concerning authentication or private key while connecting or establishing an SSH session.")
    except SocketError:
        logger.error("Socket error occurred while connecting.")
    finally:
        return client


def execution(host, todos, logger):
    client = ssh_conn(host, logger)

    for index, todo in enumerate(todos):
        match todo.module:
            case "copy":
                status = copy(client, todo.params, logger)
                logger.info(f"Done todo number {index}, status: {status}")
            case "apt":
                status = apt(client, todo.params, host.ssh_password, host.ip, logger)
                logger.info(f"Done todo number {index}, status: {status}")

    client.close()