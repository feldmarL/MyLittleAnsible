"""
Python module to execute copy module defined in todos file.
"""
from os import listdir, path

from .tools import logger

def mkdir_p(sftp, remote_directory):
    """ Recursively generate directory if doesn't exist on remote host.

    Args:
        sftp (SFTPClient): Paramiko's SFTPClient.
        remote_directory (string): Path to remote directory to generate.

    Returns:
    """
    if remote_directory == '/':
        sftp.chdir('/')
        return
    if remote_directory == '':
        return
    try:
        sftp.chdir(remote_directory)
    except IOError:
        dirname, basename = path.split(remote_directory.rstrip('/'))
        mkdir_p(sftp, dirname)
        sftp.mkdir(basename)
        sftp.chdir(basename)
        return

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

        if path.isfile(item_path):
            logger.debug(f"put file {item_path} on {dest}/{item}\n")
            sftp.put(item_path, f"{dest}/{item}", confirm=False)

        elif path.isdir(item_path):
            mkdir_p(sftp, f"{dest}/{dir_name}")
            put_dir(sftp, item_path, f"{dest}/{dir_name}")

def copy(client, params):
    """Copy module entry point.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of parameters about package defined in todos file.

    Returns:
        String: Execution state.
    """
    src = path.abspath(params["src"]).rstrip('/')
    dest = params["dest"].rstrip('/')
    _, item = path.split(src)

    sftp = client.open_sftp()

    if path.isdir(src):
        mkdir_p(sftp, f"{dest}/{item}")
        put_dir(sftp, src, f"{dest}/{item}")

    elif path.isfile(src):
        mkdir_p(sftp, dest)
        logger.debug(f"put single file {src} on {dest}/{item}")
        sftp.put(src, f"{dest}/{item}", confirm=False)

    return "changed"
