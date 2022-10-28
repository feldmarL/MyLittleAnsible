from sys import stdout
from os import listdir, path

from paramiko import SFTPClient, AutoAddPolicy, RSAKey, BadHostKeyException, AuthenticationException, ssh_exception, common
#common.logging.basicConfig(level=common.DEBUG)

def mkdir_p(sftp, remote_directory):
    """Recursively generate directory if doesn't exist on remote host.

    Args:
        sftp (SFTPClient): Paramiko's SFTPClient.
        remote_directory (string): Path to remote directory to generate.

    Returns:
        bool: True if any folder is created on remote host.
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
        return True
            
def put_dir(sftp, src, dest):
    src_dir = listdir(src)
    for item in src_dir:
        item_path = path.join(src, item)
        if path.isfile(item_path):
            sftp.put(item_path, f"{dest}/{item}")
        elif path.isdir(item_path):
            mkdir_p(sftp, f"{dest}/{item}")
            put_dir(sftp, item_path, dest)

def copy(client, params, logger):
    src = params["src"]
    dest = params["dest"].rstrip('/')

    sftp = SFTPClient.from_transport(client.get_transport())
    mkdir_p(sftp, dest)

    if path.isdir(src):
        put_dir(sftp, src, dest)
    elif path.isfile(src):
        sftp.put(src, dest)

    return "changed"