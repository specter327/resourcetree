# Container(Resource): containment abstraction

A `Container` is a Resource that can contain other Resources, including other Containers and Assets.

## Source of truth

The hierarchy is maintained by direct relationships:

- A Container owns its direct children.
- Each child exposes its parent Container.
- The ResourceTree does not duplicate these relationships.

`children` returns a read-only tuple. Use `append_child()` and `remove_child()` to modify containment.

## Independence from ResourceTree

A Container can construct, mutate, search and traverse its hierarchy without a ResourceTree.

```python
from resourcetree import Asset, Container

root = Container("root")
documents = Container("documents", parent=root)
report = Asset("report", parent=documents)

for resource in root.walk():
    print(resource.name)
```

## Managed containers

When a Container belongs to a ResourceTree, its structural methods coordinate with that tree. Adding a subtree registers all its resources; removing a subtree releases membership and index entries while preserving relationships inside the detached subtree.

A resource managed by a ResourceTree cannot be moved directly into an unmanaged Container or a different tree. It must first be detached through its owning tree.

## Operations

- `append_child(resource)`: attach a resource as a direct child.
- `remove_child(resource)`: detach a direct child.
- `find(name)`: find a direct child by name.
- `walk()`: depth-first traversal of this Container and its descendants.
- `search(pattern, flags=0)`: regular-expression search within this subtree.

Traversal detects cycles or duplicate object references rather than looping indefinitely.

## Scope

Container operations move downward through the contained subtree. They do not search ancestors or sibling branches.
