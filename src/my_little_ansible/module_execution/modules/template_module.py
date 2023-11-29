"""
Python module to render Jinja2 template on host.
"""

from .tools import execute_command, logger

def teplate(client, params, host_ip):
    """Execute command on remote host.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of parameters about package defined in todos file.
        host_ip (int): Host ip on which execute action.
        
    Returns:
        String: Execution state.
    """

    return "ok"
