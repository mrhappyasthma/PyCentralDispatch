from threading import Condition
from threading import Thread

class ThreadPool:
  """
  This class manages a pool of threads that are lazily spawned as needed to
  handle blocks (functions) that are queued from py_central_dispatch.

  Inspired by https://www.mikeash.com/pyblog/friday-qa-2015-09-04-lets-build-dispatch_queue.html
  """

  def __init__(self):
    self.__threadCount = 0
    self.__activeThreadCount = 0
    self.__threadLimit = 128;  # Arbitrary value
    self.__conditionLock = Condition()
    self.__blocks = []

  def __thread_loop(self):
    # Acquire the lock before the main loop, as each iteration is expected to
    # start and end while holding the lock.
    self.__conditionLock.acquire()
    while True:
      # If there's no pending blocks to execute, just wait until signaled.
      while len(self.__blocks) == 0:
        self.__conditionLock.wait()
      # Extract the first pending block to execute and increment the active
      # thread counter.
      currentLambda = self.__blocks.pop(0)
      self.__activeThreadCount += 1
      # Free the lock before executing the block to allow another thread to
      # continue if needed.
      self.__conditionLock.release()
      currentLambda()
      # After the work is done, acquire the lock and decrement the active
      # thread count since this thread is now free again.
      self.__conditionLock.acquire()
      self.__activeThreadCount -= 1

  def addBlock(self, block):
    self.__conditionLock.acquire()
    self.__blocks.append(block)
    # If there are more pending blocks than there are idle threads and the
    # number of threads hasn't reached the `__threadLimit`, then spawn another
    # thread.
    numIdleThreads = self.__threadCount - self.__activeThreadCount
    if len(self.__blocks) > numIdleThreads and self.__threadCount < self.__threadLimit:
      thread = Thread(target=self.__thread_loop)
      thread.setDaemon(True)
      thread.start()
      self.__threadCount += 1
    self.__conditionLock.notify()
    self.__conditionLock.release()
