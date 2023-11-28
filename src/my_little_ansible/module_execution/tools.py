"""
Tools used in multiple modules.
"""

from sys import stdout
from logging import (DEBUG, INFO, WARNING, ERROR, Formatter, StreamHandler, getLogger)

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
        self.fmt = fmt
        self.formats = {
            DEBUG: self.blue + self.fmt + self.reset,
            INFO: self.grey + self.fmt + self.reset,
            WARNING: self.yellow + self.fmt + self.reset,
            ERROR: self.red + self.fmt + self.reset,
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
        logger.debug(f'Execute command "{command}" WITH sudo.\n')
    else:
        stdin, stdout_channel, stderr = client.exec_command(f'{command}')
        logger.debug(f'Execute command "{command}" WITHOUT sudo.\n')

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

logger = getLogger(__name__)
logger.setLevel(DEBUG)

stdout_handler = StreamHandler(stdout)
stdout_handler.setLevel(DEBUG)
stdout_handler.setFormatter(CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

logger.addHandler(stdout_handler)
