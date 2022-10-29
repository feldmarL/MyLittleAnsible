"""
Python module to open todos and inventory file and populate a list of
Host and Todo which are dataclasses defined in data_classes.py.
"""

from os import path

from yaml import FullLoader, YAMLError, load

from .data_classes import Host, Todo

def populate_todo(todos_file_path, logger):
    """Populate todo from todos file.

    Args:
        todos_file_path (str): Todos file path.

    Returns:
        list: List of action to do.
    """
    todos: list[Todo] = []
    try:
        if path.isfile(todos_file_path):
            with open(todos_file_path, "r", encoding="utf-8") as todos_file:
                todos_file = load(todos_file, Loader=FullLoader)
                for todo in todos_file:
                    todos.append(Todo(todo["module"], todo["params"]))
        else:
            logger.error("Can't acces todos file path.")
    except YAMLError:
        logger.error("Error occured while parsing yaml todos file.")
    return todos

def populate_host(inventory_file, logger):
    """Populate hodt from inventory file.

    Args:
        inventory_file (str): Inventory file path.

    Returns:
        list: List of hosts on which actions to do.
    """
    hosts: list[Host] = []
    try:
        if path.isfile(inventory_file):
            with open(inventory_file, "r", encoding="utf-8") as file:
                inventory = load(file, Loader=FullLoader)
                for host, params in inventory["hosts"].items():
                    current_host = Host(host, params["ssh_address"], params["ssh_port"])
                    logger.info(f"Target host: {host}")

                    if "ssh_user" in params:
                        setattr(current_host, "ssh_user", params["ssh_user"])

                    if "ssh_password" in params:
                        setattr(current_host, "ssh_password", params["ssh_password"])
                    elif "ssh_key_file" in params:
                        setattr(current_host, "ssh_private_key_path", params["ssh_key_file"])
                        setattr(current_host, "auth", False)

                    hosts.append(current_host)
        else:
            logger.error("Inventory file does not exist, please provide an existing inventory file path.")
            raise FileNotFoundError(inventory_file)
    except YAMLError:
        logger.error("Error occured while parsing yaml inventory file.")
    return hosts
