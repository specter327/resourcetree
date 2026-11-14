# Architecture and extension boundary

## Purpose

`resourcetree` is the shared, domain-neutral model for hierarchical resources. Its design rule is:

> If a capability starts to express a specific domain, it belongs in a specialization.

The core must not depend on operating systems, filesystems, network protocols, servers, databases or external resource providers.

## Core inheritance model

```text
Resource
├── Asset
└── Container

ResourceTree
```

- `Resource`: stable identity, name, parent reference, timestamps and generic metadata.
- `Asset(Resource)`: terminal resource with an optional domain-defined payload.
- `Container(Resource)`: resource that can contain other resources.
- `ResourceTree`: root container, resource index, registration, traversal, search and tree composition.

## Method placement

| Capability | Owner | Reason |
|---|---|---|
| `touch()`, logical `path()` | Resource | Intrinsic to the generic node model |
| `append_child()`, `remove_child()`, direct `find()` | Container | Mutates or queries direct containment |
| `walk()`, subtree `search(regex)` | Container | Operates on a generic contained hierarchy |
| `register()`, `remove()`, `get()`, `contains()` | ResourceTree | Maintains tree membership and index |
| root traversal, global `search()`, `mount()` | ResourceTree | Operates on the whole logical tree |
| filesystem I/O, network I/O, external monitoring | Specialization | Requires domain-specific behavior |

## Operations versus object methods

An operation belongs on an object when it is intrinsic to that object's generic state or relationship. An operation belongs in an independent service/module when it coordinates multiple resources, performs I/O, depends on an external provider, or supports multiple execution strategies.

A specialization may expose convenient instance methods, but those methods should delegate to operation modules rather than contain all implementation logic. This keeps behavior testable and reusable for individual resources and collections.

## Serialization and rendering

Serialization formats and visual representations are not part of the core resource identity model. They should live in independent serializer and renderer modules. Object-level methods such as `to_dict()` or `to_mermaid()` may be added as thin convenience wrappers when the API is stable.

## Extension examples

- `fsresource-tree`: File(Asset), Directory(Container), FSResourceTree(ResourceTree).
- `netresource-tree`: remote resources and network transport.
- `webresource-tree`: server-backed resources and HTTP behavior.
- `noderesource-tree`: network nodes and topology.

Specializations may extend metadata, override behavior and introduce services, while preserving the core contracts.
