from datetime import datetime, timezone

import pytest

import resourcetree as rt


def make_hierarchy():
    root = rt.Container("root", uid="root-id", metadata={"kind": "workspace"})
    branch = rt.Container("branch", parent=root, uid="branch-id")
    asset = rt.Asset(
        "report",
        parent=branch,
        uid="asset-id",
        data={"bytes": [1, 2, 3], "active": True, "note": None},
        metadata={"source": "test"},
    )
    root.created_at = datetime(2024, 1, 2, tzinfo=timezone.utc)
    root.updated_at = datetime(2024, 2, 3, tzinfo=timezone.utc)
    return root, branch, asset


def assert_hierarchy_equal(actual):
    assert isinstance(actual, rt.Container)
    assert actual.uid == "root-id"
    assert actual.metadata == {"kind": "workspace"}
    assert actual.created_at == datetime(2024, 1, 2, tzinfo=timezone.utc)
    assert actual.updated_at == datetime(2024, 2, 3, tzinfo=timezone.utc)
    branch = actual.children[0]
    assert isinstance(branch, rt.Container)
    assert branch.parent is actual
    asset = branch.children[0]
    assert isinstance(asset, rt.Asset)
    assert asset.parent is branch
    assert asset.data == {"bytes": [1, 2, 3], "active": True, "note": None}
    assert asset.metadata == {"source": "test"}


def test_container_to_dict_from_dict_round_trip():
    root, _, _ = make_hierarchy()
    assert_hierarchy_equal(rt.Container.from_dict(root.to_dict()))


def test_resource_to_dict_from_dict_round_trip():
    resource = rt.Resource("standalone", uid="resource-id", metadata={"x": 1})
    restored = rt.Resource.from_dict(resource.to_dict())
    assert type(restored) is rt.Resource
    assert restored.to_dict() == resource.to_dict()


def test_asset_to_dict_from_dict_round_trip():
    asset = rt.Asset("asset", uid="asset-id", data={"values": [1, 2]})
    restored = rt.Asset.from_dict(asset.to_dict())
    assert type(restored) is rt.Asset
    assert restored.to_dict() == asset.to_dict()


@pytest.mark.parametrize("format_name", ["json", "xml"])
def test_container_text_round_trip(format_name):
    root, _, _ = make_hierarchy()
    restored = getattr(type(root), f"from_{format_name}")(
        getattr(root, f"to_{format_name}")()
    )
    assert_hierarchy_equal(restored)


@pytest.mark.parametrize("format_name", ["json", "xml"])
def test_tree_text_round_trip(format_name):
    root, _, asset = make_hierarchy()
    second_root = rt.Asset("independent", uid="second-root", data=17)
    tree = rt.ResourceTree(roots=[root, second_root], name="collection", uid="tree-id")
    restored = getattr(type(tree), f"from_{format_name}")(
        getattr(tree, f"to_{format_name}")()
    )
    assert restored.uid == tree.uid
    assert restored.name == tree.name
    assert len(restored) == 4
    assert restored.roots[0].children[0].children[0].uid == asset.uid
    assert restored.roots[0].children[0].children[0].tree is restored


def test_asset_json_rejects_non_json_payload():
    asset = rt.Asset("asset", data=object())
    with pytest.raises(TypeError):
        asset.to_json()


def test_xml_round_trip_preserves_scalar_types():
    asset = rt.Asset("asset", data={"none": None, "bool": False, "int": 4, "float": 2.5})
    restored = rt.Asset.from_xml(asset.to_xml())
    assert restored.data == asset.data
