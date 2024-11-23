import re

xml_replacements: dict[str, str] = {
  "&": "&amp;"
}
def xml_format(text: str):
  new_text = text
  for key in xml_replacements.keys():
    new_text = re.sub(key, xml_replacements[key], new_text)
  return new_text