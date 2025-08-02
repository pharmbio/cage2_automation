from abc import ABC, abstractmethod
from typing import Tuple, List, NamedTuple


class Site(NamedTuple):
    device: str
    position_index: int

#Site = Tuple[str, int]


class LabwareSite(ABC):
    @abstractmethod
    def PrepareForInput(self, HandoverPosition: Site, InternalPosition: int, LabwareType: str, LabwareUniqueID: str):
        """"""

    @abstractmethod
    def PrepareForOutput(self, HandoverPosition: Site, InternalPosition: int):
        """"""

    @abstractmethod
    def LabwareDelivered(self, HandoverPosition: Site):
        """"""

    @abstractmethod
    def LabwareRemoved(self, HandoverPosition: Site):
        """"""

    @classmethod
    def __instancecheck__(cls, instance):
        return all(hasattr(instance, attr) and callable(instance.attr) for attr in [
            "PrepareForInput", "PrepareForOutput", "LabwareDelivered", "LabwareRemoved",
                   ])

    @classmethod
    def __subclasshook__(cls, __subclass):
        print(f"Custom subclass check of {__subclass} for {__subclass} of LabwareSite")
        return all(hasattr(__subclass, attr) and callable(__subclass.attr) for attr in [
            "PrepareForInput", "PrepareForOutput", "LabwareDelivered", "LabwareRemoved",
                   ])


class LabwareManipulator(ABC):
    @abstractmethod
    def PrepareForInput(self, HandoverPosition: Site, InternalPosition: int, LabwareType: str, LabwareUniqueID: str):
        """"""

    @abstractmethod
    def PrepareForOutput(self, HandoverPosition: Site, InternalPosition: int):
        """"""

    @abstractmethod
    def GetLabware(self, HandoverPosition: Site, IntermediateActions: list[str]):
        """"""

    @abstractmethod
    def PutLabware(self, HandoverPosition: Site, IntermediateActions: list[str]):
        """"""

    @classmethod
    def __instancecheck__(cls, instance):
        return all(hasattr(instance, attr) and callable(instance.attr) for attr in [
            "PrepareForInput", "PrepareForOutput", "LabwareDelivered", "LabwareRemoved",
                   ])

    @classmethod
    def __subclasshook__(cls, __subclass):
        print(f"Custom subclass check of {__subclass} for {__subclass} of LabwareSite")
        return all(hasattr(__subclass, attr) and callable(__subclass.attr) for attr in [
            "PrepareForInput", "PrepareForOutput", "LabwareDelivered", "LabwareRemoved",
                   ])


class BoolListProperty:
    """
    Just for convenience.
    """
    def get(self) -> List[bool]:
        return []

class LabwareSiteExt(LabwareSite):
    @property
    @abstractmethod
    def InputIsPossible(self) -> BoolListProperty:
        """"""

    @property
    @abstractmethod
    def OutputIsPossible(self) -> BoolListProperty:
        """"""

    @classmethod
    def __subclasshook__(cls, __subclass):
        print(f"Custom subclass check of {__subclass} for {__subclass} of LabwareSiteExt")
        if not issubclass(__subclass, LabwareSite):
            return False
        return all(hasattr(__subclass, attr) for attr in ["InputIsPossible", "OutputIsPossible"])

    @classmethod
    def __instancecheck__(cls, instance):
        print(f"Custom instance check for {instance}")
        print(dir(instance))
        if not isinstance(LabwareSite, instance):
            return False
        return all(hasattr(instance, attr) for attr in ["InputIsPossible", "OutputIsPossible"])
