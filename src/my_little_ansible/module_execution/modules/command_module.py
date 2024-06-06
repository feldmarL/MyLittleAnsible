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

    logger.info("On %s, command module will execute this list of command:\n%s\n", host_ip, commands)
    logger.info("Make sure to be in debug mode to see stdout and stderr for each command.\n")

    for one_command in commands.split('\n'):
        stdout, stderr = execute_command(False, client, one_command)
        logger.info("On %s, executed command: %s\n", host_ip, one_command)

        logger.debug("While executing %s on %s, STDOUT:\n%s\n", one_command, host_ip, stdout)

        logger.debug("While executing %s on %s, first 200 STDERR chars:\n%s",
                     one_command, host_ip, stderr[:200])

    return "ok"
