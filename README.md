vetx-python-client
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

Input a JSON at the command line interface

```
python -m vertx loclahost:1234
> {"type": "register", "address": "discovery.versions"}

> exit

```