
def uid(
    resource,
    target_uid
):

    if resource.uid == target_uid:
        return resource



    if hasattr(resource,"children"):

        for child in resource.children:

            result = uid(
                child,
                target_uid
            )


            if result:
                return result



    return None



def name(
    resource,
    target
):

    if resource.name == target:
        return resource


    if hasattr(resource,"children"):

        for child in resource.children:

            result = name(
                child,
                target
            )

            if result:
                return result


    return None