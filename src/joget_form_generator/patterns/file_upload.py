"""FileUpload pattern."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin, ValidationMixin


class FileUploadPattern(BasePattern, ReadOnlyMixin, ValidationMixin):
    """Pattern for Joget File Upload."""

    template_name: ClassVar[str] = "file_upload.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Prepare context for FileUpload template."""
        # Joget expects maxSize as a simple number (in MB or configurable unit)
        max_size = field.get("maxSize", "")

        return {
            "id": field["id"],
            "label": field["label"],
            "maxSize": str(max_size) if max_size else "",
            "fileType": field.get("fileTypes", ""),
            "validator": self.build_validator(field),
            **self.get_readonly_props(field),
        }
