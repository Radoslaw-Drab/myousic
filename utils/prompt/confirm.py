from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML

from utils.prompt.color import Color
from utils.system import clear
from utils import Exit

class Confirm:
  def __init__(self, title: str = f'Press {Color.get_color("Enter", Color.SECONDARY)} to continue.'):
    self.__title = title
    
    self.__ps = PromptSession()
    
  def start(self, clear_screen: bool = True, padding_left: int = 2):
    if clear_screen:
      clear()
    try:
        self.__ps.prompt(HTML(''.ljust(padding_left) + self.__title))
    except KeyboardInterrupt:
      raise Exit 