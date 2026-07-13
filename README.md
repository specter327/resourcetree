# resourcetree
## Framework genérico para árboles jerárquicos de recursos

### Propósito principal
`resourcetree` es un framework genérico diseñado para modelar y manipular estructuras de datos jerárquicas basadas en árboles. Su objetivo es proporcionar una base conceptual y estructural para representar cualquier sistema que pueda organizarse como una jerarquía de elementos, sin imponer un dominio específico.

### Observaciones clave
- **Modelo de árbol genérico**: La librería se basa en dos tipos fundamentales de elementos:
  - **Ramas (Containers)**: Unidades contenedoras que pueden albergar otras ramas u hojas.
  - **Hojas (Assets)**: Unidades autocontenidas que representan elementos terminales.
- **Versatilidad conceptual**: El marco es aplicable en una amplia variedad de campos y dominios (sistemas de archivos, redes, configuraciones, etc.).
- **Base para especializaciones**: No está diseñada como una librería final, sino como una capa fundamental sobre la que se pueden construir especializaciones concretas (por ejemplo, `fsresource-tree`).

### Ejemplo de uso
```python
# Importación de la librería
import resourcetree

# Creación de una rama (contenedor)
rama = resourcetree.Container("rama")

# Creación de una hoja (recurso terminal)
hoja = resourcetree.Asset(
    "hoja",
    rama
)