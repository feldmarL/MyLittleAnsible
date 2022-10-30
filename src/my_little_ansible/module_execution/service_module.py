"""
Python module to execute service module defined in todos file.
"""

from .tools import execute_command

def set_variables(params):
    """ Set variable and return it based on params.

    Args:
        params (list(String)): List of todo params from todos file.

    Returns:
        systemd, action (String, String): Tuple of strings to describe system and action to do.
    """
    systemd = params["name"]
    match params["state"]:
        case "started":
            action = "start"
        case "restarted":
            action = "restart"
        case "stopped":
            action = "stop"
        case "enabled":
            action = "enable"
        case "disabled":
            action = "disable"
    return systemd, action

def check_execution(systemd, action, client, host_pwd):
    """Check module execution for idempotence and end execution verification.

    Args:
        systemd (String): Service to check.
        action (String): Action requested by user defined in todo params from todos file.
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        host_pwd (String): User's password on remote host.

    Returns:
        (bool, String): Execution state.
    """
    command = f"sudo -S systemctl is-active {systemd}"
    _, stdout, _ = execute_command(True, client, host_pwd, command)
    execution_state = stdout[:-1]

    match action:
        case "start":
            if "active" == execution_state:
                return True, execution_state
        case "stop":
            if "inactive" == execution_state:
                return True, execution_state

    command = f"sudo -S systemctl is-enabled {systemd}"
    _, stdout, _ = execute_command(True, client, host_pwd, command)
    execution_state = stdout[:-1]

    match action:
        case "enable":
            if "enabled" == execution_state:
                return True, execution_state
        case "disable":
            if "disabled" == execution_state:
                return True, execution_state

    return False, execution_state

def execute(systemd, action, client, host_pwd):
    """Execute action for systemd on host.

    Args:
        systemd (String): Service's name.
        action (String): Action to execute.
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        host_pwd (String): User's password on remote host.
    """
    command = f"sudo -S systemctl {action} {systemd}"
    _, _, stderr = execute_command(True, client, host_pwd, command)

    if "incorrect" in stderr:
        return False, "incorrect"

    if action == "restart":
        action = "start"
    return check_execution(systemd, action, client, host_pwd)

def service(client, params, host_pwd, host_ip, logger):
    """ Service module entry point.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of parameters about package defined in todos file.
        host_pwd (String): User's password on remote host.
        host_ip (int): Host ip on which execute action.
        logger (Logger): The main created logger to log.

    Returns:
        String: Execution state.
    """
    systemd, action = set_variables(params)
    state, execution_state = check_execution(systemd, action, client, host_pwd)

    if "failed" in execution_state:
        logger.debug(f"{systemd} initial state on {host_ip} is FAILED.")

    if state:
        return "ok"

    execution, execution_state = execute(systemd, action, client, host_pwd)
    if not execution and "incorrect" == execution_state:
        logger.info(f"Incorrect password provided in inventory file for {host_ip}. "
                    f"service module can't be executed without sudo password.")
        logger.error(f"No password were provided in inventory file for {host_ip}. "
                     f"service module can't be executed without sudo password.")
        return "ko"

    if not execution:
        logger.info(f"A problem occured when executing {action} for {systemd} on {host_ip}. "
                    f"Current state is {execution_state}")
        logger.error(f"A problem occured when executing {action} for {systemd} on {host_ip}. "
                     f"Current state is {execution_state}")
        return "ko"

    return "changed"
