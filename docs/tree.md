# ResourceTree: optional forest manager

## Purpose

A Container already forms a hierarchy through its parent/children relationships. ResourceTree is not required to create, store or traverse that hierarchy. It is an optional administrative object for managing multiple resources and hierarchies as one logical collection.

ResourceTree is independent of Resource. It shares serialization behavior through a separate capability, not through resource inheritance.

## Forest model

A ResourceTree represents zero or more independent roots:

```text
ResourceTree
├── root A: Container
│   ├── Asset
│   └── Container
│       └── Asset
├── root B: Container
│   └── Asset
└── root C: Asset
```

No synthetic root Container is required. Every root is a Resource and may be either an Asset or a Container.

## Responsibilities

ResourceTree provides identity and name for the managed collection, roots, exclusive membership, a derived global UID index, global traversal and search, registration and extraction, and atomic transfer of roots between trees.

Container remains the source of truth for parent/child relationships. The tree index is derived.

## API

- `ResourceTree(roots=[...])`: initialize with zero or more roots.
- `roots`: read-only tuple containing every root.
- `add_root(resource)` / `add_roots(resources)`: register independent roots.
- `register(resource, parent=None)`: register a root or attach a subtree below a managed Container.
- `get(uid)` / `contains(resource)`: global lookup and membership.
- `walk()` / `search(pattern)`: operate across every root.
- `remove(resource)` / `remove_root(resource)`: release membership.
- `mount(entrypoint, tree)`: transfer every source root below a destination Container.

There is one root interface: `roots`. No single-root alias or alternate constructor is provided.

## Serialization

`to_dict()` returns the tree's own type discriminator, UID, name and serialized roots. `ResourceTree.from_dict(data)` reconstructs the roots and registers their resources in the new tree.

The tree does not inherit from Resource. It uses the same independent serialization capability as the resource classes.

## Membership rules

A resource can belong to at most one ResourceTree. A root must have no parent. A resource may be registered only once in a given tree. UIDs must be unique within the forest; names need not be globally unique.

Removing a root or subtree releases membership for all its descendants but preserves their internal parent/children relationships.

## Composition

Mounting transfers all source roots as children of the destination entrypoint. The operation validates every source resource and UID collision before modifying either tree. After a successful mount, the source tree has no roots and no indexed resources.

## When to use ResourceTree

Use resources and Containers directly when local hierarchy management is sufficient. Use ResourceTree when the application needs a global identity, membership boundary, index, cross-root traversal/search or composition of multiple structures.

ResourceTree is an optional manager, not a prerequisite for resource existence or containment.
