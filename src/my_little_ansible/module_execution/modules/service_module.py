"""
Python module to execute service module defined in todos file.
"""

from .tools import execute_command, logger

def define_action(state):
    """Define litteral action to execute based on wanted state.

    Args:
        state (String): Wanted state.

    Returns:
        action (String): String of litteral action to execute. False if unknown.
    """
    return {"started": "start",
            "restarted": "restart",
            "stopped": "stop",
            "enabled": "enable",
            "disabled": "disable"}.get(state, False)

def check_execution(client, params, host_pwd):
    """Check module execution for idempotence and end execution verification.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of parameters about package defined in todos file.
        host_pwd (String): User's password on remote host.

    Returns:
        (bool, String): Execution state.
    """
    command = f"sudo -S systemctl is-active {params['name']}"
    stdout, _ = execute_command(True, client, command, host_pwd)
    execution_state = stdout[:-1]

    match params["state"]:
        case "started":
            if "active" == execution_state:
                return True, execution_state
        case "restarted":
            if "active" == execution_state:
                return True, execution_state
        case "stopped":
            if "inactive" == execution_state:
                return True, execution_state

    command = f"sudo -S systemctl is-enabled {params['name']}"
    stdout, _ = execute_command(True, client, command, host_pwd)
    execution_state = stdout[:-1]

    match params["state"]:
        case "enabled":
            if "enabled" == execution_state:
                return True, execution_state
        case "disabled":
            if "disabled" == execution_state:
                return True, execution_state

    return False, execution_state

def execute(client, params, host_pwd, host_ip):
    """Execute action for systemd on host.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of parameters about package defined in todos file.
        host_pwd (String): User's password on remote host.
        host_ip (String): Host ip on which execute action.
    """
    if not (action := define_action(params['state'])):
        logger.info("Unkown service state or action asked. Were provided with %s. "
                    "Known and defined state and action are: "
                    "started, restarted, stopped, enabled and disabled", params['state'])
        logger.error("Unkown service state or action asked. Were provided with %s. "
                     "Known and defined state and action are: "
                     "started, restarted, stopped, enabled and disabled", params['state'])
        return False, "unknown action"
    command = f"sudo -S systemctl {action} {params['name']}"
    _, stderr = execute_command(True, client, command, host_pwd)

    if "incorrect" in stderr:
        logger.info("Incorrect password provided in inventory file for %s. "
                    "service module can't be executed without sudo password.", host_ip)
        logger.error("No password were provided in inventory file for %s. "
                     "service module can't be executed without sudo password.", host_ip)
        return False, "incorrect"

    return check_execution(client, params, host_pwd)

def service(client, params, host_ip, host_pwd):
    """ Service module entry point.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of parameters about package defined in todos file.
        host_pwd (String): User's password on remote host.
        host_ip (String): Host ip on which execute action.

    Returns:
        String: Execution state.
    """
    state, execution_state = (False, "")
    if params["state"] != "restart":
        state, execution_state = check_execution(client, params, host_pwd)

    if "failed" in execution_state:
        logger.debug("%s initial state on %s is FAILED.", params['name'], host_ip)

    if state:
        return "ok"

    execution, execution_state = execute(client, params, host_pwd, host_ip)

    if not execution and execution_state not in ["incorrect", "unknown"]:
        logger.info("A problem occured when executing {params['state']} for {params['name']} "
                    "on %s. Current state is %s", host_ip, execution_state)
        logger.error("A problem occured when executing {params['state']} for {params['name']} "
                    "on %s. Current state is %s", host_ip, execution_state)
        return "ko"

    return "changed"
