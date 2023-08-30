# py2drawio

## Installation

```pip install py2drawio```

## Example

```python
from py2drawio import Diagram

# Create a diagram
diagram = Diagram()

# Add a VPC Node

vpc = diagram.add_node('vpc1', 'VPC', 'VPC')

# add blank container for public subnets

public_subnet_container = diagram.add_node('public_subnet_container', 'BlankContainer', 'Public Subnets', parent=vpc)

# add blank container for private subnets
private_subnet_container = diagram.add_node('private_subnet_container', 'BlankContainer', 'Private Subnets', parent=vpc)

# Create 3 public subnets and 3 provate subnets

availability_zones = ['eu-west-1a', 'eu-west-1b', 'eu-west-1c']

public_subnets = { az: diagram.add_node(f'public_subnet_{az}', 'PublicSubnet', f'Public Subnet {az}', parent=public_subnet_container) for az in availability_zones
}

private_subnets = { az: diagram.add_node(f'private_subnet_{az}', 'PrivateSubnet', f'Private Subnet {az}', parent=private_subnet_container) for az in availability_zones
}

# Create a reverse proxy in one of the public subnets

reverse_proxy = diagram.add_node('reverse_proxy', 'EC2Instance', 'Reverse Proxy', parent=public_subnets['eu-west-1b'])

# create a web server in each of the private subnets

web_servers = { az: diagram.add_node(f'web_server_{az}', 'EC2Instance', f'Web Server {az}', parent=private_subnets[az]) for az in availability_zones}

# create an RDS instance in one of the private subnets

rds_instance = diagram.add_node('rds_instance',  'RDSInstance', 'rds_instance', parent=private_subnets['eu-west-1b'])

# create edges between webservers and reverse proxy

for az, web_server in web_servers.items():
    diagram.add_edge(web_server, reverse_proxy)

# Compose the parent containers in reverse order

for az, subnet in public_subnets.items():
    diagram.compose_children(subnet, orientation='portrait')
for az, subnet in private_subnets.items():
    diagram.compose_children(subnet, orientation='portrait')
diagram.compose_children(public_subnet_container, width = len(public_subnets), text_padding = 20)
diagram.compose_children(private_subnet_container, width = len(private_subnets), text_padding = 20)
diagram.compose_children(vpc, vpack=True, text_padding = 10, cell_padding = 0)

# Write the diagram to a file
diagram.write('testout.drawio')
```

## Submodules

## py2drawio.diagram module

### *class* py2drawio.diagram.Diagram(filename=None, template=None)

Bases: `object`

A class for creating and editing draw.io diagrams

#### filename

The filename of the draw.io file to be edited. If not specified, a new file will be created.

* **Type:**
  str, optional

#### template

The filename of the template file in yaml format to be used. If not specified, the default template will be used.

* **Type:**
  str, optional

#### \_\_init_\_(filename=None, template=None)

* **Parameters:**
  * **filename** (*str**,* *optional*) – The filename of the draw.io file to be edited. If not specified, a new file will be created.
  * **template** (*str**,* *optional*) – The filename of the template file in yaml format to be used. If not specified, the default template will be used.

#### add_edge(source, target, name=None)

Adds an edge between two nodes to the diagram

* **Parameters:**
  * **source** (*Node*) – The source node of the edge to be added
  * **target** (*Node*) – The target node of the edge to be added
  * **name** (*str**,* *optional*) – The name of the edge to be added. If not specified, the edge will have no name.
* **Returns:**
  **edge** – The edge that was added
* **Return type:**
  Edge

#### add_node(node_id, node_type, node_name, node_height=None, node_width=None, layer=0, parent=None)

Adds a node to the diagram

* **Parameters:**
  * **node_id** (*str*) – The ID of the node to be added
  * **node_type** (*str*) – The type of the node to be added
  * **node_name** (*str*) – The name of the node to be added
  * **node_height** (*int**,* *optional*) – The height of the node to be added. If not specified, the default height for the node type will be used.
  * **node_width** (*int**,* *optional*) – The width of the node to be added. If not specified, the default width for the node type will be used.
  * **layer** (*int**,* *optional*) – The layer of the node to be added. If not specified, the node will be added to layer 0.
  * **parent** (*Node**,* *optional*) – The parent node of the node to be added. If not specified, the node will be added to the root node.
* **Returns:**
  **node** – The node that was added
* **Return type:**
  Node

#### compose_children(parent, cell_padding=20, text_padding=40, width=None, height=None, orientation='landscape', sorted=False, hpack=False, vpack=False)

Composes the children of an explicitly specified parent node into a grid.

Grid size is determined by the number of children and the specified width, height, or orientation. If width and height are not specified, the grid will be as square as possible. If width or height is specified, the required grid size will be calculated based on the specified value. If neither width nor height is specified and a square shape is not the optimal shape for the number of children, non-square grid shape will be determined by the orientation specified. Id no orientation is specified, the default orientation (“landscape”) will be used.

* **Parameters:**
  * **parent** (*Node*) – The parent node to be composed
  * **cell_padding** (*int**,* *optional*) – The padding between cells in the grid. If not specified, the default padding (20) will be used.
  * **text_padding** (*int**,* *optional*) – The padding between the text and the cell border. If not specified, the default padding (20) will be used.
  * **width** (*int**,* *optional*) – The width of the grid. If not specified, the grid width will be determined by the values provided in height or orientation. Specify either width or height, not both.
  * **height** (*int**,* *optional*) – The height of the grid. If not specified, the grid will be as tall as possible. If not specified, the grid height will be determined by the values provided in width or orientation. Specify either width or height, not both.
  * **orientation** (*{"landscape"**,* *"portrait"}**,* *optional*) – The orientation of the grid. If not specified, the default orientation (“landscape”) will be used. This value is ignored if width or height are specified.
  * **sorted** (*bool**,* *optional*) – If true, sorts the contents of the parent by type then label. Default False
* **Return type:**
  None

#### compose_parents(parent_types, cell_padding=20, text_padding=40, width=None, height=None, orientation='landscape')

Composes the children of all parent nodes of the specified types into a grid as per the specification of compose_children method.

* **Parameters:**
  * **parent_types** (*list* *of* *str*) – The types of the parent nodes to be composed
  * **cell_padding** (*int**,* *optional*) – The padding between cells in the grid. If not specified, the default padding (20) will be used.
  * **text_padding** (*int**,* *optional*) – The padding between the text and the cell border. If not specified, the default padding (40) will be used.
  * **width** (*int**,* *optional*) – The width of the grid. If not specified, the grid width will be determined by the values provided in height or orientation. Specify either width or height, not both.
  * **height** (*int**,* *optional*) – The height of the grid. If not specified, the grid height will be determined by the values provided in width or orientation. Specify either width or height, not both.
  * **orientation** (*{"landscape"**,* *"portrait"}**,* *optional*) – The orientation of the grid. If not specified, the default orientation (“landscape”) will be used. This value is ignored if width or height are specified.
* **Return type:**
  None

#### extract_node_types(outfile)

Extracts the node types from a draw.io file and saves them to a yaml file

* **Parameters:**
  **outfile** (*str*) – The filename of the yaml file to be created
* **Return type:**
  None

#### write(filename=None)

Writes the diagram to a draw.io file

* **Parameters:**
  **filename** (*str**,* *optional*) – The filename of the draw.io file to be written. If not specified, the filename specified in the constructor will be used. If no filename was specified in the constructor, a ValueError will be raised.


