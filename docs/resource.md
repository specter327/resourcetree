# Resource: Abstraccion de recurso

El elemento Resource representa la abstraccion general de un recurso. No define que recurso, como, ni su semantica.

## Identificacion

Cada recurso debe poder ser identificable de forma **univoca**.
En la praxis, se utiliza: UUID version 7 para dicho proposito.

La identificacion y su **unicidad GLOBAL (en la estructura) deben ser asegurables y protegibles**, creando una **excepcion explicita ante colisiones**.

Para mejorar la fiabilidad de la unicidad, propongo una generacion basada en datos variables como el tiempo, y aleatorias (alta entriopia)

## Nombramiento

Cada recurso debe poder ser nombrable. No unico.
En la praxis, se utiliza: texto semantico variable opcional.

El nombre y su **unicidad LOCAL (en el contexto) deben ser asegurables y protegibles**, creando una **excepcion explicita ante colisiones**