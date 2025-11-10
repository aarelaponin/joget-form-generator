"""Pattern registry for field type to pattern class mapping."""

from typing import Type, Dict
from .base import BasePattern


class PatternRegistry:
    """Registry of field patterns."""

    _patterns: Dict[str, Type[BasePattern]] = {}

    @classmethod
    def register(cls, field_type: str, pattern_class: Type[BasePattern]) -> None:
        """
        Register a pattern class for a field type.

        Args:
            field_type: Field type string (e.g., "textField")
            pattern_class: Pattern class to register
        """
        cls._patterns[field_type] = pattern_class

    @classmethod
    def get(cls, field_type: str) -> Type[BasePattern]:
        """
        Get pattern class for field type.

        Args:
            field_type: Field type string

        Returns:
            Pattern class

        Raises:
            ValueError: If no pattern registered for field type
        """
        if field_type not in cls._patterns:
            raise ValueError(
                f"No pattern registered for field type: '{field_type}'. "
                f"Available types: {', '.join(sorted(cls._patterns.keys()))}"
            )
        return cls._patterns[field_type]

    @classmethod
    def is_registered(cls, field_type: str) -> bool:
        """Check if field type has registered pattern."""
        return field_type in cls._patterns

    @classmethod
    def list_types(cls) -> list[str]:
        """Get list of all registered field types."""
        return sorted(cls._patterns.keys())
