"""
Entry point of MyLittleAnsible project.
"""

from logging import (DEBUG, INFO)

from click import command, option

from .module_execution.execute_todos import execution
from .my_dataclasses.populate_dataclasses import populate_host, populate_todo

from .module_execution.tools import logger

@command()
@option("-f", "--todos_file_path", show_default=True, default="todos.yml", help="Todos file.")
@option("-i", "--inventory", show_default=True, default="inventory.yml", help="Inventory file.")
@option("--debug", is_flag=True, show_default=True, default=False, help="Debug mode.")
@option("--dry-run", is_flag=True, show_default=True, default=False, help="Dry-run mode.")
def cmd_interpreter(todos_file_path, inventory, debug, dry_run):
    """ Entry point to main program.

    Args:
        todos_file_path (string): Path to todos file, default: todos.yml.
        inventory (string): Path to inventory file, default: inventory.yml.
        debug (bool): Option to launch project in debug mode.
        dry_run (bool): Option to launch project in dry_run mode.
    """
    logger.setLevel(INFO)

    if debug:
        logger.debug("Activated print of stack traces.")
        logger.setLevel(DEBUG)
    if dry_run:
        pass

    todos = populate_todo(todos_file_path, logger)
    logger.info("Todos file parsed.")
    logger.info(f"Total of todos to be executed: {len(todos)}")

    hosts = populate_host(inventory, logger)
    logger.info("Inventory file parsed.")

    for host in hosts:
        execution(host, todos)
