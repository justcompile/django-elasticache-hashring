from django.core.cache.backends.memcached import MemcachedCache
from django.utils import six

from elasticache_hashring import (
    auto_discovery,
    client as memcache
)


class MemcachedHashRingCache(MemcachedCache):
    "An implementation of a cache binding using python-memcached and hash_ring"
    def __init__(self, server, params):
        if isinstance(server, six.string_types):
            initial_servers = server.split(';')
        else:
            initial_servers = server

        host, port = initial_servers[0].split(':')

        servers = auto_discovery.get_cluster_info(host, port)

        super(MemcachedHashRingCache, self).__init__(servers, params,
                                                     library=memcache,
                                                     value_not_found_exception=ValueError)
