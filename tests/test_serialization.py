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


@pytest.mark.parametrize("format_name", ["json", "xml"])
def test_formats_reject_values_outside_the_shared_data_model(format_name):
    asset = Asset("unsupported", data={1, 2, 3})

    with pytest.raises(TypeError, match="unsupported"):
        getattr(asset, f"to_{format_name}")()


@pytest.mark.parametrize("format_name", ["json", "xml"])
def test_formats_reject_non_string_dictionary_keys(format_name):
    asset = Asset("unsupported", data={1: "value"})

    with pytest.raises(TypeError, match="keys must be strings"):
        getattr(asset, f"to_{format_name}")()

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



def test_deep_container_dictionary_and_format_output_are_iterative():
    depth = 1200
    root = Container("root", uid="deep-root")
    current = root
    for index in range(depth):
        child = Container(f"directory-{index}", uid=f"directory-{index}")
        current.append_child(child)
        current = child
    current.append_child(Asset("leaf", uid="deep-leaf", data={"ok": True}))

    data = root.to_dict()
    node = data
    for _ in range(depth):
        node = node["children"][0]
    assert node["children"][0]["uid"] == "deep-leaf"

    json_value = root.to_json(indent=None)
    assert '"uid":"deep-leaf"' in json_value

    from resourcetree.serialization.xml import loads as load_xml

    xml_data = load_xml(root.to_xml())
    node = xml_data
    for _ in range(depth):
        node = node["children"][0]
    assert node["children"][0]["uid"] == "deep-leaf"


def test_container_serialization_rejects_repeated_resource_references():
    root = Container("root")
    child = Asset("child")
    root._children.extend([child, child])
    child._parent = root

    with pytest.raises(ValueError, match="cycle or duplicate reference"):
        root.to_dict()


def test_deep_container_dict_and_json_reconstruction_are_iterative():
    depth = 1200
    root = Container("root", uid="deep-reconstruction-root")
    current = root
    for index in range(depth):
        child = Container(f"directory-{index}", uid=f"rebuild-{index}")
        current.append_child(child)
        current = child
    current.append_child(Asset("leaf", uid="rebuild-leaf", data={"ok": True}))

    restored = Container.from_dict(root.to_dict())
    node = restored
    for _ in range(depth):
        assert len(node.children) == 1
        node = node.children[0]
    assert node.children[0].uid == "rebuild-leaf"

    serialized = root.to_json(indent=None)
    restored_json = Container.from_json(serialized)
    node = restored_json
    for _ in range(depth):
        node = node.children[0]
    assert node.children[0].uid == "rebuild-leaf"

    tree = ResourceTree(roots=[root])
    restored_tree = ResourceTree.from_json(tree.to_json(indent=None))
    node = restored_tree.roots[0]
    for _ in range(depth):
        node = node.children[0]
    assert node.children[0].uid == "rebuild-leaf"
    assert len(restored_tree) == depth + 2


@pytest.mark.parametrize(
    "value",
    [
        '{"type": "resource_tree",}',
        '{"type": "resource_tree", "roots": [1,]}',
        '{"type": "resource_tree"} trailing',
        '{"type": NaN}',
        '{"type": "resource_tree"',
    ],
)
def test_json_loader_rejects_malformed_documents(value):
    from resourcetree.serialization.json import loads

    with pytest.raises((ValueError, TypeError)):
        loads(value)


def test_json_loader_parses_deeply_nested_arrays_iteratively():
    from resourcetree.serialization.json import loads

    depth = 1500
    value = '{"nested":' + "[" * depth + "0" + "]" * depth + "}"
    decoded = loads(value)
    current = decoded["nested"]
    for _ in range(depth):
        assert isinstance(current, list)
        current = current[0]
    assert current == 0


def test_iterative_reconstruction_preserves_sibling_order():
    root = Container("root", uid="ordered-root")
    first = Container("first", uid="ordered-first")
    second = Asset("second", uid="ordered-second")
    third = Container("third", uid="ordered-third")
    root.append_child(first)
    root.append_child(second)
    root.append_child(third)

    restored = Container.from_dict(root.to_dict())

    assert [child.uid for child in restored.children] == [
        "ordered-first",
        "ordered-second",
        "ordered-third",
    ]


def test_iterative_reconstruction_rejects_duplicate_uids_and_repeated_payloads():
    root = Container("root", uid="same")
    root.append_child(Asset("child", uid="same"))

    with pytest.raises(ValueError, match="duplicate resource uid"):
        Container.from_dict(root.to_dict())

    payload = Container("payload", uid="payload").to_dict()
    root_payload = Container("root", uid="root").to_dict()
    root_payload["children"] = [payload, payload]

    with pytest.raises(ValueError, match="repeated resource payload"):
        Container.from_dict(root_payload)


def test_resource_path_handles_deep_hierarchies_iteratively():
    depth = 1200
    root = Container("root", uid="path-root")
    current = root
    for index in range(depth):
        child = Container(f"segment-{index}", uid=f"path-{index}")
        current.append_child(child)
        current = child

    path = current.path()
    segments = path.split("/")
    assert segments[1] == "root"
    assert segments[-1] == f"segment-{depth - 1}"
    assert len(segments) == depth + 2
