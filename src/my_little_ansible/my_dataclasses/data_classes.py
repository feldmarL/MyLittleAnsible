"""
Dataclasses designed to hold Todos and Hosts.
"""

from dataclasses import dataclass
from os import getlogin


@dataclass
class Todo:
    """ Todo dataclass with todo name and parameters defined in todos file.
    """
    module: str
    params: dict

@dataclass
class Host:
    """ Host dataclass with required host infos defined in inventory file.
    """
    name: str
    ip: str
    port: int
    auth: bool = True
    ssh_user: str = getlogin()
    ssh_password: str = ""
    ssh_private_key_path: str = ""
