from thread_pool import ThreadPool
from threading import Condition
from threading import Lock


class PyCentralDispatch:
  """
  This is a non-optimal implementation inspired by Apple's Grand Central Dispatch.
  I wrote this for convenience without much worry for optimization.

  Inspired by https://www.mikeash.com/pyblog/friday-qa-2015-09-04-lets-build-dispatch_queue.html
  """
  __thread_pool = ThreadPool()
  __global_queue_lock = Lock()
  __global_dispatch_queue = None  # Lazily initialized on call to `global_queue`.

  def __init__(self, is_serial_queue=False):
    self.__is_serial_queue = is_serial_queue
    self.__lock = Lock()
    # Stores a tuple of (function, args, kwargs)
    self.__pendingBlocks = []
    self.__is_serial_queue_active = False

  @classmethod
  def global_queue(cls):
    cls.__global_queue_lock.acquire()
    if not cls.__global_dispatch_queue:
      cls.__global_dispatch_queue = cls()
    cls.__global_queue_lock.release()
    return cls.__global_dispatch_queue

  def __dispatch_one_block(self):
    """Dispatches the most first block in the queue."""
    def lambda_like_function():
      """
      An inner function to act like a lambda. This block is passed to the
      thread pool to be dispatched to a thread.
      """
      self.__lock.acquire()
      block_tuple = self.__pendingBlocks.pop(0)
      block, args, kwargs = block_tuple
      self.__lock.release()
      block(*args, **kwargs)
      # If the queue is serial, continually dispatch blocks one after the
      # other to ensure serial execution on the same thread.
      if self.__is_serial_queue:
        self.__lock.acquire()
        if len(self.__pendingBlocks) > 0:
          self.__dispatchOneBlock()
        else:
          self.__is_serial_queue_active = False
        self.__lock.release()
    self.__class__.__thread_pool.addBlock(lambda_like_function)

  def dispatch_async(self, block, args=(), kwargs={}):
    """Dispatches asyncronously and then returns."""
    self.__lock.acquire()
    block_tuple = (block, args, kwargs)
    self.__pendingBlocks.append(block_tuple)
    if self.__is_serial_queue and not self.__is_serial_queue_active:
      self.__is_serial_queue_active = True
      self.__dispatch_one_block()
    elif not self.__is_serial_queue:
      self.__dispatch_one_block()
    self.__lock.release()

  def dispatch_sync(self, block, args=(), kwargs={}):
    """Dispatches synchronously before returning."""
    # Rather than implement something more complicated, piggyback off of
    # dispatch_async and just use a Condition to signal that the work is done
    # before returning.
    condition = Condition()
    # Mutable object to track the `done` state to be modified by the inner
    # function
    done = { 'state' : False }
    def lambda_like_function():
      block(*args, **kwargs)
      condition.acquire()
      done['state'] = True
      condition.notify()
      condition.release()
    self.dispatch_async(lambda_like_function)
    condition.acquire()
    while done['state'] is False:
      condition.wait()
    condition.release()
