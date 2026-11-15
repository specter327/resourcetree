# resourcetree

**A domain-neutral foundation for resource models and optional hierarchical structure management.**

`resourcetree` defines generic resources and containment relationships without assuming that resources are files, directories, network nodes, URLs, database records, or any other domain-specific entity.

> If a capability starts to express a particular domain, it belongs in a specialization—not in this core library.

## Core model

```text
Resource
├── Asset       # terminal resource
└── Container   # resource that can contain other resources

ResourceTree    # optional manager for one or more resource roots
```

- **Resource** provides stable identity, name, timestamps, metadata and an optional parent relationship.
- **Asset** specializes Resource as a terminal unit. Its optional `data` payload remains domain-defined.
- **Container** owns direct parent/child relationships and supports local traversal and search.
- **ResourceTree** optionally manages membership, roots, a global index, traversal, lookup, search and composition.

A `Container` already forms a hierarchy through its parent/children relationships. A `ResourceTree` is not required to create or use that hierarchy. It is an optional administrative layer for managing one or more independent roots as a forest.

The core does not perform filesystem or network I/O, inspect operating-system permissions, monitor external resources, or interpret domain-specific metadata.

## Installation

```bash
pip install resourcetree
```

## Quick start: resources without ResourceTree

```python
from resourcetree import Asset, Container

root = Container("workspace")
documents = Container("documents", parent=root)
report = Asset("report", parent=documents, data={"kind": "document"})

for resource in root.walk():
    print(resource.name, resource.uid)
```

Resources and containers are fully usable without creating a `ResourceTree`.

## Optional global management

```python
from resourcetree import Asset, Container, ResourceTree

first_volume = Container("volume-a")
report = Asset("report.txt", parent=first_volume)
second_volume = Container("volume-b")

tree = ResourceTree(roots=[first_volume, second_volume])

assert tree.get(report.uid) is report
for resource in tree.walk():
    print(resource.name)
```

A tree may have zero, one or multiple roots. A root can be any `Resource`, including an `Asset`. The `root=` constructor argument remains available for a single root; `tree.root` returns that root only when exactly one exists. Use `tree.roots` for the general case.

A tree can also be initialized empty and populated later:

```python
tree = ResourceTree(name="workspace")
tree.add_root(Container("projects"))
tree.add_root(Asset("readme"))
```

## Membership and mutation

A resource can belong to at most one `ResourceTree`. When a container belongs to a tree, direct calls to `append_child()` and `remove_child()` coordinate membership and keep the global index synchronized.

```python
root = Container("root")
tree = ResourceTree(root=root)

branch = Container("branch")
root.append_child(branch)  # branch is registered automatically
```

The `uid`, `parent`, `children` and `roots` views are read-only. Structural changes must use the supported container or tree operations so invariants cannot be bypassed.

Removing a subtree from a managed container releases tree membership for every node while preserving relationships inside the detached subtree. Removing a root does the same for its complete hierarchy.

## Composition

Mounting transfers every source root beneath a destination container. The source tree becomes empty. Validation is completed before either tree is mutated.

```python
destination = ResourceTree(root=Container("workspace"))
source = ResourceTree(roots=[
    Container("shared"),
    Asset("shared-index"),
])

destination.mount(destination.root, source)
```

## Serialization

Every built-in model class exposes `to_dict()` and `from_dict()`. The dictionary representation is the neutral serialization contract; JSON and XML are supported representations of that same data.

```python
from resourcetree import Asset, Container, ResourceTree

root = Container("workspace")
Asset("report", parent=root, data={"pages": 12})
tree = ResourceTree(roots=[root])

# Dictionary representation
data = tree.to_dict()
restored_tree = ResourceTree.from_dict(data)

# JSON
json_data = tree.to_json()
restored_from_json = ResourceTree.from_json(json_data)

# XML
xml_data = tree.to_xml()
restored_from_xml = ResourceTree.from_xml(xml_data)
```

The representation preserves resource identifiers, names, timestamps, metadata, asset payloads, tree identity and root/child structure. Parent relationships are reconstructed from container children; the derived `ResourceTree` index and membership are rebuilt when a tree is restored.

JSON and XML support values represented by the model's data: dictionaries with string keys, lists, strings, integers, floats, booleans and null. Arbitrary Python objects are domain-specific and must be converted by a specialization before using these formats.

A specialization may reuse these methods, extend or override them, or provide an entirely different serialization implementation. The core does not prescribe storage destinations or require specializations to use JSON or XML.

## Specializations

The generic classes are intended to be inherited and extended:

```python
from resourcetree import Asset, Container, ResourceTree

class File(Asset):
    pass

class Directory(Container):
    pass

class FSResourceTree(ResourceTree):
    pass
```

A specialization may use its resource classes directly or provide a specialized `ResourceTree` when global management is useful.

Examples include:

- `fsresource-tree`: filesystems and multiple volume roots.
- `netresource-tree`: network resources and separately modeled connectivity.
- `webresource-tree`: web resources without confusing containment with HTTP routing.
- `noderesource-tree`: network-node hierarchies.

Each specialization owns its own I/O, discovery, monitoring, platform compatibility, operations and domain-specific metadata.

## Design boundary

| Concern | Location |
|---|---|
| Identity, name, timestamps and generic metadata | `Resource` |
| Direct parent/child relationships | `Container` |
| Local traversal and subtree search | `Container` |
| Optional roots, membership and global index | `ResourceTree` |
| Global traversal, lookup, search and composition | `ResourceTree` |
| Terminal resource payload | `Asset` |
| Dictionary, JSON and XML representations of built-in model state | Core serialization |
| Filesystem paths, permissions and disk operations | Filesystem specialization |
| Remote connectivity and network operations | Network specialization |
| HTTP endpoints and server-backed resources | Web specialization |

## Requirements

- Python 3.11+
- `uuid6` for UUIDv7 identifiers

## License

See the repository license.
