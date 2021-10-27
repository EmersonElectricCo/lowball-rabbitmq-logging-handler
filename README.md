<h1 align="center">lowball-rabbitmq-logging-handler</h1>
<p align="center">
logging handler for lowball that leverages rabbitmq
</p>


## Overview
A lowball logging module that sends your microservice ecosystem logs to a rabbitmq service. 

By default it uses the builtin lowball log formatter `lowball.builtins.logging.formatter.DefaultFormatter` but this 
can be changed if desired. 

## Installation
### Using pip
`pip install lowball-rabbitmq-logging-handler`

### From Source
```shell
git clone https://github.com/EmersonElectricCo/lowball-rabbitmq-logging-handler.git
cd ./lowball-rabbitmq-logging-handler
pip install -r requirements.txt
python3 setup.py install
```


## Lowball Configuration

When configuring your lowball microservice, the `logging` section should be as follows. What is listed here is all
defaults. You only need to add the key of an option if you wish to change the default value. 

```yaml
meta: ...
application: ...
auth_provider: ...
auth_db: ...
logging:
  level: DEBUG
  host: "127.0.0.1"
  port: 5672
  username: ""
  password: ""
  use_ssl: false
  verify_ssl: true
  ca_file: ""
  ca_path: ""
  exchange: "logs"
  environment: "default"
  service_name: "lowball"
  formatter_configuration:
    date_format: "%Y-%m-%d %H:%M:%S.%fUTC"

```

the log level should be either the integer level or the string level as outlined by this table

ref [python logging](https://docs.python.org/3/library/logging.html)

| Level    | Integer Value |
| ---------|-------------- |
| CRITICAL | 50            |
| ERROR    | 40            |
| WARNING  | 30            |
| INFO     | 20            |
| DEBUG    | 10            |
| NOTSET   | 0             |

Python Logging does not care what the integer value entered is, but it does care that 
the string is one of these names. 

### RabbitMQ Interaction
The handler will establish a topic exchange within the targetted rabbitmq instance. 
The configuration fields of 

- exchange
- environment
- service_name

Directly correlate to the construction of the exchange and routing key. 

the exchange is directly defined by the `exchange` field

The routing key will be constructed as follows

`environment.service_name.log_level_of_record`

for example, in the above default configuration, if a `LogRecord` was submitted with level WARNING, would be 
sent to the exchange `logs` with the routing key `default.lowball.WARNING`

#### Example Consumer

```python
import pika
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
result = channel.queue_declare(queue="")
channel.exchange_declare(exchange="logs", exchange_type="topic")
channel.queue_bind(exchange="logs", queue=result.method.queue, routing_key="default.lowball.*")
def callback(ch, method, properties, body):
    print(f"routing_key: {method.routing_key}\nMessage: {body.decode()}")
channel.basic_consume(queue="", auto_ack=True, on_message_callback=callback)
channel.start_consuming()

```

log output when `GET /builtins/status`
```
routing_key: default.lowball.INFO
Message: {"name": "lowball", "msg": {"result": "200 OK"}, "args": [], "additional": {"user_agent": "curl/7.68.0", "src_ip": "127.0.0.1", "http_method": "GET", "url": "/builtins/status?", "status_code": 200, "client_data": {}}, "timestamp": "2021-10-26 13:56:00.010320UTC", "level": "INFO", "request_id": "f5c01744-fb7e-4bea-9f64-21f1e3e5924f"}
```


## Example Usage
```python
from lowball_rabbitmq_logging_handler import LowballRabbitMQLoggingHandler
from lowball import Lowball, require_admin

from lowball import config_from_file

app = Lowball(config=config_from_file("/path/to/config"), logging_handler=LowballRabbitMQLoggingHandler)

```

