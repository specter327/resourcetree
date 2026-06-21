from ..core.container import Container



def direct(resource):

    yield resource


    if isinstance(resource, Container):

        for child in resource.children:

            yield from direct(child)




def inverse(resource):

    if resource.parent:

        yield from inverse(resource.parent)


    yield resource