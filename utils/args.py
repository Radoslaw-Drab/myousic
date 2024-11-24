import argparse
from pathlib import Path

from utils.classes import Obj

class Args():
  config_path: Path = Path(Path.home(), 'myousic.json')
  
  def __init__(self) -> None:
    parser = argparse.ArgumentParser('myousic', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--config', '-c', help='Use config file from specified location', action='store', dest='config_path', metavar='PATH', type=str, default=self.config_path)

    args = parser.parse_args()

    for arg in args:
      if arg not in Obj.get_attributes(self):
        continue
      setattr(self, arg, args[arg])