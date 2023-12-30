"""
Python module to render Jinja2 template on host.
"""

from os import path
from io import BytesIO

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .tools import logger, mkpath, backup

def render_template(template_path, variables):
    """Apply variables to file template using Jinja2.

    Args:
        template_path (String): String of path to file template.
        variables (dict): Variables dictionnary to apply to file template.

    Returns:
        String: File template with vars applied as a String.
    """
    environment = Environment(
        loader = FileSystemLoader("."),
        autoescape = select_autoescape()
    )

    if path.isfile(template_path):
        return environment.get_template(template_path).render(variables)

    logger.info("Template not found in source directory with specified name.")
    logger.error("Template not found in source directory with specified name.")

def template(client, params, host_ip, _):
    """Render template on remote host.

    Args:
        client (SSHClient): Paramiko's SSH Client used to connect to host.
        params (list(String)): List of parameters about package defined in todos file.
        host_ip (String): Host ip on which execute action.
        
    Returns:
        String: Execution state.
    """

    rendered_template = render_template(params["src"], params["vars"])

    sftp = client.open_sftp()

    if "backup" not in params.keys():
        logger.info("Template module initialized with default backup value set to False.")
    elif params["backup"]:
        backup(sftp, params["dest"], host_ip)

    try:
        mkpath(sftp, '/'.join(params["dest"].split('/')[:-1]))
        sftp.putfo(BytesIO(rendered_template.encode()), params["dest"], confirm = False)

    except IOError:
        logger.info("Error occured while creating remote directory or puting file to remote host. "
                    "User way not have the rights to specific remote file.")
        logger.error("Error occured while creating remote directory or puting file to remote host. "
                    "User way not have the rights to specific remote file.")
        sftp.close()
        return "ko"

    sftp.close()
    return "changed"
