from typing import Self
import os
import math
import keyboard
import colors

def clear():
  os.system('cls' if os.name=='nt' else 'clear')
def clamp(value: int | float, minValue: int | float, maxValue: int | float):
  return max(min(value, maxValue), minValue)

class Column(dict):
  id: str
  value: str
  percent: int | str | None = None
class ValueColumn(dict):
  id: str
  value: str
class Options(dict): 
  separator: str = '|'
  minSize: int = 50
  sizePercent: int | None = None
  ordered: bool = False

class Table:
  options: Options = {
    "separator": "|",
    "minSize": 50,
    "ordered": True
  }
  columns: list[Column] = []

  def __init__(self, columns: list[Column], options: Options = {}):
    self.columns = columns
    self.options = {**self.options, **options}

    if self.options['ordered']:
      self.columns = [{"id": "index", "value": "ID", "percent": "min"}, *self.columns]
    pass
  def create(self, values: list[list[str]]):
    newValues = [[f'{index}', *values[index]] for index in range(len(values))]
    def getAllInColumn(self: Self, columnIndex: int, includeHeader: bool = False):
      columnValues: list[str] = [c['value'] for c in self.columns]
      values = [columnValues, *newValues] if includeHeader else newValues
      return [row[columnIndex] for row in values]

    def findMaxSize(self: Self, columnIndex: int):
      maxSize = 0
      valuesInColumn = getAllInColumn(self, columnIndex, True)
      for value in valuesInColumn:
        length = len(value)
        if length > maxSize:
          maxSize = length
      return maxSize
    def getMaxWidth(self: Self):
      maxSize = 0
      for i in range(len(self.columns)):
        separatorSpace = len(f'{separator} ' if i < len(self.columns) - 1 else '\n')
        maxSize += findMaxSize(self, i) + separatorSpace
        print(maxSize, i, findMaxSize(self, i), separatorSpace)
      return maxSize
        
    def line():
      print(''.ljust(size if size != 'auto' else getMaxWidth(self), '-'))

    
    size = max(math.floor(clamp(self.options['sizePercent'], 0, 100) / 100 * os.get_terminal_size().columns), self.options.get('minSize') or 25) if self.options.get('sizePercent') else 'auto'
    print(self.options, size)
    separator = self.options['separator']

    columnSizes: list[int | str | None] = []

    for i in range(len(self.columns)):
      c = self.columns[i]
      percent = c.get('percent')
      if percent == None or percent == 'auto':
        columnSizes.append(None)
      elif type(percent) is str:
        maxSize = findMaxSize(self, i)
        if percent == 'min':
          columnSizes.append(maxSize)
      elif type(percent) is int and size != 'auto':
        columnSizes.append(math.floor(clamp(c['percent'], 0, 100) / 100 * size))
      else:
        columnSizes.append(None)

    # columnSizes = [math.floor(clamp(c['percent'], 0, 100) / 100 * size) if c.get('percent') != None else None for c in self.columns]
    autoSize = 0
    autoColumns = 0
    for s in columnSizes:
      if s != None:
        autoSize += s
      else:
        autoColumns += 1
    columns = [s if s != None else math.floor(autoSize / autoColumns) for s in columnSizes] 
    print(columns, autoSize)

    def row(values: list[ValueColumn | str], header: bool = False, index: int = -1):
      for i in range(len(values)):
        separatorSpace = f'{separator} ' if i < len(values) - 1 else '\n'
        s = columns[i] + len(separatorSpace) - 1
        c = values[i]
        value: str = c if type(c) is str else c.get('value')
        print(value.ljust(s), end=separatorSpace)
        # prefix = '' if header or i > 0 else ('- ' if index < 0 else f'{index}. ')
        # print((prefix + value).ljust(s), end=separatorSpace)

    line()
    row(self.columns, True)
    # for i in range(len(self.columns)):
    #   separatorSpace = f'{separator} ' if i < len(self.columns) - 1 else f'{separator}\n'
    #   s = columns[i] - len(separatorSpace)
    #   c = self.columns[i]
    #   value: str = c['value']
    #   print(value.ljust(s), end=separatorSpace)
      # print(value, end=self.options['separator'])
    line()
    for i in range(len(newValues)):
      value = newValues[i]
      row(value, index=(i + 1 if self.options['ordered'] else -1))
    line()

    

table = Table([{"id": 'id', "value": "Id", "percent": "min"}, {"id": 'value', "value": "Value", "percent": "min"}, {"id": "custom", "value": "Custom"}])

