"""
Python module to execute apt module defined in todos file.
"""

from .tools import close_std

def set_variables_and_check_ok(params, client, host_ip, logger):
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
    package = params["name"]
    if params["state"] == "present":
        action = "install"
    elif params["state"] == "absent":
        action = "remove"

    stdin, stdout, stderr = client.exec_command(f'dpkg -s {package} | grep "Status"')
    if action == "install":
        if "ok installed" in stdout.read().decode():
            logger.info(f"{package} already installed on {host_ip}. Todos DONE with status OK.")
            close_std(stdin, stdout, stderr)
            return "ok", action, package

    elif action == "remove":
        if not "ok installed" in stdout.read().decode():
            logger.info(f"{package} already uninstalled on {host_ip}. Todos DONE with status OK.")
            close_std(stdin, stdout, stderr)
            return "ok", action, package

    close_std(stdin, stdout, stderr)
    return "to change", action, package

def apt(client, params, host_pwd, host_ip, logger):
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
    stdin, stdout, stderr = client.exec_command(f'echo "{host_pwd}" | sudo -S apt-get update')
    if "incorrect" in stderr.read().decode():
        logger.info(f"Incorrect password provided in inventory file for {host_ip}. "
                    f"apt module can't be executed without sudo password.")
        logger.error(f"No password were provided in inventory file for {host_ip}. "
                     f"apt module can't be executed without sudo password.")
        return "ko"
    close_std(stdin, stdout, stderr)

    state, action, package = set_variables_and_check_ok(params, client, host_ip, logger)

    if state == "ok":
        return state

    stdin, stdout, stderr = client.exec_command(f'echo "{host_pwd}" | \
                                                sudo -S apt-get -y {action} {package}')

    logger.debug(f"While trying to {action} {package}, STDOUT:\n{stdout.read().decode()}")
    logger.error(f"While trying to {action} {package}, STDERR:\n{stderr.read().decode()}")
    close_std(stdin, stdout, stderr)
    return "changed"
