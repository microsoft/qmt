from typing import Any, Dict, List
from qmt.infrastructure import WithParts


class GeoData(WithParts):
    def __init__(self, lunit: str = "nm"):
        """Base class for geometry data objects.
        
        Parameters
        ----------
        lunit : str, optional
            Length unit for this geometry, by default "nm"
        """
        self.lunit: str = lunit
        self.build_order: List[str] = []
        super().__init__()
