from typing import Any, Dict, List, Optional
from qmt.infrastructure import WithParts


class GeoData(WithParts):
    def __init__(self, lunit: Optional[str] = None):
        """Base class for geometry data objects.
        
        Parameters
        ----------
        lunit : str, optional
            Length unit for this geometry, by default "nm"
        """
        self.lunit: Optional[str] = lunit
        self.build_order: List[str] = []
        super().__init__()
