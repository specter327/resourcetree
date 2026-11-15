# ResourceTree: Abstraccion de arbol de recursos

El elemento ResourceTree representa la union como **conjunto** (compuesto) de **recursos**, como:
- Container
- Asset

Proporciona:
- Propiedad (pertenencia)
- Estructura

### Diagrama

```text
ResourceTree1

  Container1
    Asset1
    Asset2

    Container2
      Container3
        Asset3
        Asset4

      Asset5

ResourceTree2

  Container1
    Asset1
    Asset2
```

## Identificacion

Cada arbol de recursos debe ser identificable de forma **univoca**.
En la praxis, se utiliza: UUID version 7 para dicho proposito.

## Nombramiento

Cada arbol de recursos debe poder ser nombrable.
En la praxis, se utiliza: texto semantico variable opcional

## Montaje

Si el ResourceTree es un arbol de recursos, debe permitir su integracion; en cuyo caso, el **montaje** de contenedores es necesario.
Pero, tambien es posible el montaje de arboles de recursos en otros arboles de recursos. Simplemente: montando todos los contenedores raiz (primer nivel de anidacion) dentro del otro arbol