import pytest

from resourcetree import Asset, Container, ResourceTree
from resourcetree.operations import ancestors, walk


def make_forest():
    first = Container("first")
    branch = Container("branch", parent=first)
    leaf = Asset("leaf", parent=branch)
    sibling = Asset("sibling", parent=first)
    second = Container("second")
    final = Asset("final", parent=second)
    return first, branch, leaf, sibling, second, final


def test_walk_preorder_and_postorder_for_container():
    first, branch, leaf, sibling, _, _ = make_forest()
    assert list(walk(first)) == [first, branch, leaf, sibling]
    assert list(walk(first, order="post")) == [leaf, branch, sibling, first]
    assert list(first.walk(order="post")) == [leaf, branch, sibling, first]


def test_walk_resource_tree_preserves_root_and_sibling_order():
    first, branch, leaf, sibling, second, final = make_forest()
    tree = ResourceTree(roots=[first, second])
    assert list(tree.walk()) == [first, branch, leaf, sibling, second, final]
    assert list(tree.walk(order="post")) == [leaf, branch, sibling, first, final, second]


def test_walk_supports_terminal_resources_and_deep_hierarchies():
    leaf = Asset("leaf")
    assert list(leaf.walk()) == [leaf]
    assert list(leaf.walk(order="post")) == [leaf]
    root = Container("root")
    current = root
    for index in range(1600):
        current = Container(str(index), parent=current)
    assert sum(1 for _ in root.walk()) == 1601
    assert sum(1 for _ in root.walk(order="post")) == 1601


def test_ancestors_walks_upward_or_downward_and_can_include_self():
    root = Container("root")
    nested = Container("nested", parent=root)
    item = Asset("item", parent=nested)
    assert list(ancestors(item)) == [nested, root]
    assert list(ancestors(item, order="down")) == [root, nested]
    assert list(ancestors(item, include_self=True)) == [item, nested, root]
    assert list(item.ancestors()) == [nested, root]
    assert list(nested.ancestors(include_self=True, order="down")) == [root, nested]


def test_ancestors_of_root_are_empty_without_self():
    root = Container("root")
    assert list(ancestors(root)) == []
    assert list(ancestors(root, include_self=True)) == [root]


def test_walk_rejects_invalid_order_and_corrupt_hierarchies():
    root = Container("root")
    child = Asset("child", parent=root)
    with pytest.raises(ValueError, match="order"):
        list(walk(root, order="sideways"))
    root._children.append(child)
    with pytest.raises(ValueError, match="duplicate child"):
        list(walk(root))


def test_ancestors_detects_inconsistent_parent_links_and_cycles():
    root = Container("root")
    child = Asset("child")
    child._parent = root
    with pytest.raises(ValueError, match="inconsistent parent/child"):
        list(ancestors(child))
    loop = Container("loop")
    loop._parent = loop
    loop._children.append(loop)
    with pytest.raises(ValueError, match="cycle"):
        list(ancestors(loop, include_self=True))
