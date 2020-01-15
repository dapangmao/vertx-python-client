vertx-python-client
---

An asynchronous TCP eventbus Python client other than the thread-based [official client](https://github.com/vert-x3/vertx-eventbus-bridge-clients/tree/master/python)


### Feature

1. Use the event loop from Python 3 for high performance
2. Provide a command line interface


### Install 


```
pip install vertx-python-client
```

### Usage 

Use as a standard Python library

```python


from vertx import EventBus, Payload

eb = EventBus(host='localhost', port=1234)
eb.connect()
eb.add_listen_func(address="api.versions", action=lambda x: print(x))

# Send the JSON binary
reg = Payload(type="register", address="api.versions")
eb.send(reg)
pub = Payload(type="publish", address="api.versions.get", replyAddress="api.versions")
eb.send(pub)

# Quit the connection
eb.disconnect()
```

Instead use from the command line interface

```
python -m vertx localhost:1234
> {"type": "register", "address": "api.versions"}
> {"type": "publish", "address": "api.versions.get", "replyAddress": "api.versions"}
> exit

```


### Test

``` 
pytest --log-cli-level=DEBUG tests
```
