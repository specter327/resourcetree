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