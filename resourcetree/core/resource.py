from uuid6 import uuid7
from datetime import datetime


class Resource:

    def __init__(
        self,
        name: str,
        parent=None,
        uid: str | None = None
    ):

        self.uid = uid or str(uuid7())

        self.name = name

        self.parent = parent

        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at

        self.metadata = {}


    def touch(self):
        self.updated_at = datetime.utcnow()


    def path(self):

        if self.parent is None:
            return "/" + self.name

        return (
            self.parent.path()
            + "/"
            + self.name
        )


    def __repr__(self):

        return (
            f"<{self.__class__.__name__} "
            f"{self.path()} "
            f"{self.uid}>"
        )