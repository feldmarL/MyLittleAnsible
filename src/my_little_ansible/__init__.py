"""
Entry point of MyLittleAnsible project.
"""

from logging import (DEBUG, ERROR, INFO, FileHandler, Formatter, StreamHandler,
                     getLogger)
from sys import stdout

from click import command, option

from .module_execution.execute_todos import execution
from .my_dataclasses.populate_dataclasses import populate_host, populate_todo

formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

stderr_handler = FileHandler("stderr.log")
stderr_handler.setLevel(ERROR)
stderr_handler.setFormatter(formatter)

stdout_handler = StreamHandler(stdout)
stdout_handler.setLevel(DEBUG)
stdout_handler.setFormatter(formatter)

logger = getLogger(__name__)
logger.setLevel(DEBUG)
logger.addHandler(stderr_handler)
logger.addHandler(stdout_handler)

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
        execution(host, todos, logger)
