# ResourceTree: optional forest manager

## Purpose

A Container already forms a hierarchy through its parent/children relationships. Therefore, ResourceTree is not necessary to create, store or traverse a hierarchy.

ResourceTree remains useful as an optional administrative object when an application needs to manage multiple resources and hierarchies as one logical collection.

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

ResourceTree provides:
- Identity and name for the managed collection.
- Zero or more roots.
- Exclusive resource membership.
- A derived global UID index.
- Global traversal and regular-expression search.
- Registration and extraction of roots or subtrees.
- Atomic transfer of all roots from another ResourceTree.

It does not own the parent/children relationships; Container remains their source of truth.

## API

- `ResourceTree(roots=[...])`: initialize with zero or more roots.
- `roots`: read-only tuple containing every root.
- `add_root(resource)` / `add_roots(resources)`: register independent roots.
- `register(resource, parent=None)`: register a root or attach a subtree below a managed Container.
- `get(uid)` / `contains(resource)`: global lookup and membership.
- `walk()` / `search(pattern)`: operate across every root.
- `remove(resource)` / `remove_root(resource)`: release membership.
- `mount(entrypoint, tree)`: transfer every source root below a destination Container.
- `to_dict()` / `from_dict()`, `to_json()` / `from_json()`, `to_xml()` / `from_xml()`: serialize and reconstruct the managed forest.

There is no singular `root` property or `root=` constructor parameter. Callers must work with the explicit `roots` collection, which has consistent semantics for empty, single-root and multi-root forests.

## Membership rules

A resource can belong to at most one ResourceTree. A root must have no parent. A resource may be registered only once in a given tree. UIDs must be unique within the forest; names need not be globally unique.

The tree UID is immutable after construction. The resource index is derived from the hierarchy and cannot be mutated through the public `resources` view.

Removing a root or subtree releases membership for all its descendants but preserves their internal parent/children relationships.

## Composition

Mounting transfers all source roots as children of the destination entrypoint. The operation validates every source resource and UID collision before modifying either tree. After a successful mount, the source tree has no roots and no indexed resources.

## When to use ResourceTree

Use resources and Containers directly when local hierarchy management is sufficient.

Use ResourceTree when the application needs a global identity, membership boundary, index, cross-root traversal/search or composition of multiple structures.

ResourceTree is an optional manager, not a prerequisite for resource existence or containment.
