
import pytest
from lowball_rabbitmq_logging_handler.lowball_rabbitmq_logging_handler import pika, sys
from unittest.mock import Mock, MagicMock, PropertyMock
from logging import LogRecord
import logging
from pika.channel import Channel


@pytest.fixture
def mock_pika_open_channel(monkeypatch):

    mock_channel = Channel
    monkeypatch.setattr(mock_channel, "__init__", Mock(return_value=None))
    monkeypatch.setattr(mock_channel, "is_open", PropertyMock(return_value=True))
    monkeypatch.setattr(mock_channel, "is_closed", PropertyMock(return_value=False))
    monkeypatch.setattr(mock_channel, "exchange_declare", Mock())
    monkeypatch.setattr(pika.BlockingConnection, "channel", Mock(return_value=mock_channel()))
    monkeypatch.setattr(mock_channel, "basic_publish", Mock())
    monkeypatch.setattr(mock_channel, "close", Mock())

@pytest.fixture
def mock_pika_open_channel_error_first_pub(monkeypatch):
    mock_channel = Channel
    monkeypatch.setattr(mock_channel, "__init__", Mock(return_value=None))
    monkeypatch.setattr(mock_channel, "is_open", PropertyMock(return_value=True))
    monkeypatch.setattr(mock_channel, "is_closed", PropertyMock(return_value=False))
    monkeypatch.setattr(mock_channel, "exchange_declare", Mock())
    monkeypatch.setattr(pika.BlockingConnection, "channel", Mock(return_value=mock_channel()))
    monkeypatch.setattr(mock_channel, "basic_publish", Mock(side_effect=[Exception, None]))
    monkeypatch.setattr(mock_channel, "close", Mock())


@pytest.fixture
def mock_pika_open_channel_error_all_pub(monkeypatch):
    mock_channel = Channel
    monkeypatch.setattr(mock_channel, "__init__", Mock(return_value=None))
    monkeypatch.setattr(mock_channel, "is_open", PropertyMock(return_value=True))
    monkeypatch.setattr(mock_channel, "is_closed", PropertyMock(return_value=False))
    monkeypatch.setattr(mock_channel, "exchange_declare", Mock())
    monkeypatch.setattr(pika.BlockingConnection, "channel", Mock(return_value=mock_channel()))
    monkeypatch.setattr(mock_channel, "basic_publish", Mock(side_effect=[Exception, Exception, None]))
    monkeypatch.setattr(mock_channel, "close", Mock())

@pytest.fixture
def mock_pika_closed_channel(monkeypatch):

    mock_channel = Channel
    monkeypatch.setattr(mock_channel, "__init__", Mock(return_value=None))
    monkeypatch.setattr(mock_channel, "is_open", PropertyMock(return_value=False))
    monkeypatch.setattr(mock_channel, "is_closed", PropertyMock(return_value=True))
    monkeypatch.setattr(mock_channel, "exchange_declare", Mock())
    monkeypatch.setattr(pika.BlockingConnection, "channel", Mock(return_value=mock_channel()))
    monkeypatch.setattr(mock_channel, "basic_publish", Mock())
    monkeypatch.setattr(mock_channel, "close", Mock())


@pytest.fixture
def mock_pika_open_blocking_connection(monkeypatch):

    monkeypatch.setattr(pika.BlockingConnection, "__init__", Mock(return_value=None))
    monkeypatch.setattr(pika.BlockingConnection, "is_open", PropertyMock(return_value=True))
    monkeypatch.setattr(pika.BlockingConnection, "is_closed", PropertyMock(return_value=False))


@pytest.fixture
def mock_pika_closed_blocking_connection(monkeypatch):
    monkeypatch.setattr(pika.BlockingConnection, "__init__", Mock(return_value=None))
    monkeypatch.setattr(pika.BlockingConnection, "is_open", PropertyMock(return_value=False))
    monkeypatch.setattr(pika.BlockingConnection, "is_closed", PropertyMock(return_value=True))

@pytest.fixture()
def test_log_record():

    return LogRecord("Test", logging.INFO, "/test/", 10, "a log!", (), None)
