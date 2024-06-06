"""
Python module to execute apt module defined in todos file.
"""

from .tools import execute_command, logger

def switch_state(params, original):
    """ Switch state as we need install and remove in code
        but don't want to change todo.

    Args:
        params (list(String)): List of parameters about package defined in todos file.
        original (bool): Action type. Back to original or not?

    Returns:
        params (list(String)): List of parameters about package defined in todos file.
    """
    if not original:
        params["state"] = {"present": "install", "absent": "remove"}[params["state"]]
    else:
        params["state"] = {"install": "present", "remove": "absent"}[params["state"]]
    return params

def check_state(client, params, host_ip):
    """ Check if the action is already done and return state + variables.

    Args:
        params (list(String)): List of parameters about package defined in todos file.
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        host_ip (String): Host ip.

    Returns:
        state (String): Execution state, action to do and package on which action to do.
    """
    command = f'dpkg -s {params["name"]} | grep "Status"'
    stdout, _ = execute_command(False, client, command)

    logger.debug("%s state on %s: %s", params['name'], host_ip, stdout)

    if params["state"] == "install":
        if "ok installed" in stdout:
            logger.info("%s already installed on %s. Todos DONE with status OK.",
                        params['name'], host_ip)
            return "ok"

    elif params["state"] == "remove":
        if not "ok installed" in stdout:
            logger.info("%s already absent from %s. Todos DONE with status OK.",
                        params['name'], host_ip)
            return "ok"

    return "to change"

def apt(client, params, host_ip, host_pwd):
    """ Module's entry point.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of todo's params extracted from todos file.
        host_pwd (String): User's password on remote host.
        host_ip (String): Host ip.
        logger (Logger): The main created logger to log.

    Returns:
        String: Execution state.
    """
    command = f'echo "{host_pwd}" | sudo -S apt-get update'
    _, stderr = execute_command(True, client, command, host_pwd=host_pwd)

    if "incorrect" in stderr:
        logger.warning("Incorrect password provided in inventory file for %s. "
                       "apt module can't be executed without sudo password.", host_ip)
        logger.error("No password were provided in inventory file for %s. "
                     "apt module can't be executed without sudo password.", host_ip)
        return "ko"

    params = switch_state(params, False)

    state = check_state(client, params, host_ip)
    if state == "ok":
        return state

    command = f'echo "{host_pwd}" | sudo -S apt-get -y {params["state"]} {params["name"]}'
    stdout, stderr = execute_command(True, client, command, host_pwd=host_pwd)

    logger.debug("While trying to %s %s, STDOUT:\n%s", params['state'], params['name'], stdout)

    if stderr != "" and "dpkg-preconfigure: unable to re-open stdin:" not in stderr:
        logger.error("While trying to %s %s, first 200 STDERR chars:\n%s",
                     params['state'], params['name'], stderr[:200])
        params = switch_state(params, True)
        return "ko"

    params = switch_state(params, True)
    return "changed"
