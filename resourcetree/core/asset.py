from .resource import Resource



class Asset(Resource):


    def __init__(
        self,
        name,
        parent=None,
        uid=None,
        data=None
    ):

        super().__init__(
            name,
            parent,
            uid
        )


        self.data = data


        if parent:

            parent.append_child(self)