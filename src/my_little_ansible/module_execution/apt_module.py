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
        if params["state"] == "present":
            params["state"] = "install"
        elif params["state"] == "absent":
            params["state"] = "remove"

    if original:
        if params["state"] == "install":
            params["state"] = "present"
        elif params["state"] == "remove":
            params["state"] = "absent"

    return params

def check_state(client, params, host_ip):
    """ Check if the action is already done and return state + variables.

    Args:
        params (list(String)): List of parameters about package defined in todos file.
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        host_ip (int): Host ip.

    Returns:
        state (String): Execution state, action to do and package on which action to do.
    """
    command = f'dpkg -s {params["name"]} | grep "Status"'
    stdout, _ = execute_command(False, client, command)

    logger.debug(f"{params['name']} state on {host_ip}: {stdout}")

    if params["state"] == "install":
        if "ok installed" in stdout:
            logger.info(f"{params['name']} already installed on {host_ip}. Todos DONE with status OK.")
            return "ok"

    elif params["state"] == "remove":
        if not "ok installed" in stdout:
            logger.info(f"{params['name']} already uninstalled on {host_ip}. Todos DONE with status OK.")
            return "ok"

    return "to change"

def apt(client, params, host_pwd, host_ip):
    """ Module's entry point.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of todo's params extracted from todos file.
        host_pwd (String): User's password on remote host.
        host_ip (int): Host ip.
        logger (Logger): The main created logger to log.

    Returns:
        String: Execution state.
    """
    command = f'echo "{host_pwd}" | sudo -S apt-get update'
    _, stderr = execute_command(True, client, command, host_pwd=host_pwd)

    if "incorrect" in stderr:
        logger.warning(f"Incorrect password provided in inventory file for {host_ip}. "
                    f"apt module can't be executed without sudo password.")
        logger.error(f"No password were provided in inventory file for {host_ip}. "
                     f"apt module can't be executed without sudo password.")
        return "ko"

    params = switch_state(params, False)
    
    state = check_state(client, params, host_ip)
    if state == "ok":
        return state

    command = (f'echo "{host_pwd}" | sudo -S apt-get -y {params["state"]} {params["name"]}')
    stdout, stderr = execute_command(True, client, command, host_pwd=host_pwd)

    logger.debug(f"While trying to {params['state']} {params['name']}, STDOUT:\n{stdout}")

    if stderr != "" and "dpkg-preconfigure: unable to re-open stdin:" not in stderr:
        logger.error(f"While trying to {params['state']} {params['name']}, first 200 STDERR chars:\n{stderr[:200]}")
        params = switch_state(params, True)
        return "ko"

    params = switch_state(params, True)
    return "changed"
