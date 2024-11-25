from typing import Literal
from prompt_toolkit import PromptSession
from tabulate import tabulate

from utils import Exit
from utils.prompt import clear, List, Input, Color, default_input
from utils.config import Config
from utils.classes import Obj

key_names = {
  'temp_folder': 'Temporary folder',
  'output_folder': 'Output folder',
  'artwork_size': 'Artwork size',
  'show_count': 'List show count',
  'excluded_genres': 'Genres to exclude (RegEx)',
  'included_genres': 'Genres to include (RegEx)',
  'genres_modifiers': 'Modifier in genres (RegEx)',
  'lyrics_modifiers': 'Modifier in lyrics (RegEx)',
  'lyrics_url_modifiers': 'Modifier in lyrics url (RegEx)',
  'genres_url_modifiers': 'Modifier in genres url (RegEx)'
}

def init(config: Config):
  clear()
  ps = PromptSession()
  data = config.get_data()
  
  table_options: list[dict[str, any]] = []

  for key in Obj.get_attributes(data):
    value = getattr(data, key)

    name = get_name(key)
    option = { "key": key, "list": [] }
    if type(value) is list:
      option['list'] = [name, value[:3]]
    elif type(value) is dict:
      option['list'] = [name, '{ ... }']
    else:
      option['list'] = ([name, value])
    table_options.append(option)

  table = tabulate([opt.get('list') for opt in table_options], tablefmt='presto', showindex=True).split('\n')
  
  options = [
    (table_options[index].get('key'), table[index])
    for index in range(len(table))
  ]

  try:
    key = List(options, 'Settings', list_prefix=False).get_value()
    
    if key == None:
      return init(config)
    
    setting(config, key, getattr(data, key))
    
    init(config)
  except Exit: 
    return
def get_name(key: str):
  return key if key not in key_names else key_names[key]
def setting(config: Config, key: str, value: any):
  clear()
  name =Color.get_color(get_name(key), Color.PRIMARY) + ': ' + str(value)
  try: 
    action = List[Literal['change', 'reset', 'exit']](
      [
        ("change", "Change"),
        ("reset", "Reset to default"),
        ("exit", "Exit")
      ], 
      name, horizontal=True).get_value()
    
    match action:
      case 'change':
        try:
          v = input_by_type(config, key, value)
          config.set_data(key, v)
          return v
        except Exit:
          return setting(config, key, value)
      case 'reset':
        v = getattr(config.AppConfig(), key)
        config.set_data(key, v)
        return v
  except Exit:
    return
  
def input_by_type(config: Config, key: str, value: any, extra_data: dict = {}):
  name = Color.get_color(get_name(key), Color.PRIMARY)
  if type(value) is bool:
    clear()
    v = List([True, False], name + ': ' + str(value), horizontal=True).get_value()
    return v == True
  if type(value) is int or type(value) is str:
    return default_input(name, value)
  if type(value) is list:
    clear()
    default_index: int = extra_data.get('default_index') if extra_data.get('default_index') != None else -1
    default_action_index: int = extra_data.get('default_action_index') if extra_data.get('default_action_index') != None else 0
  
    (index, action, action_index) = List(
    value, 
    name,
    default_index=default_index,
    default_action_index=default_action_index,
    actions=[
      ('add-below', 'Add below', True), 
      ('add-above', 'Add above', True), 
      ('move-up', 'Move up', len(value) > 0), 
      ('move-down', 'Move down', len(value) > 0), 
      ('edit', 'Edit', len(value) > 0), 
      ('remove', 'Remove', len(value) > 0),
      ('save', 'Save', True)
    ]).get_action()
    extra_data['default_action_index'] = action_index
    if action == 'add-below':
      value.insert(index + 1, default_input(name, ''))
      extra_data['default_index'] = -1
    if action == 'add-above':
      value.insert(index, default_input(name, ''))
      extra_data['default_index'] = -2
    if action == 'edit':
      value[index] = default_input(name, value[index])
      extra_data['default_index'] = index
    if action == 'remove':
      value = [*value[:index], *value[index + 1:]]
    if action == 'move-up' and index - 1 >= 0:
      value = [*value[:index - 1], value[index], value[index - 1], *value[index + 1:]]
      extra_data['default_index'] = max(index - 1, 0)
    if action == 'move-down' and index + 1 < len(value):
      value = [*value[:index], value[index + 1], value[index], *value[index + 2:]]
      extra_data['default_index'] = index + 1
    if action == 'save':
      return value

    return input_by_type(config, key, value, extra_data)
  if type(value) is dict:
    print('Not implemented')
    input()
  return value