"""Pattern library for Joget field generation."""

from .registry import PatternRegistry
from .hidden_field import HiddenFieldPattern
from .text_field import TextFieldPattern
from .password_field import PasswordFieldPattern
from .text_area import TextAreaPattern
from .select_box import SelectBoxPattern
from .check_box import CheckBoxPattern
from .radio import RadioPattern
from .date_picker import DatePickerPattern
from .file_upload import FileUploadPattern
from .custom_html import CustomHTMLPattern
from .id_generator import IDGeneratorPattern
from .subform import SubformPattern
from .grid import GridPattern
from .calculation_field import CalculationFieldPattern
from .rich_text_editor import RichTextEditorPattern
from .form_grid import FormGridPattern
from .multi_paged_form import MultiPagedFormPattern
from .section import SectionPattern

# Register all Phase 1 patterns
PatternRegistry.register("hiddenField", HiddenFieldPattern)
PatternRegistry.register("textField", TextFieldPattern)
PatternRegistry.register("passwordField", PasswordFieldPattern)
PatternRegistry.register("textArea", TextAreaPattern)
PatternRegistry.register("selectBox", SelectBoxPattern)
PatternRegistry.register("checkBox", CheckBoxPattern)
PatternRegistry.register("radio", RadioPattern)
PatternRegistry.register("datePicker", DatePickerPattern)
PatternRegistry.register("fileUpload", FileUploadPattern)

# Register Phase 2 patterns
PatternRegistry.register("customHTML", CustomHTMLPattern)
PatternRegistry.register("idGenerator", IDGeneratorPattern)
PatternRegistry.register("subform", SubformPattern)
PatternRegistry.register("grid", GridPattern)

# Register Enterprise patterns
PatternRegistry.register("calculationField", CalculationFieldPattern)
PatternRegistry.register("richTextEditor", RichTextEditorPattern)
PatternRegistry.register("formGrid", FormGridPattern)
PatternRegistry.register("multiPagedForm", MultiPagedFormPattern)

# Register structural patterns
PatternRegistry.register("section", SectionPattern)

__all__ = [
    "PatternRegistry",
    "HiddenFieldPattern",
    "TextFieldPattern",
    "PasswordFieldPattern",
    "TextAreaPattern",
    "SelectBoxPattern",
    "CheckBoxPattern",
    "RadioPattern",
    "DatePickerPattern",
    "FileUploadPattern",
    "CustomHTMLPattern",
    "IDGeneratorPattern",
    "SubformPattern",
    "GridPattern",
    "CalculationFieldPattern",
    "RichTextEditorPattern",
    "FormGridPattern",
    "MultiPagedFormPattern",
    "SectionPattern",
]
