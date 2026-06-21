# resourcetree


Generic hierarchical resource tree framework.


## Example


```python
import resourcetree as rt


root = rt.Container("root")

file = rt.Asset(
    "data.txt",
    root
)