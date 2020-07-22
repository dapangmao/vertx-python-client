vertx-python-client
---

An asynchronous TCP eventbus Python client other than the thread-based [official client](https://github.com/vert-x3/vertx-eventbus-bridge-clients/tree/master/python)


### Feature

1. Asynchronous
2. No dependency
3. Provides a command line interface


### Install 

```
pip install vertx-python-client
```

### Usage 

1. use as a command line interface

``` 
python -m vertx localhost 8080

Welcome to the VertX shell. Type help or ? to list commands.
Press CTRL+C twice to quit

>> {"type": "register", "address": "app.version"}
07/21/20 07:48:00 - INFO: {'type': 'pong'}
```

2. use as a standard Python library

```python
from vertx import EventBusAsync, EventBusAsync

eb = EventBusAsync(host='localhost', port=1234)
eb.connect()
eb.add_listen_func(address="api.versions", action=lambda x: print(x))

# Send a JSON payload
reg = EventBusAsync(type="register", address="api.version")
eb.send(reg)
pub = EventBusAsync(type="publish", address="api.versions.", replyAddress="api.version")
eb.send(pub)

# Quit the connection
eb.disconnect()
```




### Test

``` 
pytest tests
```
