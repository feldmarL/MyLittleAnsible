from dataclasses import dataclass
from os import getlogin

@dataclass
class Todo:
    module: str
    params: dict

@dataclass
class Host:
    name: str
    ip: str
    port: int
    auth: bool = True
    ssh_user: str = getlogin()
    ssh_password: str = ""
    ssh_private_key_path: str = ""