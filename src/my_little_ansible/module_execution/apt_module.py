
def close_std(stdin, stdout, stderr):
    stdin.close()
    stdout.close()
    stderr.close()

def apt(client, params, host_pwd, host_ip, logger):
    stdin, stdout, stderr = client.exec_command(f'echo "{host_pwd}" | sudo -S apt-get update')
    close_std(stdin, stdout, stderr)

    package = params["name"]
    if params["state"] == "present":
        action = "install"
    elif params["state"] == "absent":
        action = "remove"

    stdin, stdout, stderr = client.exec_command(f'dpkg -s {package} | grep "Status"')

    if action == "install":
        if "ok installed" in stdout.read().decode():
            logger.info(f"Package {package} is already installed on {host_ip}. Todos DONE with status OK.")
            close_std(stdin, stdout, stderr)
            return "ok"

    elif action == "remove":
        if "deinstall" in stdout.read().decode() or "not installed" in stderr.read().decode():
            logger.info(f"Package {package} is already uninstalled on {host_ip}. Todos DONE with status OK.")
            close_std(stdin, stdout, stderr)
            return "ok"


    stdin, stdout, stderr = client.exec_command(f'echo "{host_pwd}" | sudo -S apt-get -y {action} {package}')

    logger.debug(f"While trying to {action} {package}, STDOUT:\n{stdout.read().decode()}")
    logger.error(f"While trying to {action} {package}, STDERR:\n{stderr.read().decode()}")
    close_std(stdin, stdout, stderr)
    return "changed"