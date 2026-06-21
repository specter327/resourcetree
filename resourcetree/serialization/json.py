import json



def encode(resource):

    data = {

        "type":
            resource.__class__.__name__,

        "uid":
            resource.uid,

        "name":
            resource.name,

        "metadata":
            resource.metadata

    }


    if hasattr(resource,"children"):

        data["children"] = [
            encode(x)
            for x in resource.children
        ]


    return data




def dumps(resource):

    return json.dumps(
        encode(resource),
        indent=4
    )