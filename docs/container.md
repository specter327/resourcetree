# Container(Resource): Abstraccion de contenedor

El elemento Container representa la abstraccion general de un contenedor, y es un **tipo** de recurso: su principal caracteristica es que su objetivo es **almacenar** otros recursos:
- Container
- Asset

## Contenedor e hijos

Sutge una duda: ¿El contenedor tiene como "hijos" a los elementos que contiene?
Ejemplo:

Container1
  -> Children1
  -> Children2
  -> Children3

En caso de que si:
- ¿El contenedor almacena la informacion de la relacion con los otros elementos? <- Monolitico
- ¿El arbol de recursos (ResourceTree) almacena la informacion de la relacion entre elementos? <- Para mantener relaciones, NECESITA un arbol de recursos - lo cual es coherente, si pensamos que el Container y Asset son **recursos**, mientras que el arbol es **pertenencia y composicion como conjunto**

- En caso de que el contenedor mantenga las relaciones; no seria necesario un arbol de recursos para poder componer estructuras, pero entonces el ResourceTree tendria que operar de forma recursiva sobre los contenedores para descubrir la verdad

> Porque, si mantenemos DOS verdades, terminaran deslizandose o simplemente provocando duplicidad peligrosa e inutil.

## Especificacion

Cuando se indican conjuntos de recursos, se necesita **especificacion**, la cual nos permita señalar a un recurso frente a otros; de manera univoca.

Podemos utilizar la identificacion, la cual es unica e inequivoca, porque el nombre **no lo es**. Pero ¿Que notacion de especificacion utilizaremos?

Podemos utilizar: **notacion por simbolo**
El simbolo es configurable. Por ejemplo:
1. "."
2. "/"
3. "\\"

Lo cual permita utilizar, rutas como:
- "Container1.Container2.Container3.Asset1"
- "Container1/Container2/Container3/Asset1"

## Operacion recursiva

La operacion recursiva sobre un contenedor y sus hijos es una operacion explorativa, la cual indaga y profundiza entre los niveles de anidacion.
Por ello surge una duda:
- ¿Las operaciones deberian implementarse SOBRE el recurso: contenedor, o sobre el arbol de recursos?

Ademas:
- Si el contenedor posee a sus hijos, y el arbol no duplica dichos datos; ¿Entonces el arbol de recursos podria proporcionar unicamente una indexacion global auto-reflejada de todos sus recursos pertenecientes?

Semejante a:

```text
ResourceTree
  1: ContainerX
  2: ContainerY
  3: AssetZ
  ...
```