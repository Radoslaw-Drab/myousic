import re
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from utils.prompt.xml import xml_format

class ColorType():
  PRIMARY = '#ff5500'
  SECONDARY = '#0055ff'
  GREY = '#555555'
  ERROR = '#ff0000'
  WARNING = '#ffff00'
  SUCCESS = '#00ff00'


def remove_color(text: str):
  match = re.search(r'(?<=\>).*(?=<\/style>)', text)
  inside_styles = re.sub(r'<\/.*>', '', match.group()) if match else None
  return inside_styles if inside_styles else text

def get_color(text: str, type: ColorType | str, modify_type: str = 'fg'):
  return '\n'.join([f'<style {modify_type}="{type}">{t}</style>' for t in text.split('\n')])

def print_formatted(text: str, sep: str = ' ', end: str = '\n', padding_left: int = 2):
  splitted_text = [''.ljust(padding_left) + line for line in text.split('\n')]
  try:
    print_formatted_text(HTML(xml_format('\n'.join(splitted_text))), sep=sep, end=end)
  except:
    print('\n'.join(splitted_text), sep=sep, end=end)

def print_color(text: str, type: ColorType, modify_type: str = 'fg', sep: str = ' ', end: str = '\n'):
  print_formatted(get_color(text, type, modify_type), sep=sep, end=end)

class Color(ColorType):
  get_color = get_color
  print_color = print_color
  print_formatted = print_formatted
  print_formatted_text = print_formatted_text
  remove_color = remove_color