import pytest

import resourcetree as rt


def test_generic_tree_and_relationships():
    root = rt.Container("root")
    home = rt.Container("home", parent=root)
    asset = rt.Asset("notes", parent=home, data="hello")
    tree = rt.ResourceTree(root=root)

    assert tree.root is root
    assert tree.get(asset.uid) is asset
    assert list(tree.walk()) == [root, home, asset]
    assert tree.search(r"note") == [asset]
    assert asset.parent is home


def test_tree_can_create_root_from_name_and_register_children():
    tree = rt.ResourceTree(root="workspace")
    projects = rt.Container("projects")
    tree.register(projects, parent=tree.root)

    assert tree.root.name == "workspace"
    assert tree.contains(projects)
    assert projects.parent is tree.root


def test_mount_transfers_source_tree():
    destination = rt.ResourceTree(root="destination")
    source = rt.ResourceTree(root="source")
    child = rt.Asset("item", parent=source.root)

    mounted = destination.mount(destination.root, source)

    assert mounted is source.root or mounted.name == "source"
    assert destination.contains(child)
    assert source.root is None
    assert len(source) == 0


def test_container_rejects_cycles():
    root = rt.Container("root")
    child = rt.Container("child", parent=root)

    with pytest.raises(ValueError):
        child.append_child(root)


def test_remove_subtree_updates_index():
    root = rt.Container("root")
    branch = rt.Container("branch", parent=root)
    leaf = rt.Asset("leaf", parent=branch)
    tree = rt.ResourceTree(root=root)

    assert tree.remove(branch)
    assert not tree.contains(branch)
    assert not tree.contains(leaf)
    assert leaf.parent is None
