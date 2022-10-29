"""
Python module to execute copy module defined in todos file.
"""
from os import listdir, path

from paramiko import SFTPClient

#common.logging.basicConfig(level=common.DEBUG)

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

def copy(client, params, logger):
    """Copy module entry point.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (_type_): List of parameters about package defined in todos file.
        logger (_type_): The main created logger to log.

    Returns:
        String: Execution state.
    """
    src = params["src"]
    dest = params["dest"].rstrip('/')

    sftp = SFTPClient.from_transport(client.get_transport())
    mkdir_p(sftp, dest)

    if path.isdir(src):
        put_dir(sftp, src, dest)
    elif path.isfile(src):
        sftp.put(src, dest)

    logger.debug("When you'll be able to read this line, cry. Cry because you surely succeeded.")

    return "changed"
