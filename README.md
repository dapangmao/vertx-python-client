vertx-python-client
---

An asynchronous TCP eventbus Python client other than the thread-based [official client](https://github.com/vert-x3/vertx-eventbus-bridge-clients/tree/master/python)


### Feature

1. Use the event loop from Python 3 for high performance
2. Provide a command line interface


### Install 


```
pip install git+https://github.com/dapangmao/vertx-python-client
```

### Usage 



```python

from vertx import EventBus, Payload
import time

eb = EventBus(host='localhost', port=1011)
eb.connect()
eb.add_listen_func("discovery.versions", lambda x: print(x))
# Send the JSON binary
reg = Payload(type="register", address="api.versions")
eb.send(reg)
pub = Payload(type="publish", address="api.versions.get", replyAddress="api.versions")
eb.send(pub)
time.sleep(3)
eb.disconnect()
```

Instead use the command line interface

```
python -m vertx loclahost:1234
> {"type": "register", "address": "discovery.versions"}

> exit

```


### test

``` 
pytest tests --log-level=DEBUG
```