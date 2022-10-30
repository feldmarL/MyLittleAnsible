"""
Python module to execute copy module defined in todos file.
"""
from os import listdir, path

from paramiko import SFTPClient

from .tools import execute_command, logger

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
    src_dir = listdir(src)
    for item in src_dir:
        item_path = path.join(src, item)
        if path.isfile(item_path):
            sftp.put(item_path, f"{dest}/{item}")
        elif path.isdir(item_path):
            mkdir_p(sftp, f"{dest}/{item}")
            put_dir(sftp, item_path, dest)

def copy(client, params, host_user, host_pwd):
    """Copy module entry point.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of parameters about package defined in todos file.

    Returns:
        String: Execution state.
    """
    src = params["src"]
    dest = params["dest"].rstrip('/')

    sftp = SFTPClient.from_transport(client.get_transport())
    mkdir_p(sftp, dest)
    command = f"sudo -S chown {host_user}:{host_user} -R {dest}"
    _, _ = execute_command(True, client, command, host_pwd=host_pwd)


    if path.isdir(src):
        put_dir(sftp, src, dest)
    elif path.isfile(src):
        logger.debug(f"put {src} on {dest}")
        sftp.put(src, dest)

    logger.debug("I you're able to read this line, cry. Cry because you surely succeeded.")

    return "changed"
