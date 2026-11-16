import pytest

import resourcetree as rt


def test_resources_and_containers_work_without_resource_tree():
    root = rt.Container("root")
    child = rt.Container("child", parent=root)
    asset = rt.Asset("item", parent=child, data="payload")

    assert list(root.walk()) == [root, child, asset]
    assert child.find("item") is asset
    assert root.search("item") == [asset]
    assert asset.tree is None


def test_resource_tree_accepts_multiple_roots_and_assets():
    first = rt.Container("first")
    nested = rt.Asset("nested", parent=first)
    second = rt.Asset("second")
    tree = rt.ResourceTree(roots=[first, second])

    assert tree.roots == (first, second)
    assert list(tree.walk()) == [first, nested, second]
    assert tree.get(nested.uid) is nested
    assert tree.contains(second)
    assert len(tree) == 3


def test_resource_tree_has_no_singular_root_api():
    tree = rt.ResourceTree(roots=[rt.Container("workspace")])
    assert tree.roots[0].name == "workspace"
    assert not hasattr(tree, "root")
    with pytest.raises(TypeError):
        rt.ResourceTree(root=rt.Container("legacy"))


def test_tree_can_be_empty_and_accept_roots_later():
    tree = rt.ResourceTree()
    asset = rt.Asset("standalone")
    tree.add_root(asset)

    assert tree.roots == (asset,)
    assert list(tree.walk()) == [asset]


def test_container_mutation_keeps_registered_tree_index_synchronized():
    root = rt.Container("root")
    tree = rt.ResourceTree(roots=[root])
    branch = rt.Container("branch")
    root.append_child(branch)
    leaf = rt.Asset("leaf", parent=branch)

    assert tree.contains(branch)
    assert tree.contains(leaf)
    assert tree.get(leaf.uid) is leaf
    assert len(tree) == 3


def test_registered_subtree_can_be_detached_without_losing_internal_links():
    root = rt.Container("root")
    branch = rt.Container("branch", parent=root)
    leaf = rt.Asset("leaf", parent=branch)
    tree = rt.ResourceTree(roots=[root])

    assert root.remove_child(branch)
    assert branch.parent is None
    assert leaf.parent is branch
    assert branch.tree is None
    assert leaf.tree is None
    assert not tree.contains(branch)
    assert not tree.contains(leaf)


def test_remove_root_releases_entire_subtree_but_preserves_hierarchy():
    root = rt.Container("root")
    child = rt.Container("child", parent=root)
    leaf = rt.Asset("leaf", parent=child)
    tree = rt.ResourceTree(roots=[root])

    assert tree.remove_root(root)
    assert tree.roots == ()
    assert len(tree) == 0
    assert all(node.tree is None for node in (root, child, leaf))
    assert child.parent is root
    assert leaf.parent is child


def test_resource_cannot_belong_to_two_trees():
    resource = rt.Asset("resource")
    tree = rt.ResourceTree(roots=[resource])
    other = rt.ResourceTree()

    with pytest.raises(ValueError):
        other.add_root(resource)


def test_registered_resource_cannot_be_moved_outside_its_tree():
    root = rt.Container("root")
    child = rt.Asset("child", parent=root)
    rt.ResourceTree(roots=[root])
    external = rt.Container("external")

    with pytest.raises(ValueError):
        external.append_child(child)


def test_multiple_roots_reject_duplicate_uids_atomically():
    first = rt.Asset("first", uid="same")
    second = rt.Asset("second", uid="same")
    tree = rt.ResourceTree()

    with pytest.raises(ValueError):
        tree.add_roots([first, second])

    assert tree.roots == ()
    assert len(tree) == 0
    assert first.tree is None
    assert second.tree is None


def test_root_must_not_have_a_parent():
    parent = rt.Container("parent")
    child = rt.Asset("child", parent=parent)

    with pytest.raises(ValueError):
        rt.ResourceTree(roots=[child])


def test_uid_and_relationship_views_are_read_only():
    resource = rt.Asset("resource")
    container = rt.Container("container")
    tree = rt.ResourceTree()

    with pytest.raises(AttributeError):
        resource.uid = "changed"
    with pytest.raises(AttributeError):
        resource.parent = container
    with pytest.raises(AttributeError):
        container.children.append(resource)
    with pytest.raises(AttributeError):
        tree.uid = "changed"


def test_container_rejects_cycles():
    root = rt.Container("root")
    child = rt.Container("child", parent=root)

    with pytest.raises(ValueError):
        child.append_child(root)


def test_mount_transfers_all_source_roots_atomically():
    destination_root = rt.Container("destination")
    destination = rt.ResourceTree(roots=[destination_root])
    source_a = rt.Container("source-a")
    source_leaf = rt.Asset("leaf", parent=source_a)
    source_b = rt.Asset("source-b")
    source = rt.ResourceTree(roots=[source_a, source_b])

    mounted = destination.mount(destination_root, source)

    assert mounted == (source_a, source_b)
    assert source.roots == ()
    assert len(source) == 0
    assert source_leaf.tree is destination
    assert source_b.tree is destination
    assert source_a.parent is destination_root
    assert source_b.parent is destination_root
    assert len(destination) == 4


def test_mount_rejects_uid_collision_without_mutating_either_tree():
    destination_root = rt.Container("destination")
    collision = rt.Asset("collision", uid="duplicate")
    destination = rt.ResourceTree(roots=[destination_root, collision])
    source_root = rt.Asset("source", uid="duplicate")
    source = rt.ResourceTree(roots=[source_root])

    with pytest.raises(ValueError):
        destination.mount(destination_root, source)

    assert source.roots == (source_root,)
    assert source_root.parent is None
    assert source_root.tree is source
    assert destination.contains(collision)
    assert len(destination) == 2


def test_contains_requires_resource_identity_not_only_uid():
    resource = rt.Asset("resource", uid="shared")
    impostor = rt.Asset("impostor", uid="shared")
    tree = rt.ResourceTree(roots=[resource])

    assert tree.contains(resource)
    assert not tree.contains(impostor)


def test_walk_and_search_cover_every_root_once():
    first = rt.Container("first")
    second = rt.Container("second")
    tree = rt.ResourceTree(roots=[first, second])

    assert tree.search(".*") == [first, second]
    assert len(list(tree.walk())) == 2
