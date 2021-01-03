# PyCentralDispatch
A Grand Central Dispatch (GCD) inspired API for python. Not optimal, mostly just for convenience.

Inspired by Mike Ash's [article](https://www.mikeash.com/pyblog/friday-qa-2015-09-04-lets-build-dispatch_queue.html).

## Install

Install the package using `pip`.

```
python3 -m pip install pycentraldispatch
```

## API

The general behavior of this API is inspired by Apple's [Grand Central Dispatch (GCD)](https://en.wikipedia.org/wiki/Grand_Central_Dispatch). The API allows for dispatching
tasks (functions) `synchronously` or `asynchronously`. There are two flavors of queues: `serial` and `concurrent`.

`serial` - Tasks will be executed one-at-a-time in the order they are queued.

`concurrent` - Tasks may be executed in parallel, but they will be started in the order they are queued. 

Additionally, the API provides access to a `global` queue, which is a default singleton concurrent queue that
can be shared across the application.

The primary APIs are `dispatch_sync` and `dispatch_async`, which dispatch the task onto a queue, either
synchronously or asynchronously. The primary difference is that synchronous tasks do not return until the
task is completed. Asynchronous tasks will be run in the background and return from the dispatch call
immediately.

### Global queue

A shared concurrent queue singleton for access across the application.

```
from pycentraldispatch import PyCentralDispatch

# This same singleton queue can be used anywhere in the application.
global_queue = PyCentralDispatch.global_queue()

def some_function():
  print 'hello'

global_queue.dispatch_sync(some_function)  # Prints "hello"
```

### Serial queues

Serial queues do not provide any parallelization. They execute tasks one-at-a-time in the order they were received.

```
from pycentraldispatch import PyCentralDispatch

local_serial_queue = PyCentralDispatch.create_queue(is_serial_queue=True)

def some_function_with_parameters(a, b):
  print a + b
  
local_serial_queue.dispatch_async(some_function_with_parameters, args=(3, 5))  # Prints `8`
```

### Concurrent queues

Concurrent queues allow for tasks to execute in parallel. However the tasks are started in the order they were queued.

```
from pycentraldispatch import PyCentralDispatch

local_concurrent_queue = PyCentralDispatch.create_queue()  # Defaults to concurrent queue.

def some_function_with_parameters(a, b=5):
  print a + b

local_concurrent_queue.dispatch_async(some_function_with_parameters, args=(3,), kwargs={'b' : 3})  # Prints `6`
```
