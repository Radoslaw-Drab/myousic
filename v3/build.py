import subprocess
import argparse
import sys


def get_args():
  parser = argparse.ArgumentParser('build.py')
  parser.add_argument('--build', '-b', help='Build script for your system', action='store_true')
  parser.add_argument('--install', '-i', help='Install dependencies for script', action='store', metavar='ENV_NAME', type=str, default='dev')
  return parser.parse_args()

def main():
  args = get_args()

  if args.build:
    requirements = subprocess.check_output(['pip', 'freeze'], text=True)
    open('requirements.txt', 'w').write(requirements)
    subprocess.run(['pyinstaller', '-F', 'myousic.py'])
  if args.install:
    subprocess.run([sys.executable,  '-m venv', args.install], shell=True)
    subprocess.run(['sudo', 'dev/bin/activate'], shell=True)
    subprocess.run(['pip',  'install',  '-r', 'requirements.txt'], shell=True)

if __name__ == "__main__":
  main()