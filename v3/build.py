import subprocess

requirements = subprocess.check_output(['pip', 'freeze'], text=True)

open('requirements.txt', 'w').write(requirements)

subprocess.run(['pyinstaller', '-F', 'myousic.py'])
