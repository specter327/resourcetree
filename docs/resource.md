# Resource: generic resource abstraction

`Resource` represents a domain-neutral resource. It does not define what the resource represents or assign domain-specific semantics.

## Identity

Every resource has a stable UID. UUID version 7 is used by default.

The UID is immutable after construction. UIDs must be unique within a ResourceTree, but resources that are not managed by a common tree may exist independently.

A ResourceTree rejects UID collisions before mutating its structure.

## Naming

Every resource has a non-empty name. Names are descriptive and are not globally unique.

Local name uniqueness is not imposed by the generic core. A specialization may define stricter naming rules when its domain requires them.

## Relationships and membership

A resource may have:
- No parent (standalone resource or ResourceTree root).
- One parent Container.
- No ResourceTree membership.
- Membership in at most one ResourceTree.

The `parent` and `tree` properties are read-only views. Relationship changes are performed through Container and ResourceTree operations.

## Metadata and timestamps

Resources expose generic metadata and creation/update timestamps. Domain-specific metadata semantics belong to specializations.

## Independence

A Resource does not require a Container or ResourceTree to exist. It can be used as an independent object.

## Serializacion

La serializacion de un **Resource** transforma sus propiedades en memoria, a un formato descriptivo como:
- JSON
- XML
O alguno otro

Lo cual permite su:
- **Almacenamiento**
- **Transporte e intercambio**

Ademas de su:
- **Serializacion**: Objetos de codigo -> Texto
- **Rehidratacion**: Texto -> Objetos de codigo

De forma consistente y estable.