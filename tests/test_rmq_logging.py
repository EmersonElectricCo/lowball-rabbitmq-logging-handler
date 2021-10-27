import logging
import ssl
import pika
import pytest
from lowball_rabbitmq_logging_handler import LowballRabbitMQLoggingHandler
import lowball_rabbitmq_logging_handler
from unittest.mock import Mock, call, patch
from io import StringIO
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

    @pytest.mark.parametrize("ca_file_path,error", [
        ("ca_certificates", False),
        (1234, True),
        ("/LOL", True),
        ("something", False),
        ("", False),
        (None, False)
    ])
    def test_init_ca_path(self, tmp_path, ca_file_path, error):

        if error:
            with pytest.raises(ValueError):
                LowballRabbitMQLoggingHandler(ca_path=ca_file_path)
        else:
            if ca_file_path:
                path = tmp_path / ca_file_path
                path.mkdir()
                strpath = str(path)
                handler = LowballRabbitMQLoggingHandler(ca_path=strpath)
                assert handler.ca_path == strpath
            else:
                handler = LowballRabbitMQLoggingHandler(ca_path=ca_file_path)
                assert handler.ca_path == None

    @pytest.mark.parametrize("cafile", [
        "/tmp/this/does/not/exist.pem",
        12344

    ])
    def test_init_ca_file_file_does_not_exist_or_invalid(self, cafile):
        with pytest.raises(ValueError):
            LowballRabbitMQLoggingHandler(ca_file="/tmp/this/does/not/exist.pem")


    @pytest.mark.parametrize("cafile", [
        "file.ca",
        "",
        None
    ])
    def test_init_ca_file_file_does_exist_or_empty(self, tmp_path, cafile):

        if cafile:
            path = tmp_path / "cas"
            path.mkdir()
            f = path / cafile
            f.write_text("hello")

            handler = LowballRabbitMQLoggingHandler(ca_file=str(f.absolute()))
            assert handler.ca_file == str(f.absolute())
        else:
            handler = LowballRabbitMQLoggingHandler(ca_file=cafile)
            assert handler.ca_file == None

    @pytest.mark.parametrize("value,error,expected", [
        ("", False, "logs"),
        (None, False, "logs"),
        ("hello", False, "hello"),
        (101232, True, None),
        (["list"], True, None)
    ])
    def test_init_exchange(self, value, error, expected):

        if error:
            with pytest.raises(Exception):
                LowballRabbitMQLoggingHandler(exchange=value)
        else:
            handler = LowballRabbitMQLoggingHandler(exchange=value)
            assert handler.exchange == expected

    @pytest.mark.parametrize("value,error,expected", [
        ("", False, "default"),
        (None, False, "default"),
        ("hello", False, "hello"),
        (101232, True, None),
        (["list"], True, None)
    ])
    def test_init_environment(self, value, error, expected):

        if error:
            with pytest.raises(Exception):
                LowballRabbitMQLoggingHandler(environment=value)
        else:
            handler = LowballRabbitMQLoggingHandler(environment=value)
            assert handler.environment == expected

    @pytest.mark.parametrize("value,error,expected", [
        ("", False, "lowball"),
        (None, False, "lowball"),
        ("hello", False, "hello"),
        (101232, True, None),
        (["list"], True, None)
    ])
    def test_init_service_name(self, value, error, expected):

        if error:
            with pytest.raises(Exception):
                LowballRabbitMQLoggingHandler(service_name=value)
        else:
            handler = LowballRabbitMQLoggingHandler(service_name=value)
            assert handler.service_name == expected

    @pytest.mark.parametrize("config,expected_call", [
        ({"hello": "goodbyte", "k": 1}, call(hello="goodbyte", k=1)),
        (None, call())

    ])
    def test_init_formatter(self, monkeypatch, config, expected_call):

        monkeypatch.setattr(LowballRabbitMQLoggingHandler.FORMATTER_CLASS, "__init__", Mock(return_value=None))

        handler = LowballRabbitMQLoggingHandler(formatter_configuration=config)
        LowballRabbitMQLoggingHandler.FORMATTER_CLASS.__init__.assert_has_calls([expected_call])

    @pytest.mark.parametrize("env,name,loglevel, expected_key", [
        (None, None, "info", "default.lowball.info"),
        ("", "", "critical", "default.lowball.critical"),
        ("something", "bow", "debug", "something.bow.debug"),
    ])
    def test_get_routing_key(self, env, name, loglevel, expected_key):

        handler = LowballRabbitMQLoggingHandler(environment=env, service_name=name)
        assert handler.get_routing_key(loglevel) == expected_key


    @pytest.mark.parametrize("username,password,usessl,cafile,capath,verify_ssl", [
        ("", "", False, "", "", False),
        ("user", "", False, "", "", False),
        ("user", "password", True, "", "", True),
        ("user", "password", True, "", "", False)
    ])
    def test_get_connection_parameters(self,
                                       username,
                                       password,
                                       usessl,
                                       cafile,
                                       capath,
                                       verify_ssl
                                       ):

        handler = LowballRabbitMQLoggingHandler(username=username, password=password,
                                                use_ssl=usessl, ca_path=capath, ca_file=cafile, verify_ssl=verify_ssl)


        connection_dict = {
            "host": handler.host,
            "port": handler.port
        }

        if username:
            connection_dict["credentials"] = pika.PlainCredentials(handler.username, handler.password)

        if usessl:
            expected_context = ssl.create_default_context(cafile=cafile, capath=capath)
            if not verify_ssl:
                expected_context.check_hostname = False
                expected_context.verify_mode = ssl.CERT_NONE

            connection_dict["ssl_options"] = pika.SSLOptions(expected_context)

        expected_connection_parameters = pika.ConnectionParameters(**connection_dict)
        connection_parameters = handler.get_connection_parameters()

        assert connection_parameters.host == expected_connection_parameters.host
        assert connection_parameters.port == expected_connection_parameters.port
        assert connection_parameters.credentials == expected_connection_parameters.credentials
        if not usessl:
            assert connection_parameters.ssl_options is None
        else:
            assert connection_parameters.ssl_options.context.verify_mode == expected_connection_parameters.ssl_options.context.verify_mode
            assert connection_parameters.ssl_options.context.check_hostname == expected_connection_parameters.ssl_options.context.check_hostname

    def test_emit_no_channel_or_connection(self, mock_pika_open_blocking_connection, mock_pika_open_channel, test_log_record):

        handler = LowballRabbitMQLoggingHandler()
        with patch('sys.stderr', new=StringIO()) as test_stderr:

            handler.emit(test_log_record)

            assert handler._connection is not None
            assert handler._channel is not None
            handler._channel.basic_publish.assert_called_once()

            msg = test_stderr.getvalue()
            assert not msg

    def test_emit_error_first_publish(self, test_log_record, mock_pika_open_channel_error_first_pub, mock_pika_open_blocking_connection):

        handler = LowballRabbitMQLoggingHandler()
        with patch('sys.stderr', new=StringIO()) as test_stderr:

            handler.emit(test_log_record)

            assert handler._connection is not None
            assert handler._channel is not None

            assert handler._channel.basic_publish.call_count == 2
            msg = test_stderr.getvalue()
            assert not msg

    def test_emit_error_second_publish(self, test_log_record, mock_pika_open_channel_error_all_pub, mock_pika_open_blocking_connection):

        handler = LowballRabbitMQLoggingHandler()
        with patch('sys.stderr', new=StringIO()) as test_stderr:

            handler.emit(test_log_record)

            assert handler._connection is not None
            assert handler._channel is not None
            assert handler._channel.basic_publish.call_count == 2
            msg = test_stderr.getvalue()
            assert msg.startswith("Unable to submit log")


