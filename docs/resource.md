# Resource: generic resource abstraction

`Resource` represents a domain-neutral resource. It does not define what the resource represents or assign domain-specific semantics.

## Identity and state

Every resource has a stable UID (UUIDv7 by default), a non-empty name, creation and update timestamps, and generic metadata. UIDs are immutable after construction and must be unique within a ResourceTree.

## Relationships and membership

A resource may be standalone, be a child of one Container, or be a root in a ResourceTree. A resource can belong to at most one ResourceTree. Parent and tree references are runtime relationships, not duplicated fields in the serialized representation.

## Dictionary representation

`to_dict()` returns the serializable state owned by the resource: its type discriminator, UID, name, timestamps and metadata. `Resource.from_dict(data)` reconstructs a Resource with that state.

Subclasses extend the representation with their own state. For example, Asset includes its `data` payload and Container includes its children. The hierarchy is represented through children; parent links are restored when a Container is reconstructed.

## Text formats

The shared serialization methods expose:

- `to_json()` / `from_json(text)`
- `to_xml()` / `from_xml(text)`

Both formats encode the same dictionary representation. They do not define persistence, filesystem I/O, network transport or database storage.

The built-in JSON and XML adapters support scalar values, lists and string-keyed dictionaries. Payloads must be representable in the selected format. Specializations may reuse, extend, override or omit these capabilities.
