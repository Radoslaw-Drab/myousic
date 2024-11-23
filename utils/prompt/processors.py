from prompt_toolkit.formatted_text import HTML, to_formatted_text, fragment_list_to_text
from prompt_toolkit.layout.processors import Processor, Transformation, TransformationInput

class FormatText(Processor):
    def apply_transformation(self, ti: TransformationInput):
        try:
          fragments = to_formatted_text(HTML(fragment_list_to_text(ti.fragments)))
          return Transformation(fragments)
        except Exception as error:
          return Transformation(ti.fragments)