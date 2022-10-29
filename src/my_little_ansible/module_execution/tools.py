"""
Tools used in multiple modules.
"""
def close_std(stdin, stdout, stderr):
    """ Close all specified std.

    Args:
        stdin (ChannelFile): stdin returned from paramiko's exe_command
        stdout (ChannelFile): stdout returned from paramiko's exe_command
        stderr (ChannelFile): stderr returned from paramiko's exe_command
    """
    stdin.close()
    stdout.close()
    stderr.close()