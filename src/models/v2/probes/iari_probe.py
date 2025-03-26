from src.models.v2.base import IariBaseModel
from abc import ABC, abstractmethod


class IariProbe(IariBaseModel, ABC):
    # iari_version: str = ""
    # iari_version: str = get_poetry_version("pyproject.toml")

    # * * *
    # this should be implemented in calling object
    # * * *

    @property
    @abstractmethod
    def probe_name(self):
        """Abstract class property that must be implemented by subclasses"""
        pass

    @staticmethod
    @abstractmethod
    def probe(url):
        pass

