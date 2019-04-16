from typing import Any, Dict, List


class GeoData:
    """
    Base Class for geometry data objects
    """

    def __init__(self, lunit: str = "nm"):
        """
        :param parts: Dictionary of parts in this geometry
        :param lunit: Length unit for this geometry
        """
        self.parts: Dict[str, Any] = {}
        self.lunit: str = lunit
        self.build_order: List[str] = []
