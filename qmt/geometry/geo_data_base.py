from typing import Any, Dict, List


class GeoData:
    def __init__(self, lunit: str = "nm"):
        """Base Class for geometry data objects

        Parameters
        ----------
        lunit : str
            Length unit for this geometry.
        """
        self.parts: Dict[str, Any] = {}
        self.lunit: str = lunit
        self.build_order: List[str] = []
