from resourcetree import Asset, Container, Resource, ResourceTree


class SpecializedContainer(Container):
    pass


class SpecializedAsset(Asset):
    pass


class SpecializedTree(ResourceTree):
    def _validate_node(self, resource):
        if not isinstance(resource, (SpecializedContainer, SpecializedAsset)):
            raise TypeError("unsupported specialized resource")


def test_specialized_node_validation_covers_entire_subtree_atomically():
    root = SpecializedContainer("root", uid="root")
    invalid = Resource("invalid", uid="invalid")
    root.append_child(invalid)
    tree = SpecializedTree()

    try:
        tree.add_root(root)
    except TypeError as exc:
        assert "unsupported specialized resource" in str(exc)
    else:
        raise AssertionError("invalid descendant was accepted")

    assert tree.roots == ()
    assert len(tree) == 0
    assert root.tree is None
    assert invalid.tree is None


def test_specialized_node_validation_runs_for_registered_subtrees():
    root = SpecializedContainer("root", uid="root")
    tree = SpecializedTree(roots=[root])
    child = SpecializedContainer("child", uid="child")
    asset = SpecializedAsset("asset", uid="asset")
    child.append_child(asset)

    root.append_child(child)

    assert tree.get("child") is child
    assert tree.get("asset") is asset
    assert child.tree is tree
    assert asset.tree is tree
