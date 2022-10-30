"""
Tools used in multiple modules.
"""

from sys import stdout

from logging import (DEBUG, ERROR, FileHandler, Formatter, StreamHandler, getLogger)

formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

stderr_handler = FileHandler("stderr.log")
stderr_handler.setLevel(ERROR)
stderr_handler.setFormatter(formatter)

stdout_handler = StreamHandler(stdout)
stdout_handler.setLevel(DEBUG)
stdout_handler.setFormatter(formatter)

logger = getLogger(__name__)
logger.setLevel(DEBUG)
logger.addHandler(stderr_handler)
logger.addHandler(stdout_handler)

def execute_command(sudo, client, host_pwd, command):
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
        logger.debug(f"Execute commande {command} WITH sudo.")
    else:
        stdin, stdout_channel, stderr = client.exec_command(f'{command}')
        logger.debug(f"Execute commande {command} WITHOUT sudo.")

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
