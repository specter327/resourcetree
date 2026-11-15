# Architecture and extension boundary

## Purpose

`resourcetree` is the shared, domain-neutral model for resources and optional hierarchical structure management.

> If a capability starts to express a specific domain, it belongs in a specialization.

The core must not depend on operating systems, filesystems, network protocols, servers, databases or external resource providers.

## Core model

```text
Resource
├── Asset
└── Container

ResourceTree (optional manager)
```

- `Resource`: identity, name, timestamps, generic metadata, parent and optional tree membership.
- `Asset(Resource)`: terminal resource with an optional domain-defined payload.
- `Container(Resource)`: owns direct parent/child relationships and local subtree operations.
- `ResourceTree`: optionally manages one or more independent roots, membership and a derived global index.

## Independence

A `Resource` may exist without a parent and without a `ResourceTree`.

A `Container` may build and manage a complete hierarchy without a `ResourceTree`. Its parent/children relationships are the source of truth for containment.

A `ResourceTree` is optional. It does not create the hierarchy; it administers a collection of resources that already have their own relationships.

## Responsibility placement

| Capability | Owner | Reason |
|---|---|---|
| Stable UID, name, timestamps, metadata, logical path | Resource | Intrinsic resource state |
| Parent reference | Resource | Reverse side of direct containment |
| Direct child collection and mutation | Container | Source of truth for hierarchy |
| Direct lookup, subtree walk and search | Container | Local containment operations |
| Optional roots and membership | ResourceTree | Administrative scope |
| Global UID index | ResourceTree | Derived lookup structure |
| Global traversal and search | ResourceTree | Operates across all roots |
| Registration, extraction and mounting | ResourceTree | Coordinates membership and multiple resources |
| Filesystem/network I/O and monitoring | Specialization | Domain-specific behavior |

## Forest semantics

A ResourceTree represents a forest: zero or more independent roots.

- Every root is a Resource; it may be an Asset or Container.
- A root has no parent.
- A resource belongs to at most one ResourceTree at a time.
- UIDs are unique within a ResourceTree.
- Names are not globally unique.
- No synthetic root container is required.
- The only public root collection is `roots`; there is no singular-root shortcut or alternate constructor parameter.

## Membership and synchronization

The hierarchy is authoritative in `Container`; the ResourceTree index is derived.

When a managed Container is changed through `append_child()` or `remove_child()`, the owning ResourceTree coordinates the operation and updates membership/index state. A resource already managed by one tree cannot be attached to an unmanaged container or another tree.

Structural views (`uid`, `parent`, `children`, `roots`) are read-only. Mutations go through methods that enforce invariants. The tree UID is also immutable after construction.

Operations that add roots, register subtrees or mount trees validate all affected resources before changing either structure. Failed validation must not leave partial mutations.

## Invariants

- No containment cycles.
- No duplicate child references.
- Parent and child references agree.
- No resource belongs to more than one ResourceTree.
- UIDs are unique within each ResourceTree.
- Every indexed resource is reachable from exactly one root.
- The global index agrees with the containment hierarchy.
- Detaching a subtree clears its tree membership but preserves its internal hierarchy.
- Mounting transfers all source roots and membership atomically.

## Operations versus object methods

An operation belongs on an object when it is intrinsic to that object's generic state or relationship. An operation belongs in an independent service/module when it coordinates multiple resources, performs I/O, depends on an external provider, or supports multiple execution strategies.

## Serialization

The core model classes own their dictionary representations through `to_dict()` and `from_dict()`. The JSON and XML modules encode and decode those dictionaries without knowing specialized resource types. A specialization can override the model methods and provide its own reconstruction factory.

## Extension examples

- `fsresource-tree`: File(Asset), Directory(Container), FSResourceTree(ResourceTree), with ResourceTree optional for direct filesystem structures.
- `netresource-tree`: network resources and connectivity modeled separately from containment.
- `webresource-tree`: server-backed resources and HTTP behavior.
- `noderesource-tree`: network-node hierarchies.

Specializations may extend metadata, override behavior and introduce services, while preserving the core contracts.
