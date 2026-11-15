# Asset(Resource): terminal resource

`Asset` represents a terminal resource: a resource that does not contain other resources.

It may hold an optional `data` payload. The payload is generic and its interpretation belongs to the application or specialization.

An Asset can exist independently, be a child of a Container, or be a root of a ResourceTree. A ResourceTree is not required.
