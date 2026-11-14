# resourcetree

**A domain-neutral foundation for hierarchical resource models.**

`resourcetree` defines the common structure shared by specialized resource-tree libraries. It models resources and their relationships without assuming that those resources are files, directories, network nodes, URLs, database records, or any other domain-specific entity.

> If a capability starts to express a particular domain, it belongs in a specialization—not in this core library.

## Core model

```text
Resource
├── Asset       # terminal resource
└── Container   # resource that can contain other resources

ResourceTree    # root, hierarchy and resource index
```

- **Resource** provides identity, name, timestamps, metadata and a logical hierarchy path.
- **Asset** specializes Resource as a terminal unit. Its optional `data` payload remains domain-defined.
- **Container** specializes Resource as a container and maintains parent/child relationships.
- **ResourceTree** owns a root container and indexes the resources reachable from it. It supports registration, traversal, lookup, search and composition.

The core does not perform filesystem or network I/O, inspect operating-system permissions, monitor external resources, or interpret domain-specific metadata.

## Installation

```bash
pip install resourcetree
```

## Quick start

```python
from resourcetree import Asset, Container, ResourceTree

root = Container("root")
documents = Container("documents", parent=root)
report = Asset("report", parent=documents, data={"kind": "document"})

tree = ResourceTree(root=root)

for resource in tree.walk():
    print(resource.name, resource.uid)

matches = tree.search(r"report$")
print(matches)
```

A root can also be created from a name:

```python
tree = ResourceTree(root="workspace")
tree.register(Container("projects"), parent=tree.root)
```

## Composition

Mounting transfers the source tree's root subtree into a container in the destination tree. The source tree becomes empty.

```python
left = ResourceTree(root="workspace")
right = ResourceTree(root="shared")

left.mount(entrypoint=left.root, tree=right)
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

Examples of possible specializations include:

- `fsresource-tree`: real local filesystems.
- `netresource-tree`: resources hosted by remote systems.
- `webresource-tree`: resources exposed through a server and port.
- `noderesource-tree`: network-node hierarchies.

Each specialization owns its own I/O, discovery, monitoring, platform compatibility, operations and domain-specific metadata.

## Design boundary

| Concern | Location |
|---|---|
| Identity, name, timestamps and generic metadata | `Resource` |
| Parent/child relationships | `Container` and `ResourceTree` |
| Terminal resource payload | `Asset` |
| Root, indexing, traversal, lookup and composition | `ResourceTree` |
| Filesystem paths, file size, permissions and disk operations | Filesystem specialization |
| Remote connections and network operations | Network specialization |
| HTTP endpoints and server-backed resources | Web specialization |

## Requirements

- Python 3.11+
- `uuid6` for UUIDv7 identifiers

## License

See the repository license.
