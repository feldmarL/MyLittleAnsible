"""
Python module to execute service module defined in todos file.
"""

from .tools import execute_command, logger

SYSTEMD: str
ACTION: str
PASSWORD: str
IP: str

def set_variables(params, host_pwd, host_ip):
    """ Set variable and return it based on params.

    Args:
        params (list(String)): List of todo params from todos file.
        host_pwd (String): User's password on remote host.
        host_ip (String): Remote host ip.
    """
    global SYSTEMD, ACTION, PASSWORD, IP
    SYSTEMD = params["name"]
    match params["state"]:
        case "started":
            ACTION = "start"
        case "restarted":
            ACTION = "restart"
        case "stopped":
            ACTION = "stop"
        case "enabled":
            ACTION = "enable"
        case "disabled":
            ACTION = "disable"
    PASSWORD = host_pwd
    IP = host_ip

def check_execution(client):
    """Check module execution for idempotence and end execution verification.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.

    Returns:
        (bool, String): Execution state.
    """
    command = f"sudo -S systemctl is-active {SYSTEMD}"
    stdout, _ = execute_command(True, client, command, host_pwd=PASSWORD)
    execution_state = stdout[:-1]

    match ACTION:
        case "start":
            if "active" == execution_state:
                return True, execution_state
        case "restart":
            if "active" == execution_state:
                return True, execution_state
        case "stop":
            if "inactive" == execution_state:
                return True, execution_state

    command = f"sudo -S systemctl is-enabled {SYSTEMD}"
    stdout, _ = execute_command(True, client, command, host_pwd=PASSWORD)
    execution_state = stdout[:-1]

    match ACTION:
        case "enable":
            if "enabled" == execution_state:
                return True, execution_state
        case "disable":
            if "disabled" == execution_state:
                return True, execution_state

    return False, execution_state

def execute(client):
    """Execute action for systemd on host.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
    """
    command = f"sudo -S systemctl {ACTION} {SYSTEMD}"
    _, stderr = execute_command(True, client, command, host_pwd=PASSWORD)

    if "incorrect" in stderr:
        logger.info(f"Incorrect password provided in inventory file for {IP}. "
            f"service module can't be executed without sudo password.")
        logger.error(f"No password were provided in inventory file for {IP}. "
                     f"service module can't be executed without sudo password.")
        return False, "incorrect"

    return check_execution(client)

def service(client, params, host_pwd, host_ip):
    """ Service module entry point.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of parameters about package defined in todos file.
        host_pwd (String): User's password on remote host.
        host_ip (int): Host ip on which execute action.

    Returns:
        String: Execution state.
    """
    set_variables(params, host_pwd, host_ip)
    state, execution_state = (False, "")
    if ACTION != "restart":
        state, execution_state = check_execution(client)

    if "failed" in execution_state:
        logger.debug(f"{SYSTEMD} initial state on {IP} is FAILED.")

    if state:
        return "ok"

    execution, execution_state = execute(client)

    if not execution and execution_state != "incorrect":
        logger.info(f"A problem occured when executing {ACTION} for {SYSTEMD} on {IP}. "
                    f"Current state is {execution_state}")
        logger.error(f"A problem occured when executing {ACTION} for {SYSTEMD} on {IP}. "
                     f"Current state is {execution_state}")
        return "ko"

    return "changed"
