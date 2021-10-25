import logging
import sys
import time
from logging import LogRecord
import pika
import ssl
import os
from pika import credentials
from lowball.builtins.logging.formatter import DefaultFormatter


class LowballRabbitMQLoggingHandler(logging.Handler):

    FORMATTER_CLASS = DefaultFormatter

    DEFAULT_ENVIRONMENT = "default"
    DEFAULT_SERVICE_NAME = "lowball"
    DEFAULT_EXCHANGE = "logs"
    def __init__(self,
                 level=logging.DEBUG,  # 10
                 host="127.0.0.1",
                 port=5672,
                 username="",
                 password="",
                 use_ssl=False,
                 verify_ssl=True,
                 ca_file="",
                 ca_path="",
                 exchange="logs",
                 environment="default",
                 service_name="lowball",
                 formatter_configuration=None
                 ):
        logging.Handler.__init__(self, level)
        if formatter_configuration is None or not isinstance(formatter_configuration, dict):
            formatter_configuration = {}
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.verify_ssl = verify_ssl
        self.ca_file = ca_file
        self.ca_path = ca_path
        self.exchange = exchange
        self.environment = environment
        self.service_name = service_name
        self.formatter = self.FORMATTER_CLASS(**formatter_configuration)
        self._connection = None
        self._channel = None

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        if not value:
            value = ""
        if not isinstance(value, str):
            raise ValueError("host must be a string")
        self._host = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if not isinstance(value, int) or not 0 < value < 65536:
            raise ValueError("Port must be a valid port in range 1-65535")
        self._port = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise ValueError("if set, username must be a string")
        self._username = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise ValueError("if set, password must be a string")
        self._password = value

    @property
    def use_ssl(self):
        return self._use_ssl

    @use_ssl.setter
    def use_ssl(self, value):
        if value is None:
            value = False
        if not isinstance(value, (str, int, bool)):
            raise ValueError("use_ssl must be True or False, but can also be 0,1")

        if isinstance(value, str):
            if value in ("True", "true", "TRUE"):
                value = True
            elif value in ("False", "false", "FALSE"):
                value = False
            else:
                raise ValueError("use_ssl should be True/False or a string True/False")

        if isinstance(value, int):
            value = bool(value)

        self._use_ssl = value

    @property
    def verify_ssl(self):
        return self._verify_ssl

    @verify_ssl.setter
    def verify_ssl(self, value):
        if value is None:
            value = False
        if not isinstance(value, (str, int, bool)):
            raise ValueError("verify_ssl must be True or False, but can also be 0,1")

        if isinstance(value, str):
            if value in ("True", "true", "TRUE"):
                value = True
            elif value in ("False", "false", "FALSE"):
                value = False
            else:
                raise ValueError("verify_ssl should be True/False or a string True/False")

        if isinstance(value, int):
            value = bool(value)
        self._verify_ssl = value

    @property
    def ca_file(self):
        return self._ca_file

    @ca_file.setter
    def ca_file(self, value):
        if not value:
            value = None
        elif not isinstance(value, str) or not os.path.exists(value) or not os.path.isfile(value):
            raise ValueError("ca_file if set must be a path to a valid file")
        self._ca_file = value

    @property
    def ca_path(self):
        return self._ca_path

    @ca_path.setter
    def ca_path(self, value):

        if not value:
            value = None

        elif not isinstance(value, str) or not os.path.exists(value) or not os.path.isdir(value):
            raise ValueError("ca_path if set must be a path to a valid directory")

        self._ca_path = value

    @property
    def exchange(self):
        return self._exchange

    @exchange.setter
    def exchange(self, value):
        if not value:
            value = self.DEFAULT_EXCHANGE

        if not isinstance(value, str):
            raise ValueError("exchange, if set, should be a string")
        self._exchange = value

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, value):
        if not value:
            value = self.DEFAULT_ENVIRONMENT

        if not isinstance(value, str):
            raise ValueError("exchange, if set, should be a string")
        self._environment = value

    @property
    def service_name(self):
        return self._service_name

    @service_name.setter
    def service_name(self, value):
        if not value:
            value = self.DEFAULT_SERVICE_NAME

        if not isinstance(value, str):
            raise ValueError("exchange, if set, should be a string")
        self._service_name = value

    def get_routing_key(self, log_level):

        return f"{self.environment}.{self.service_name}.{log_level}"

    def get_connection_parameters(self):
        connection_parameters = {
            "host": self.host,
            "port": self.port
        }

        if self.username:
            connection_parameters["credentials"] = pika.PlainCredentials(self.username, self.password)
        if self.use_ssl:
            context = ssl.create_default_context(cafile=self.ca_file, capath=self.ca_path)
            if not self.verify_ssl:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

            connection_parameters["ssl_options"] = pika.SSLOptions(context)

        return pika.ConnectionParameters(**connection_parameters)

    def _get_connection(self):
        self._close_connection()
        self._connection = pika.BlockingConnection(self.get_connection_parameters())
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange=self.exchange, exchange_type="topic")

    def _close_connection(self):

        try:
            self._connection.close()
        except:
            pass
        try:
            self._channel.close()
        except:
            pass
        self._connection = None
        self._channel = None

    def emit(self, record: LogRecord) -> None:

        if record.levelno < self.level:
            return

        self.acquire()
        try:
            # because we are using a blocking connection, we will only HB when we send a message
            # this is the only way to check liveliness, we assume connection if we have established
            if not self._connection or not self._channel:
                self._get_connection()
            message = self.format(record)
            self._channel.basic_publish(
                body=message,
                routing_key=self.get_routing_key(record.levelname),
                exchange=self.exchange
            )
        except Exception as err:
            try:
                # if the send fails, we attempt a fresh connection and send again.
                self._get_connection()
                message = self.format(record)
                self._channel.basic_publish(
                    body=message,
                    routing_key=self.get_routing_key(record.levelname),
                    exchange=self.exchange
                )
            except Exception as err:
                # twice errors are output to stderr
                print(f"Unable to submit log: {err}", file=sys.stderr)

        finally:
            self.release()
