import keyboard
from utils.config import SortType
from utils.colors import Color
from utils.number import clamp
from utils.system import clear 

cl = Color()

class ListItem(dict):
  id: str
  name: str | None = None

class List:
  def __init__(self, items: list[ListItem | str], title: str | None = None, loop: bool = True, ordered: bool = True, multiple: bool = False, prefix: str | None = None, selector: str = '>', show_count: int = 10, before_screen: str | None = None, horizontal: bool = False):
    self.items: list[ListItem | str] = []
    self.selected = []
    self.__current_index = 0
    for item in items:
      if type(item) is str:
        self.items.append({"id": item})
      else:
        self.items.append(item)
    self.title = title
    self.loop = loop
    self.ordered = ordered
    self.multiple = multiple
    self.prefix = prefix
    self.selector = selector
    self.show_count = show_count
    self.before_screen = before_screen
    self.horizontal = horizontal
    
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
      
  def get_index(self):
    self.show()
    
    keyboard.add_hotkey('left' if self.horizontal else 'up', lambda: self.__up())
    keyboard.add_hotkey('right' if self.horizontal else 'down', lambda: self.__down())

    if self.multiple:
      keyboard.add_hotkey('space', lambda: self.__select_current())
      keyboard.add_hotkey('ctrl+a', lambda: self.select_all_toggle())

    keyboard.wait('enter')
    clear()
    return self.__current_index
  def get_value(self) -> str:
    index = self.get_index()
    return self.items[index].get('id')
  def show(self):
    clear()
    if self.before_screen != None:
      print(self.before_screen)
      if self.title != None:
        print(cl.change(''.rjust(len(self.title), '-'), cl.text.GREY))

    show_count_half = round(self.show_count / 2)
    greater_than_show_count = len(self.items) >= self.show_count
    items = list(filter(lambda i: i >= self.__current_index - show_count_half and i <= self.__current_index + show_count_half, range(len(self.items))))
    reversed_items = self.items.copy()
    reversed_items.reverse()

    if len(items) < self.show_count and len(self.items) > self.show_count:
      if items[len(items) - 1] >= len(self.items) - 1: 
        for index in range(self.show_count - len(items)):
          items.append(index)
      else:
        for index in range(len(reversed_items) - 1, len(reversed_items) - self.show_count + len(items) - 1, -1):
          items.insert(0, index)

    if self.multiple:
      print(cl.change('(SPACE to select, CTRL+A for All)', cl.text.GREY))
    if self.title != None:
      if self.prefix != None:
        print(cl.change(self.prefix, cl.text.BLUE), end=' ')
      print(self.title)
      print(cl.change(''.rjust(len(self.title), '-'), cl.text.GREY))

    for index in items:
      item = self.items[index]
      value = item.get('name') or item.get('id')
      prefix = (f'{index + 1}'.rjust(len(str(len(items)))) + '.' if self.ordered else '-') + ' ' if not self.horizontal else ''
      is_selected = index in self.selected
      is_current_index = index == self.__current_index
      term = (f'{self.selector} ' if is_selected else '  ') + prefix + value if self.multiple else prefix + value

      end = '\n' if not self.horizontal or (self.horizontal and index == len(items) - 1) else ' | '
      if index == 0 and greater_than_show_count and not self.horizontal:
        print(cl.change('---', cl.text.GREY))
      if is_current_index:
        print(cl.change(term, cl.text.BLUE), end='')
      else:
        print(term, end='')
      print(end, end='')
    print()