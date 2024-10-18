from typing import Callable

class Listener:
  def __init__(self, listener: Callable | None = None):
    self.__listener = self.set(listener)
    pass
  def set(self, listener: Callable | None):
    self.__listener = listener
  def emit(self, *args):
    return self.__listener(*args) if self.__listener != None else None
class Listeners:
  def __init__(self, listeners: list[Callable] = []):
    self.__listeners: list[Callable] = listeners
    pass
  def add(self, listener: Callable):
    self.__listeners.append(listener)
    return len(self.__listeners) - 1
  def remove(self, index: int):
    self.__listeners = list(filter(lambda _, i: i != index, self.__listeners))
  def emit(self, *args):
    output: list[tuple[int, list[any]]] = []
    for listener_index in range(len(self.__listeners)):
      listener = self.__listeners[listener_index]
      values = listener(*args)
      output.append((listener_index, [*values]))
    return output