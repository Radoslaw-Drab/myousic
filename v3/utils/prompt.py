import keyboard
from typing import Callable
from utils.config import SortType
from utils.classes import Listener
from utils.colors import Color
from utils.number import clamp
from utils.system import clear 

cl = Color()

class Input:
  def __init__(self, title: str | None = None, *prompts: list[str]):
    self.__prompts = prompts
    self.__values: list[str] = []
    self.__title = title
    pass
  def start(self, clearScreen: bool = True):
    if clearScreen:
      clear()
    if self.__title:
      print(self.__title)
    for prompt in self.__prompts:
      self.__values.append(input(prompt))
    return self.__values

class ListItem(dict):
  id: str
  name: str | None = None
class ListSortFunction(Callable[[str, SortType], list[ListItem | str]]):
  pass
class List:
  def __init__(self, items: list[ListItem | str | None], title: str | None = None, loop: bool = True, ordered: bool = True, multiple: bool = False, prefix: str | None = None, selector: str = '>', show_count: int = 10, before_screen: str | None = None, horizontal: bool = False, sort_types: list[str] | None = None, sort_listener: ListSortFunction | None = None, show_info: bool = True):
    self.items: list[ListItem] = self.__set_items(items)
    self.selected = []
    self.__current_index: int = 0

    self.title = title
    self.loop = loop
    self.ordered = ordered
    self.multiple = multiple
    self.prefix = prefix
    self.selector = selector
    self.show_count = show_count
    self.before_screen = before_screen
    self.horizontal = horizontal
    self.sort_types = sort_types
    self.sort_type_index: int = -1
    self.sort_dir: SortType = SortType.ASC
    self.__allow_show_info = show_info
    self.__show_info: bool = True
    self.__set_ended(False)

    self.__sort_listener = Listener() 
    
    if sort_listener:
      self.__sort_listener.set(sort_listener)
  
  def __repr__(self):
    return self.get_index()
  
  def __set_items(self, items: list[ListItem | str | None], replace: bool = True):
    new_items: list[ListItem] = [] if replace else self.items

    for item in items:
      if type(item) is str:
        new_items.append({"id": item})
      elif type(item) is dict:
        new_items.append(item)
    self.items = new_items
    
    return new_items
  
  def __up(self):
    if self.loop:
      self.__current_index -= 1
      if self.__current_index < 0:
        self.__current_index = len(self.items) - 1
    else:
      self.__current_index = clamp(self.__current_index - 1, 0, len(self.items) - 1)
    self.show()
  def __down(self):
    if self.loop:
      self.__current_index += 1
      if self.__current_index >= len(self.items):
        self.__current_index = 0
    else:
      self.__current_index = clamp(self.__current_index + 1, 0, len(self.items) - 1)
    self.show()
  def __select_current(self):
    self.__select(self.__current_index)
  def __select(self, index: int): 
    if index in self.selected:
      self.selected = list(filter(lambda i: i != index, self.selected))
    else:
      self.selected.append(index)
    self.show()
  def select_all_toggle(self):
    if len(self.selected) == len(self.items):
      self.selected = []
    else:
      self.selected = [i for i in range(len(self.items))]
    self.show()
      
  def __toggle_show_info(self):
    if self.__allow_show_info:
      self.__show_info = not self.__show_info
      self.show()
  def __set_ended(self, value: bool):
    self.__ended = value
  def get_index(self):
    self.show()
    keyboard.add_hotkey('enter', lambda: self.__set_ended(True))
    keyboard.add_hotkey('left' if self.horizontal else 'up', lambda: self.__up())
    keyboard.add_hotkey('right' if self.horizontal else 'down', lambda: self.__down())

    if self.multiple:
      keyboard.add_hotkey('space', lambda: self.__select_current())
      keyboard.add_hotkey('ctrl+a', lambda: self.select_all_toggle())
    if self.sort_types != None and len(self.sort_types) > 0:
      keyboard.add_hotkey('page up', lambda: self.__change_sort())
      keyboard.add_hotkey('page down', lambda: self.__change_sort(-1))
      keyboard.add_hotkey('tab', lambda: self.__change_sort_dir())
    keyboard.add_hotkey('ctrl+i', lambda: self.__toggle_show_info())
    input()
    clear()
    return self.__current_index
  def get_value(self):
    index = self.get_index()
    return self.items[index].get('id')
  def show(self):
    if self.__ended: 
      return
    clear()
    show_count_half = round(self.show_count / 2)
    greater_than_show_count = len(self.items) >= self.show_count
    items = list(filter(lambda i: i >= self.__current_index - show_count_half and i < self.__current_index + show_count_half, range(len(self.items))))

    if len(items) < self.show_count and len(self.items) > self.show_count:
      is_last = items[len(items) - 1] >= len(self.items) - 1
      if is_last: 
        for index in range(self.show_count - len(items)):
          items.append(index)
      else:
        reversed_items = self.items.copy()
        reversed_items.reverse()
        for index in range(len(reversed_items) - 1, len(reversed_items) - self.show_count + len(items) - 1, -1):
          items.insert(0, index)
    self.show_info()

    longestItemSize = max(0, *[len(item.get('name') or item.get('id')) for item in self.items])
    for index in items:
      item = self.items[index]
      value = item.get('name') or item.get('id')
      prefix = (f'{index + 1}'.rjust(len(str(len(items)))) + '.' if self.ordered else '-') + ' ' if not self.horizontal else ''
      is_selected = index in self.selected
      is_current_index = index == self.__current_index
      term = (f'{self.selector} ' if is_selected else '  ') + prefix + value if self.multiple else prefix + value

      end = '\n' if not self.horizontal or (self.horizontal and index == len(items) - 1) else ' | '
      print_line = index == 0 and index != items[0] and greater_than_show_count and not self.horizontal
      has_items_from_end = index < items[0]
      is_last = index == items[len(items) - 1]
      if print_line:
        print(cl.change(''.ljust(longestItemSize + len(prefix), '-'), cl.text.GREY))

      if is_current_index:
        print(cl.change(term, cl.text.BLUE), end='')
      else:
        print(term, end='')
      # print(is_first, is_last, end='')
      print(end, end='')
      if not has_items_from_end and is_last:
        print()

  def show_info(self):
    if self.__allow_show_info:
      print(cl.change('CTRL + I for info', cl.text.GREY))

    if self.before_screen != None:
      print(self.before_screen)
      if self.title != None:
        print(cl.change(''.rjust(len(self.title), '-'), cl.text.GREY))


    if self.multiple and self.__show_info:
      print(cl.change('(SPACE to select, CTRL+A for All)', cl.text.GREY))
    

    if self.title != None:
      if self.prefix != None:
        print(cl.change(self.prefix, cl.text.BLUE), end=' ')
      print(self.title)
      
    if self.sort_types != None and len(self.sort_types) > 0:
      print('Sort:', end=' ')
      if self.sort_type_index != -1:
        print(f'{cl.change(self.sort_types[self.sort_type_index], cl.options.URL)} ({self.sort_dir.value.upper()})', end=' ')
      else:
        print('-', end=' ')
        
      if self.__show_info:
        print(cl.change('(Page Up/Down and TAB to change)', cl.text.GREY))
      else:
        print()

    if self.title != None:
      print(cl.change(''.rjust(len(self.title), '-'), cl.text.GREY))

  def __change_sort(self, step: int = 1):
    self.sort_type_index += max(min(step, 1), -1)
    if self.sort_type_index >= len(self.sort_types):
      self.sort_type_index = -1
    if self.sort_type_index < -1:
      self.sort_type_index = len(self.sort_types) - 1
    self.__set_items(self.__sort_listener.emit(self.sort_types[self.sort_type_index], self.sort_dir))
    self.show()
  def __change_sort_dir(self):
    if self.sort_type_index != -1:  
      if self.sort_dir == SortType.ASC:
        self.sort_dir = SortType.DESC
      else:
        self.sort_dir = SortType.ASC
      self.__set_items(self.__sort_listener.emit(self.sort_types[self.sort_type_index], self.sort_dir))
      self.show()
  def set_sort_listener(self, listener: ListSortFunction | None):
    self.__sort_listener.set(listener)
