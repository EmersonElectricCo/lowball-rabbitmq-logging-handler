import logging
import pytest
from lowball_rabbitmq_logging_handler import LowballRabbitMQLoggingHandler

"""
CRITICAL: 'CRITICAL',
ERROR: 'ERROR',
WARNING: 'WARNING',
INFO: 'INFO',
DEBUG: 'DEBUG',
NOTSET: 'NOTSET',
"""
class TestLowballRabbitMQLoggingHandler:

    @pytest.mark.parametrize("level,error", [
        (logging.DEBUG, False),
        (logging.INFO, False),
        (logging.WARNING, False),
        (logging.ERROR, False),
        (logging.NOTSET, False),
        (logging.CRITICAL, False),
        ("hello", True),
        (1000, False),
        (["list"], True)

    ])
    def test_init_level(self, level, error):

        if error:
            with pytest.raises(Exception):
                LowballRabbitMQLoggingHandler(level=level)
        else:
            handler = LowballRabbitMQLoggingHandler(level=level)
            assert handler.level == level

    @pytest.mark.parametrize("host,error", [
        ("hello", False),
        ("hello.hello.com", False),
        ("1.2.4.5", False),
        (12000, True),
        (["list"], True)
    ])
    def test_init_host(self, host, error):

        if error:
            with pytest.raises(Exception):
                LowballRabbitMQLoggingHandler(host=host)
        else:
            handler = LowballRabbitMQLoggingHandler(host=host)
            assert handler.host == host

    @pytest.mark.parametrize("port,error", [
        (-1, True),
        (1.334, True),
        ("1.2.4.5", True),
        (12000, False),
        (["list"], True),
        (65536, True),
        (8000, False)
    ])
    def test_init_port(self, port, error):
        if error:
            with pytest.raises(Exception):
                LowballRabbitMQLoggingHandler(port=port)
        else:
            handler = LowballRabbitMQLoggingHandler(port=port)
            assert handler.port == port

    @pytest.mark.parametrize("value,error,expected", [
        ("hello", False, "hello"),
        ("", False, ""),
        (None, False, ""),
        (["list"], True, None),
        (11234, True, None)
    ])
    def test_init_username_password(self, value, error, expected):
        if error:
            with pytest.raises(ValueError):
                LowballRabbitMQLoggingHandler(username=value)
            with pytest.raises(ValueError):
                LowballRabbitMQLoggingHandler(password=value)
        else:
            handler = LowballRabbitMQLoggingHandler(password=value)
            assert handler.password == expected
            handler = LowballRabbitMQLoggingHandler(username=value)
            assert handler.username == expected

    @pytest.mark.parametrize("value,error,expected", [
        (True, False, True),
        (False, False, False),
        ("True", False, True),
        ("TRUE", False, True),
        ("False", False, False),
        ("true", False, True),
        ("false", False, False),
        ("FALSE", False, False),
        ("somestring", True, None),
        (0, False, False),
        (1, False, True),
        (None, False, False),
        ("", True, None),
        (["list"], True, None)
    ])
    def test_init_use_ssl_verify_ssl(self, value, error, expected):

        if error:
            with pytest.raises(ValueError):
                LowballRabbitMQLoggingHandler(use_ssl=value)
            with pytest.raises(ValueError):
                LowballRabbitMQLoggingHandler(verify_ssl=value)
        else:
            handler = LowballRabbitMQLoggingHandler(use_ssl=value)
            assert handler.use_ssl == expected
            handler = LowballRabbitMQLoggingHandler(verify_ssl=value)
            assert handler.verify_ssl == expected

    def test_init_ca_file(self):

        pass

    def test_init_ca_path(self):

        pass

    def test_init_exchange(self):

        pass

    def test_init_environment(self):

        pass

    def test_init_service_name(self):

        pass

    def test_init_formatter_configuration(self):

        pass

    def test_get_connection_parameters(self):

        pass

    def test_get_connection(self):

        pass

    def test_close_connection(self):

        pass

    def test_emit(self):

        pass