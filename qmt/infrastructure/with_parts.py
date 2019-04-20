from typing import Any, Callable, Dict, Optional


class WithParts:
    def __init__(self, parts: Optional[Dict[str, Any]] = None):
        """Base class for an object that contains parts
        
        Parameters
        ----------
        parts : Dict[str, Any], optional
            A dictionary of parts to initialize with, by default None
        """
        self.parts = {} if parts is None else parts

    def add_part(
        self,
        part_name: str,
        part: Any,
        overwrite: bool = False,
        call_back: Callable[[Any], None] = lambda x: None,
    ):
        """Add a part to this object.
        
        Parameters
        ----------
        part_name : str
            Name of the part to add
        part : Any
            Part to add
        overwrite : bool, optional
            Whether we allow this to overwrite existing part, by default False
        call_back : Callable[[bool], None], optional
            A callback function. If the part is successfully added, the part is passed
            to the function. Otherwise None is passed. By default lambdax:None
        
        Raises
        ------
        ValueError
            An existing part name was added without overwrite
        """
        if (part_name in self.parts) and (not overwrite):
            call_back(None)
            raise ValueError(f"Attempted to overwrite the part {part_name}.")
        else:
            self.parts[part_name] = part
            call_back(part)

    def remove_part(
        self,
        part_name: str,
        ignore_if_absent: bool = False,
        call_back: Callable[[bool], None] = lambda x: None,
    ):
        """Remove a part from this object.
        
        Parameters
        ----------
        part_name : str
            Name of the part to remove
        ignore_if_absent : bool, optional
            Whether we ignore an attempted removal if the part name is not present, by
            default False
        call_back : Callable[[bool], None], optional
            A callback function. If the part is successfully removed, the part is passed
            to the function. Otherwise None is passed. By default lambdax:None
        
        Raises
        ------
        ValueError
            Attempted to remove a missing part while ignore_if_absent is not True 
        """
        if part_name in self.parts:
            part = self.parts[part_name]
            del self.parts[part_name]
            call_back(part)
        elif not ignore_if_absent:
            call_back(None)
            raise ValueError(
                f"Attempted to remove the part {part_name}, which doesn't exist."
            )
