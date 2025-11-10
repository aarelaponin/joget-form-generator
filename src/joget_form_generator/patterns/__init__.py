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
]
