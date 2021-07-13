import logging
from logging import LogRecord
import pika
import ssl
from pika import credentials
from lowball.builtins.logging.formatter import DefaultFormatter


class LowballRabbitMQLoggingHandler(logging.Handler):

    FORMATTER_CLASS = DefaultFormatter

    def __init__(self,
                 level=logging.DEBUG,  # 10
                 host="127.0.0.1",
                 port=5672,
                 username=None,
                 password=None,
                 use_ssl=False,
                 verify_ssl=True,
                 exchange="logs",
                 environment="default",
                 formatter_configuration=None
                 ):
        logging.Handler.__init__(self, level)

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.verify_ssl = verify_ssl
        self.exchange = exchange
        self.environment = environment
        self.formatter_configuration = formatter_configuration
        self.formatter = self.FORMATTER_CLASS(**self.formatter_configuration)

    @property
    def host(self):
        return

    @host.setter
    def host(self, value):
        pass

    @property
    def port(self):
        return

    @port.setter
    def port(self, value):
        pass

    @property
    def username(self):
        return

    @username.setter
    def username(self, value):
        pass

    @property
    def password(self):
        return

    @password.setter
    def password(self, value):
        pass

    @property
    def use_ssl(self):
        return

    @use_ssl.setter
    def use_ssl(self, value):
        pass

    @property
    def verify_ssl(self):
        return

    @verify_ssl.setter
    def verify_ssl(self, value):
        pass

    @property
    def exchange(self):
        return

    @exchange.setter
    def exchange(self, value):
        pass

    @property
    def environment(self):
        return

    @environment.setter
    def environment(self, value):
        pass

    @property
    def formatter_configuration(self):
        return

    @formatter_configuration.setter
    def formatter_configuration(self, value):
        pass

    @property
    def connection_parameters(self):
        return

    def create_connection(self):

        pass

    def close_connection(self):

        pass

    def emit(self, record: LogRecord) -> None:

        pass
