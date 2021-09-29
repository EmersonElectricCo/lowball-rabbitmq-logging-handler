import logging
import sys
from logging import LogRecord
import pika
import ssl
from pika import credentials
from lowball.builtins.logging.formatter import DefaultFormatter


class LowballRabbitMQLoggingHandler(logging.Handler):

    FORMATTER_CLASS = DefaultFormatter

    DEFAULT_ENVIRONMENT = "default"
    DEFAULT_SERVICE_NAME = "lowball"

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
        if formatter_configuration is None:
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
        self.formatter_configuration = formatter_configuration
        self.formatter = self.FORMATTER_CLASS(**self.formatter_configuration)
        self._connection = None
        self._channel = None

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def use_ssl(self):
        return self.use_ssl

    @use_ssl.setter
    def use_ssl(self, value):
        self._use_ssl = value

    @property
    def verify_ssl(self):
        return self._verify_ssl

    @verify_ssl.setter
    def verify_ssl(self, value):
        self._verify_ssl = value

    @property
    def ca_file(self):
        return self._ca_file

    @ca_file.setter
    def ca_file(self, value):
        self._ca_file = value

    @property
    def ca_path(self):
        return self._ca_path

    @ca_path.setter
    def ca_path(self, value):
        self._ca_path = value

    @property
    def exchange(self):
        return self._exchange

    @exchange.setter
    def exchange(self, value):
        self._exchange = value

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, value):
        self._environment = value

    @property
    def service_name(self):
        return self._service_name

    @service_name.setter
    def service_name(self, value):
        self._service_name = value

    @property
    def formatter_configuration(self):
        return self._formatter_configuration

    @formatter_configuration.setter
    def formatter_configuration(self, value):
        self._formatter_configuration = value

    def get_routing_key(self, log_level):
        environ = self.environment if self.environment else self.DEFAULT_ENVIRONMENT
        sname = self.name if self.name else self.DEFAULT_SERVICE_NAME

        return f"{environ}.{sname}.{log_level}"

    def get_connection_parameters(self):
        connection_parameters = {}

        if self.username:
            connection_parameters["credentials"] = pika.PlainCredentials(self.username, self.password)
        if self.use_ssl:
            context = ssl.create_default_context(cafile=self.ca_file, capath=self.ca_path)
            if not self.verify_ssl:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

            connection_parameters["ssl_options"] = pika.SSLOptions(context)

        return pika.ConnectionParameters(**connection_parameters)

    def get_connection(self):

        if any([not self._connection or not self._connection.is_open, not self._channel or not self._channel.is_open]):

            self.close_connection()
            self._connection = pika.BlockingConnection(self.get_connection_parameters())
            self._channel = self._connection.channel()
            self._channel.exchange_declare(exchange=self.exchange, exchange_type="topic")

    def close_connection(self):

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

        self.acquire()
        try:
            self.get_connection()
            message = self.format(record)
            self._channel.basic_publish(
                body=message,
                routing_key=self.get_routing_key(record.levelname),
                exchange=self.exchange
            )
        except Exception as err:
            print("Unable to submit log: {err}", file=sys.stderr)

        finally:
            self.release()
