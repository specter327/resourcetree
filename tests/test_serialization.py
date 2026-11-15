from datetime import datetime, timezone

import pytest

from resourcetree import Asset, Container, Resource, ResourceTree


def make_hierarchy():
    root = Container("workspace", uid="root", metadata={"active": True})
    documents = Container("documents", parent=root, uid="documents")
    Asset(
        "report.json",
        parent=documents,
        uid="report",
        data={"items": [1, "two", None, True], "size": 3.5},
        metadata={"labels": ["important", "draft"]},
    )
    return root


def assert_hierarchy(root):
    assert isinstance(root, Container)
    assert root.uid == "root"
    assert root.metadata == {"active": True}
    assert len(root.children) == 1

    documents = root.children[0]
    assert isinstance(documents, Container)
    assert documents.parent is root
    assert len(documents.children) == 1

    report = documents.children[0]
    assert isinstance(report, Asset)
    assert report.parent is documents
    assert report.uid == "report"
    assert report.data == {"items": [1, "two", None, True], "size": 3.5}
    assert report.metadata == {"labels": ["important", "draft"]}


def test_resource_to_dict_from_dict_preserves_identity_and_timestamps():
    resource = Resource("standalone", uid="resource-1", metadata={"enabled": False})
    resource.created_at = datetime(2024, 1, 2, 3, 4, tzinfo=timezone.utc)
    resource.updated_at = datetime(2024, 2, 3, 4, 5, tzinfo=timezone.utc)

    restored = Resource.from_dict(resource.to_dict())

    assert type(restored) is Resource
    assert restored.uid == resource.uid
    assert restored.name == resource.name
    assert restored.metadata == resource.metadata
    assert restored.created_at == resource.created_at
    assert restored.updated_at == resource.updated_at


def test_asset_to_dict_from_dict_preserves_payload():
    asset = Asset("payload", uid="asset-1", data={"bytes": [0, 1, 255]})
    restored = Asset.from_dict(asset.to_dict())

    assert isinstance(restored, Asset)
    assert restored.uid == asset.uid
    assert restored.data == asset.data


def test_container_dictionary_roundtrip_rebuilds_parent_relationships():
    root = make_hierarchy()

    restored = Container.from_dict(root.to_dict())

    assert_hierarchy(restored)


@pytest.mark.parametrize("format_name", ["json", "xml"])
def test_container_format_roundtrip_rebuilds_subtree(format_name):
    root = make_hierarchy()
    serialized = getattr(root, f"to_{format_name}")()
    restored = getattr(Container, f"from_{format_name}")(serialized)

    assert_hierarchy(restored)


def test_resource_tree_dictionary_roundtrip_rebuilds_roots_and_index():
    first = make_hierarchy()
    second = Asset("standalone-root", uid="second")
    tree = ResourceTree(name="workspace", uid="tree-1", roots=[first, second])

    restored = ResourceTree.from_dict(tree.to_dict())

    assert restored.uid == tree.uid
    assert restored.name == tree.name
    assert len(restored.roots) == 2
    assert restored.roots[0].parent is None
    assert restored.roots[1].parent is None
    assert restored.get("report") is not None
    assert restored.get("report").tree is restored
    assert len(restored) == 4
    assert_hierarchy(restored.roots[0])


@pytest.mark.parametrize("format_name", ["json", "xml"])
def test_resource_tree_format_roundtrip(format_name):
    first = make_hierarchy()
    second = Asset("standalone-root", uid="second")
    tree = ResourceTree(name="workspace", uid="tree-1", roots=[first, second])

    serialized = getattr(tree, f"to_{format_name}")()
    restored = getattr(ResourceTree, f"from_{format_name}")(serialized)

    assert restored.to_dict() == tree.to_dict()
    assert len(restored) == len(tree)
    assert restored.get("report").tree is restored


def test_resource_from_dict_rejects_another_model_type():
    with pytest.raises(ValueError, match="expected resource type"):
        Resource.from_dict(Asset("asset").to_dict())


def test_xml_rejects_values_outside_the_supported_data_model():
    asset = Asset("unsupported", data={1, 2, 3})

    with pytest.raises(TypeError, match="unsupported XML value type"):
        asset.to_xml()

@pytest.mark.parametrize("format_name", ["json", "xml"])
def test_resource_and_asset_format_roundtrips(format_name):
    resource = Resource("resource", uid="resource-format")
    asset = Asset("asset", uid="asset-format", data={"value": [1, 2, 3]})

    restored_resource = getattr(Resource, f"from_{format_name}")(
        getattr(resource, f"to_{format_name}")()
    )
    restored_asset = getattr(Asset, f"from_{format_name}")(
        getattr(asset, f"to_{format_name}")()
    )

    assert restored_resource.to_dict() == resource.to_dict()
    assert restored_asset.to_dict() == asset.to_dict()
