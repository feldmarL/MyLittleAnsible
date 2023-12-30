"""
Python module to execute command module defined in todos file.
"""

from .tools import execute_command, logger

def command(client, params, host_ip, _):
    """Execute command on remote host.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of todo's params extracted from todos file.
        host_ip (String): Host ip.
    """
    commands = params["command"]

    logger.info(f"On {host_ip}, command module will execute this list of command:\n{commands}\n")
    logger.info("Make sure to be in debug mode to see stdout and stderr for each command.\n")

    for one_command in commands.split('\n'):
        stdout, stderr = execute_command(False, client, one_command)
        logger.info(f"On {host_ip}, executed command: {one_command}\n")

        logger.debug(f"While executing {one_command} on {host_ip}, STDOUT:")
        logger.debug(f"{stdout}\n")

        logger.debug(f"While executing {one_command} on {host_ip}, first 200 STDERR "
                     f"chars:\n{stderr[:200]}")

    return "ok"
