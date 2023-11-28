"""
Python module to execute apt module defined in todos file.
"""

from .tools import execute_command, logger

PACKAGE: str
ACTION: str

def set_variables_and_check_ok(params, client, host_ip):
    """ Set variables from received parameters and check if
        the action is already done and return state + variables.

    Args:
        params (list(String)): List of parameters about package defined in todos file.
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        host_ip (int): Host ip.
        logger (Logger): The main created logger to log.

    Returns:
        state, action, package (String, String, String):
            Execution state, action to do and package on which action to do.
    """
    global PACKAGE, ACTION
    PACKAGE = params["name"]
    if params["state"] == "present":
        ACTION = "install"
    elif params["state"] == "absent":
        ACTION = "remove"

    command = f'dpkg -s {PACKAGE} | grep "Status"'
    stdout, _ = execute_command(False, client, command)

    logger.debug(f"{PACKAGE} state on {host_ip}: {stdout}")

    if ACTION == "install":
        if "ok installed" in stdout:
            logger.info(f"{PACKAGE} already installed on {host_ip}. Todos DONE with status OK.")
            return "ok"

    elif ACTION == "remove":
        if not "ok installed" in stdout:
            logger.info(f"{PACKAGE} already uninstalled on {host_ip}. Todos DONE with status OK.")
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
    state = set_variables_and_check_ok(params, client, host_ip)

    if state == "ok":
        return state

    command = (f'echo "{host_pwd}" | sudo -S apt-get -y {ACTION} {PACKAGE}')
    stdout, stderr = execute_command(True, client, command, host_pwd=host_pwd)

    logger.debug(f"While trying to {ACTION} {PACKAGE}, STDOUT:\n{stdout}")

    if stderr != "" and "dpkg-preconfigure: unable to re-open stdin:" not in stderr:
        logger.error(f"While trying to {ACTION} {PACKAGE}, first 200 STDERR chars:\n{stderr[:200]}")
        return "ko"

    return "changed"
