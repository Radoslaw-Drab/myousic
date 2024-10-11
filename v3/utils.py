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
selected = 1

def show_menu():
    global selected
    print("\n" * 30)
    print("Choose an option:")
    for i in range(1, 5):
        print("{1} {0}. Do something {0} {2}".format(i, ">" if selected == i else " ", "<" if selected == i else " "))

def up():
    global selected
    if selected == 1:
        return
    selected -= 1
    show_menu()

def down():
    global selected
    if selected == 4:
        return
    selected += 1
    show_menu()

# show_menu()
# keyboard.add_hotkey('up', up)
# keyboard.add_hotkey('down', down)
# keyboard.wait()

class List:
  __currentIndex: int = 0
  __colors = colors.Colors()
  title: str = 'Select:'
  items: list[str]
  ordered: bool
  loop: bool
  multiple: bool
  selected: list[int]

  def __init__(self, title: str, items: list[str], loop: bool = True, ordered: bool = True, multiple: bool = False):
    self.title = title
    self.items = items 
    self.loop = loop
    self.ordered = ordered
    self.multiple = multiple
    pass
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
      
  def start(self):
    self.show()
    
    keyboard.add_hotkey('up', lambda: self.__up())
    keyboard.add_hotkey('down', lambda: self.__down())
    keyboard.wait('enter')
    clear()
    return self.__currentIndex
  def show(self):
    clear()
    print(self.title)
    for index in range(len(self.items)):
      item = self.items[index]
      prefix = f'{index + 1}.' if self.ordered else '-'
      
      term = prefix + ' ' + item
      if index == self.__currentIndex:
        print(self.__colors.change(term, self.__colors.text['BLUE']))
      else:
        print(term)


print(List('Test', ['One', 'Two', 'Three', 'Four']).start())