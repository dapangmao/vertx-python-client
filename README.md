vertx-python-client
---

An asynchronous TCP eventbus Python client


### Feature

1. Use the event loop from Python 3 for high performance
2. Provide a command line interface


### Install 


```
pip install git+https://github.com/dapangmao/vertx-python-client
```

### Usage 



```python

from vertx import EventBus, Delivery

import time
eb = EventBus(host='localhost', port=1011)
eb.connect()
eb.add_listen_func("discovery.versions", lambda x: print(x))

reg = Delivery(type="register", address="api.versions")
eb.send(reg)
pub = Delivery(type="publish", address="api.versions.get", replyAddress="api.versions")
eb.send(pub)
time.sleep(3)
eb.disconnect()
```

Input a JSON at the command line interface

```
python -m vertx loclahost:1234
> {"type": "register", "address": "discovery.versions"}

> exit

```