"""
Python module to execute service module defined in todos file.
"""

from .tools import close_std

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
        host_ip (int): Host ip.
        logger (Logger): The main created logger to log.

    Returns:
        (bool, String): Execution state.
    """
    stdin, stdout, stderr = client.exec_command(f'echo "{host_pwd}" | \
                                            sudo -S systemctl is-active {systemd}')
    execution_state = stdout.read().decode()[:-1]
    close_std(stdin, stdout, stderr)

    match action:
        case "start":
            if "active" == execution_state:
                return True, execution_state
        case "stop":
            if "inactive" == execution_state:
                return True, execution_state

    stdin, stdout, stderr = client.exec_command(f'echo "{host_pwd}" | \
                                            sudo -S systemctl is-enabled {systemd}')
    execution_state = stdout.read().decode()[:-1]
    close_std(stdin, stdout, stderr)

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
        systemd (_type_): _description_
        action (_type_): _description_
        client (_type_): _description_
        host_pwd (_type_): _description_
    """
    stdin, stdout, stderr = client.exec_command(f'echo "{host_pwd}" | \
                                            sudo -S systemctl {action} {systemd}')

    if "incorrect" in stderr.read().decode():
        return False, "incorrect"

    close_std(stdin, stdout, stderr)

    if action == "restart":
        action = "start"
    return check_execution(systemd, action, client, host_pwd)

def service(client, params, host_pwd, host_ip, logger):
    """ Service module entry point.

    Args:
        client (SSHClient): _description_
        params (list(String)): _description_
        host_pwd (String): _description_
        host_ip (int): _description_
        logger (Logger): _description_

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
