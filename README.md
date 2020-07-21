vertx-python-client
---

An asynchronous TCP eventbus Python client other than the thread-based [official client](https://github.com/vert-x3/vertx-eventbus-bridge-clients/tree/master/python)


### Feature

1. Use the event loop from Python 3 for high performance 
2. No dependency
3. Provide a command line interface


### Install 


```
pip install vertx-python-client
```

### Usage 

1. use as a command line interface

``` 
# specify an IP and a port
python -m vertx localhost:1234
> {"type": "register", "address": "api.versions"}
> {"type": "publish", "address": "api.versions.get", "replyAddress": "api.versions"}
> exit

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
pytest --log-cli-level=DEBUG tests
```