# table.create([
#   ["Testing", "More", "Custom test"],
#   ["Other", "hehe", "Test"],
#   ["Other", "hehe", "Test"],
#   ["Other", "hehe", "Test"],
#   ["Other", "hehe", "Test"],
#   ["Other", "hehe", "Test"],
#   ["Other", "hehe", "Test"],
#   ["Other", "hehe", "Test"],
#   ["Other", "hehe", "Test"],

# ])

cl = colors.Color()
class ListItem(dict):
  id: str
  name: str | None = None
class List:
  # __currentIndex: int = 0
  # title: str = 'Select:'
  # items: list[ListItem] = []
  # ordered: bool
  # loop: bool
  # multiple: bool
  # selected: list[int] = []
  # prefix: str | None
  # selector: str = '>'
  # showCount: int = 10
  # beforeScreen: str | None = None
  def __init__(self, items: list[ListItem | str], title: str | None = None, loop: bool = True, ordered: bool = True, multiple: bool = False, prefix: str | None = None, selector: str = '>', showCount: int = 10, beforeScreen: str | None = None, horizontal: bool = False):
    self.items = []
    self.selected = []
    self.__currentIndex = 0
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
    self.showCount = showCount
    self.beforeScreen = beforeScreen
    self.horizontal = horizontal
  def __up(self):
    if self.loop:
      self.__currentIndex -= 1
      if self.__currentIndex < 0:
        self.__currentIndex = len(self.items) - 1
    else:
      self.__currentIndex = clamp(self.__currentIndex - 1, 0, len(self.items) - 1)
    self.show()
      
  def __down(self):
    if self.loop:
      self.__currentIndex += 1
      if self.__currentIndex >= len(self.items):
        self.__currentIndex = 0
    else:
      self.__currentIndex = clamp(self.__currentIndex + 1, 0, len(self.items) - 1)
    self.show()
  def selectAllToggle(self):
    if len(self.selected) == len(self.items):
      self.selected = []
    else:
      self.selected = [i for i in range(len(self.items))]
    self.show()
  def __selectCurrent(self):
    self.__select(self.__currentIndex)
  def __select(self, index: int): 
    if index in self.selected:
      self.selected = list(filter(lambda i: i != index, self.selected))
    else:
      self.selected.append(index)
    self.show()
      
  def getIndex(self):
    self.show()
    
    keyboard.add_hotkey('up', lambda: self.__up())
    keyboard.add_hotkey('down', lambda: self.__down())
    if self.multiple:
      keyboard.add_hotkey('space', lambda: self.__selectCurrent())
      keyboard.add_hotkey('ctrl+a', lambda: self.selectAllToggle())

    keyboard.wait('enter')
    clear()
    return self.__currentIndex
  def getValue(self) -> str:
    index = self.getIndex()
    return self.items[index].get('id')
  def show(self):
    clear()
    if self.beforeScreen != None:
      print(self.beforeScreen)
      if self.title != None:
        print(cl.change(''.rjust(len(self.title), '-'), cl.text.GREY))

    showCountHalf = round(self.showCount / 2)
    greaterThanShowCount = len(self.items) >= self.showCount
    items = list(filter(lambda i: i >= self.__currentIndex - showCountHalf and i <= self.__currentIndex + showCountHalf, range(len(self.items))))
    reversedItems = self.items.copy()
    reversedItems.reverse()

    if len(items) < self.showCount and len(self.items) > self.showCount:
      if items[len(items) - 1] >= len(self.items) - 1: 
        for index in range(self.showCount - len(items)):
          items.append(index)
      else:
        for index in range(len(reversedItems) - 1, len(reversedItems) - self.showCount + len(items) - 1, -1):
          items.insert(0, index)

    if self.multiple:
      print(cl.change('(SPACE to select, CTRL+A for All)', cl.text.GREY))
    if self.title != None:
      if self.prefix != None:
        print(cl.change(self.prefix, cl.text.BLUE), end=' ')
      print(self.title)
    if greaterThanShowCount:
      print(cl.change(''.rjust(len(self.title), '-'), cl.text.GREY))

    for index in items:
      item = self.items[index]
      value = item.get('name') or item.get('id')
      prefix = (f'{index + 1}'.rjust(len(str(len(items)))) + '.' if self.ordered else '-') + ' ' if not self.horizontal else ''
      isSelected = index in self.selected
      isCurrentIndex = index == self.__currentIndex
      term = (f'{self.selector} ' if isSelected else '  ') + prefix + value if self.multiple else prefix + value

      end = '\n' if not self.horizontal or (self.horizontal and index == len(items) - 1) else ' | '
      if index == 0 and greaterThanShowCount and not self.horizontal:
        print(cl.change('---', cl.text.GREY))
      if isCurrentIndex:
        print(cl.change(term, cl.text.BLUE), end='')
      else:
        print(term, end='')
      print(end, end='')
    print()