"""
Python module to execute copy module defined in todos file.
"""
from os import listdir, path

from .tools import logger, mkpath, backup

def put_dir(sftp, src, dest):
    """ Function to send whole directory to remote host and destination.

    Args:
        sftp (SFTPClient): Paramiko's SFTPClient.
        src (String): Source of directory to send to remote host.
        dest (String): Destination on remote host where to send directory.
    """
    _, dir_name = path.split(src)
    src_dir = listdir(src)

    for item in src_dir:
        item_path = path.join(src, item)

        if path.isdir(item_path):
            mkpath(sftp, f"{dest}/{dir_name}")
            put_dir(sftp, item_path, f"{dest}/{dir_name}")

        else:
            logger.debug("Pushing file %s to %s/%s\n", item_path, dest, item)
            sftp.put(item_path, f"{dest}/{item}", confirm = False)


def copy(client, params, host_ip, _):
    """Copy module entry point.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of parameters about package defined in todos file.
        host_ip (String): Host ip on which execute action.

    Returns:
        String: Execution state.
    """

    src = path.abspath(params["src"]).rstrip('/')
    dest = params["dest"].rstrip('/')
    _, item = path.split(src)

    sftp = client.open_sftp()

    if "backup" not in params.keys():
        logger.info("Copy module initialized with default backup value set to False.")
    elif params["backup"]:
        backup(sftp, f"{dest}/{item}", host_ip)

    try:
        if path.isdir(src):
            mkpath(sftp, f"{dest}/{item}")
            put_dir(sftp, src, dest)

        else:
            mkpath(sftp, dest)
            logger.debug("Put single file %s on %s/%s", src, dest, item)
            sftp.put(src, f"{dest}/{item}", confirm = False)

    except IOError:
        logger.info("Error occured while creating remote directory or puting file to remote host. "
                    "User way not have the rights.")
        logger.error("Error occured while creating remote directory or puting file to remote host. "
                    "User way not have the rights.")
        sftp.close()
        return "ko"

    sftp.close()
    return "changed"
