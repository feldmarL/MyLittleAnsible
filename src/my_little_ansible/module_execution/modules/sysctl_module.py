"""
Python module to execute sysctl module defined in todos file.
"""

from .tools import execute_command, logger

ATTRIBUTE: str
VALUE: str
PERMANENT: str
PASSWORD: str

def set_variables(params, host_pwd):
    """ Set variable and return it based on params.

    Args:
        params (list(String)): List of todo params from todos file.
        host_pwd (String): User's password on remote host.
    """
    global ATTRIBUTE, VALUE, PERMANENT, PASSWORD
    ATTRIBUTE = params["attribute"]
    VALUE = str(params["value"])
    PERMANENT = params["permanent"]
    PASSWORD = host_pwd

def check_execution_np(client):
    """Check NON PERMANENT module execution for idempotence and end execution verification.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.

    Returns:
        (bool, String): Execution state.
    """
    command = f"sudo -S sysctl -n {ATTRIBUTE}"
    stdout, _ = execute_command(True, client, command, host_pwd=PASSWORD)
    effective_value = stdout[:-1]

    if effective_value == VALUE:
        return True, effective_value
    return False, effective_value

def check_execution_p(client):
    """Check PERMANENT module execution for idempotence and end execution verification.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.

    Returns:
        (bool, String): Execution state.
    """
    command = f'cat /etc/sysctl.conf | grep {ATTRIBUTE} | cut -d "=" -f2'
    stdout, _ = execute_command(False, client, command)
    file_value = stdout[:-1]

    state, effective_value = check_execution_np(client)

    if effective_value == VALUE and state:
        return True, effective_value, file_value
    return False, effective_value, file_value

def execute_change(client):
    """Apply changes to kernel host.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.

    Returns:
        (boold, String): Execution state.
    """
    if not PERMANENT:
        command = f'sudo -S sysctl -w {ATTRIBUTE}={VALUE}'
        _, _ = execute_command(True, client, command, host_pwd=PASSWORD)
        return check_execution_np(client)

    state, _, _ = check_execution_p(client)

    if not state:
        command = f'sudo -S echo {ATTRIBUTE}={VALUE} >> /etc/sysctl.conf'
        _, _ = execute_command(True, client, command, host_pwd=PASSWORD)

    command = "sudo -S sysctl -p"
    _, _ = execute_command(True, client, command, host_pwd=PASSWORD)
    state, effective_value = check_execution_np(client)
    return state, effective_value

def sysctl(client, params, host_ip, host_pwd):
    """ Sysctl module entry point.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of parameters about package defined in todos file.
        host_pwd (String): User's password on remote host.
        host_ip (String): Host ip on which execute action.

    Returns:
        String: Execution state.
    """
    set_variables(params, host_pwd)

    if not PERMANENT:
        state, effective_value = check_execution_np(client)
        if not state:
            logger.debug(f"Not yet {ATTRIBUTE}={VALUE} on {host_ip}, current: {effective_value}")
    else:
        state, effective_value, file_value = check_execution_p(client)
        if not state:
            logger.debug(f"{ATTRIBUTE}={VALUE} not applied permanently yet on {host_ip}. "
                         f"Currently effective: {effective_value}. "
                         f"Currently defined in /etc/sysctl.conf file: {file_value}")
    if state:
        return "ok"

    state, effective_value = execute_change(client)

    if state:
        return "changed"

    logger.debug(f"{ATTRIBUTE}={VALUE} FAILED on {host_ip}, current: {effective_value}")

    return "ko"
