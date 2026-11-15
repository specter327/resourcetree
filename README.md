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

A tree may have zero, one or multiple roots. A root can be any `Resource`, including an `Asset`. Use `roots` as the single interface for zero, one or multiple roots.

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
tree = ResourceTree(roots=[root])

branch = Container("branch")
root.append_child(branch)  # branch is registered automatically
```

The `uid`, `parent`, `children` and `roots` views are read-only. Structural changes must use the supported container or tree operations so invariants cannot be bypassed.

Removing a subtree from a managed container releases tree membership for every node while preserving relationships inside the detached subtree. Removing a root does the same for its complete hierarchy.

## Composition

Mounting transfers every source root beneath a destination container. The source tree becomes empty. Validation is completed before either tree is mutated.

```python
destination = ResourceTree(roots=[Container("workspace")])
source = ResourceTree(roots=[
    Container("shared"),
    Asset("shared-index"),
])

destination.mount(destination.roots[0], source)
```

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
| Filesystem paths, permissions and disk operations | Filesystem specialization |
| Remote connectivity and network operations | Network specialization |
| HTTP endpoints and server-backed resources | Web specialization |

## Requirements

- Python 3.11+
- `uuid6` for UUIDv7 identifiers

## License

See the repository license.

## Serialization

Every core model class exposes `to_dict()` and `from_dict()`. The dictionary representation is the format-neutral description of the object's serializable state.

The same model can be serialized as JSON or XML and reconstructed:

```python
from resourcetree import Asset, Container, ResourceTree

root = Container("workspace")
Asset("report", parent=root, data={"pages": 12})

as_dict = root.to_dict()
restored_from_dict = Container.from_dict(as_dict)

json_text = root.to_json()
restored_from_json = Container.from_json(json_text)

tree = ResourceTree(roots=[root], name="documents")
xml_text = tree.to_xml()
restored_tree = ResourceTree.from_xml(xml_text)
```

The serialized hierarchy stores child relationships once; parent links are rebuilt during reconstruction. `ResourceTree` serializes its own identity, name and roots without inheriting from `Resource`.

JSON and XML support ordinary scalar values, lists and string-keyed dictionaries. An `Asset.data` payload must be representable by the selected format. Domain specializations may reuse, extend, override or omit this serialization API.
