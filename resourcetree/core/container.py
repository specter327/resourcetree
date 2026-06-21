from .resource import Resource


class Container(Resource):


    def __init__(
        self,
        name,
        parent=None,
        uid=None
    ):

        super().__init__(
            name,
            parent,
            uid
        )


        self.children = []


        if parent:

            parent.append_child(self)



    def append_child(
        self,
        resource: Resource
    ):


        if resource not in self.children:

            self.children.append(resource)

            resource.parent = self

            self.touch()



    def remove_child(
        self,
        resource
    ):

        self.children.remove(resource)

        resource.parent = None

        self.touch()



    def find(
        self,
        name
    ):

        for child in self.children:

            if child.name == name:
                return child


        return None