from utils.prompt.color import Color
from utils.prompt.input import Input
from utils.prompt.confirm import Confirm
from utils.prompt.list import List, ListItem

def clear():
  from os import system, name
  system('cls' if name=='nt' else 'clear')
