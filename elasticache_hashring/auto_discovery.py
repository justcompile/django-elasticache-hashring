"""
utils for discovery cluster
"""
import re
from distutils.version import StrictVersion
from telnetlib import Telnet
from django.utils.encoding import smart_text


class WrongProtocolData(ValueError):
    """
    Exception for raising when we get something unexpected
    in telnet protocol
    """
    def __init__(self, cmd, response):
        super(WrongProtocolData, self).__init__(
            'Unexpected response {} for command {}'.format(response, cmd))


def get_cluster_info(host, port):
    """
    return list with info about nodes in cluster
    [
        'IP:port',
        'IP:port',
    ]
    """
    client = Telnet(host, int(port))
    client.write(b'version\n')
    res = client.read_until(b'\r\n').strip()
    version_list = res.split(b' ')
    if len(version_list) != 2 or version_list[0] != b'VERSION':
        raise WrongProtocolData('version', res)
    version = version_list[1]
    if StrictVersion(smart_text(version)) >= StrictVersion('1.4.14'):
        cmd = b'config get cluster\n'
    else:
        cmd = b'get AmazonElastiCache:cluster\n'
    client.write(cmd)
    res = client.read_until(b'\n\r\nEND\r\n')
    client.close()
    ls = [x for x in re.compile(br'\r?\n').split(res)]
    if len(ls) != 4:
        raise WrongProtocolData(cmd, res)

    try:
        version = int(ls[1])
    except ValueError:
        raise WrongProtocolData(cmd, res)
    nodes = []
    try:
        for node in ls[2].split(b' '):
            host, ip, port = node.split(b'|')
            nodes.append('{}:{}'.format(smart_text(ip or host),
                                        smart_text(port)))
    except ValueError:
        raise WrongProtocolData(cmd, res)
    return nodes
