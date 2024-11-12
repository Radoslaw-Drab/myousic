from tabulate import tabulate
from utils import Exit
from utils.prompt import clear, List, Input, get_color, ColorType, EditableList, ListItem
from utils.config import Config
from prompt_toolkit import PromptSession, Application

key_names = {
  'temp_folder': 'Temporary folder',
  'output_folder': 'Output folder',
  'artwork_size': 'Artwork size',
  'show_count': 'List show count',
  'excluded_genres': 'Genres to exclude (RegEx)',
  'included_genres': 'Genres to include (RegEx)',
  'replace_genres': 'Replacement in genres (RegEx)',
  'replace_lyrics': 'Replacement in lyrics (RegEx)',
  'lyrics_regex': 'Replacement in lyrics url (RegEx)',
  'genres_regex': 'Replacement in genres url (RegEx)'
}

def init(config: Config):
  clear()
  ps = PromptSession()
  data = config.get_data_json()
  keys = [*data.keys()]
  
  table_options: list[str] = []

  for index in range(len(keys)):
    key = keys[index]
    
    table_options.append(
      [
        index + 1, 
        get_name(key), 
        data[key] if type(data[key]) is not dict else '--- Object ---'
      ]
    )
  table = tabulate(table_options, tablefmt='presto').split('\n')
  
  options = [
    { "id": keys[index], "name": table[index] } 
    for index in range(len(table))
  ]

  try:
    key = List(options, 'Settings', list_prefix=False).get_value()
    
    if key == None:
      return init(config)

    setting(config, key, data[key])
    
    init(config)
  except Exit: 
    return
def get_name(key: str):
  return key if key not in key_names else key_names[key]
def setting(config: Config, key: str, value: any):
  clear()
  name = get_color(get_name(key), ColorType.PRIMARY) + ': ' + str(value)
  try: 
    action = List(
      [
        { "id": "change", "name": "Change" },
        { "id": "reset", "name": "Reset to default" },
        { "id": "exit", "name": "Exit" }
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
        v = config.default_config_type.get('key')
        config.set_data(key, v)
        return v
  except Exit:
    return
  
def input_by_type(config: Config, key: str, value: any, extra_data: dict = {}):
  def default_input(name: str, value: str):
    [v] = Input(
      name, 
      ('New value: ', get_color(value, ColorType.GREY))
    ).start()
    return v if type(value) is str else int(v)
  name = get_color(get_name(key), ColorType.PRIMARY)
  if type(value) is bool:
    clear()
    v = List(["True", "False"], name + ': ' + str(value), horizontal=True).get_value()
    return v == "True"
  if type(value) is int or type(value) is str:
    return default_input(name, value)
  if type(value) is list:
    clear()
      # return [*items, 'test']
    # v = EditableList( 
    #   add_function=add, 
    #   remove_function=remove,
    #   items=value, 
    #   title=name,
    # ).get_list()
    default_index = extra_data.get('default_index') or -1
    default_action_index = extra_data.get('default_action_index') or 0
  
    (index, action, action_index) = List(
    value, 
    name,
    default_index=default_index,
    default_action_index=default_action_index,
    actions=[
      ('add-below', 'Add below'), 
      ('add-above', 'Add above'), 
      ('move-up', 'Move up'), 
      ('move-down', 'Move down'), 
      ('edit', 'Edit'), 
      ('remove', 'Remove')
    ]).get_action()
    extra_data['default_action_index'] = action_index
    # v = List(value, name, custom_bindings={}).get_index()

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
    if action == 'move-up':
      t = [*value[:index - 1], value[index], value[index - 1], *value[index + 1:]]
      print(t)
      input()
      value = t
      extra_data['default_index'] = index - 1
    if action == 'move-down':
      value = [*value[:index], value[index + 1], value[index], *value[index + 2:]]
      extra_data['default_index'] = index + 1
    

    return input_by_type(config, key, value, extra_data)
  return value