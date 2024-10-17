import re

def uppercase(text: str, startIndex: int = 0, span: int = 1):
  chunks = re.sub(r'\W', '-', text).split('-')
  newText: str = '' 
  for chunk in chunks:
    endIndex = min(startIndex + span, len(chunk)) if span > 0 else len(chunk)
    newText += chunk[startIndex : endIndex].upper() + chunk[endIndex:] + ' '
  return newText.removesuffix(' ')