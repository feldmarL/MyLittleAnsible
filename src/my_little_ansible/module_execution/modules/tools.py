"""
Tools used in multiple modules.
"""

from sys import stdout
from os import path
from logging import DEBUG, INFO, WARNING, ERROR, Formatter, StreamHandler, getLogger

class CustomFormatter(Formatter):
    """Logging colored formatter
    """

    grey: str = "\x1b[38;20m"
    yellow: str = "\x1b[33;20m"
    red: str = "\x1b[31;20m"
    blue: str = "\x1b[38;5;39m"
    reset: str = "\x1b[0m"

    def __init__(self, fmt):
        super().__init__()
        self.formats = {
            DEBUG: self.blue + fmt + self.reset,
            INFO: self.grey + fmt + self.reset,
            WARNING: self.yellow + fmt + self.reset,
            ERROR: self.red + fmt + self.reset,
        }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = Formatter(log_fmt)
        return formatter.format(record)

def execute_command(sudo, client, command, host_pwd=""):
    """_summary_

    Args:
        sudo (bool): Use of sudo or not.
        client (SSHClient): _description_
        host_pwd (String): Sudo password.
        command (String): command to execute.

    Returns:
        (String, String, String): String definition of stdin, stdout and stderr.
    """
    if sudo:
        stdin, stdout_channel, stderr = client.exec_command(f'echo "{host_pwd}" | {command}')
        logger.debug('Execute command "%s" WITH sudo.\n', command)
    else:
        stdin, stdout_channel, stderr = client.exec_command(command)
        logger.debug('Execute command "%s" WITHOUT sudo.\n', command)

    stdout_str = stdout_channel.read().decode()
    stderr_str = stderr.read().decode()

    close_std(stdin, stdout_channel, stderr)

    return stdout_str, stderr_str

def close_std(stdin, stdout_channel, stderr):
    """ Close all specified std.

    Args:
        stdin (ChannelFile): stdin returned from paramiko's exe_command
        stdout_channel (ChannelFile): stdout returned from paramiko's exe_command
        stderr (ChannelFile): stderr returned from paramiko's exe_command
    """
    stdin.close()
    stdout_channel.close()
    stderr.close()

def mkpath(sftp, remote_directory):
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
        mkpath(sftp, dirname)
        sftp.mkdir(basename)
        sftp.chdir(basename)

def backup(sftp, dest, host_ip):
    """Backup remote file to /tmp folder.

    Args:
        sftp (SFTPClient): Paramiko's SFTPClient.
        dest (String): Remote file to backup.
        host_ip (String): Host ip.
    """
    try:
        tmp_dest = f"/tmp{'/'.join(dest.split('/')[:-1])}/"
        mkpath(sftp, tmp_dest)
        sftp.rename(dest, f"{tmp_dest}{dest.split('/')[-1]}")
        logger.info("Backup of %s on %s done. Backuped file can be found at %s",
                    {dest}, {host_ip}, {tmp_dest})
        return True
    except FileNotFoundError:
        logger.debug("Remote file does not exist, skipped backuping.")
        return False

logger = getLogger(__name__)
logger.setLevel(DEBUG)

stdout_handler = StreamHandler(stdout)
stdout_handler.setLevel(DEBUG)
stdout_handler.setFormatter(CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

logger.addHandler(stdout_handler)
