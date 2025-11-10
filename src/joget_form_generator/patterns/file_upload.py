"""FileUpload pattern."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin


class FileUploadPattern(BasePattern, ReadOnlyMixin):
    """Pattern for Joget File Upload."""

    template_name: ClassVar[str] = "file_upload.j2"

    def _prepare_context(
        self, field: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Prepare context for FileUpload template."""
        # Convert maxSize from MB to bytes (Joget expects bytes)
        max_size_mb = field.get("maxSize", 10)
        max_size_bytes = max_size_mb * 1024 * 1024

        return {
            "id": field["id"],
            "label": field["label"],
            "maxSize": str(max_size_bytes),
            "fileTypes": field.get("fileTypes", "*"),
            **self.get_readonly_props(field),
        }
