# internal
from galah.core.backends.redis import *

# test internal
from .pytest_redis import parse_redis_config

# stdlib
import re

# external
import pytest
import redis

# Tell pytest to load our pytest_redis plugin. Absolute import is required here
# though I'm not sure why. It does not error when given simply "pytest_redis"
# but it does not correclty load the plugin.
pytest_plugins = ("galah.tests.core.pytest_redis", )

@pytest.fixture
def redis_server(request, capfd):
    raw_config = request.config.getoption("--redis")
    if not raw_config:
        pytest.skip("Configuration with `--redis` required for this test.")
    config = parse_redis_config(raw_config)

    db = config.db_range[0]
    connection = redis.StrictRedis(host = config.host, port = config.port,
        db = db)

    # This will delete everything in the current database
    connection.flushdb()

    return connection

class TestRedis:
    def test_foo(self, redis_server):
        redis_server.ping()

        assert False
