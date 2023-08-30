import xml.etree.ElementTree as ET
from math import ceil,sqrt
from yaml import safe_load, safe_dump
from os.path import realpath
from .base_xml import base_xml


class Diagram:
    """
    A class for creating and editing draw.io diagrams

    Attributes
    ----------
    filename : str, optional
        The filename of the draw.io file to be edited. If not specified, a new file will be created.
    template : str, optional
        The filename of the template file in yaml format to be used. If not specified, the default template will be used.
    """
    base_xml = base_xml
    def __init__(self, filename: str=None, template: str = None):
        """
        Parameters
        ----------
        filename : str, optional
            The filename of the draw.io file to be edited. If not specified, a new file will be created.
        template : str, optional
            The filename of the template file in yaml format to be used. If not specified, the default template will be used.
        """
        if template is not None:
            template_path = template
        else:
            template_path = realpath(__file__).replace("diagram.py", "nodetypes.yml")
        with open(template_path) as f:
            self.nodetypes = safe_load(f)
        if filename is None:
            self.filename = None
            self.root = ET.fromstring(self.base_xml)            
        else:  
            self.filename = filename
            self.root = ET.parse(filename).getroot()
        self.diagroot = self.root.find("./diagram/mxGraphModel/root")

    def extract_node_types(self, outfile: str):
        """
        Extracts the node types from a draw.io file and saves them to a yaml file

        Parameters
        ----------
        outfile : str
            The filename of the yaml file to be created
        
        Returns
        -------
        None
        """
        node_types = {}
        node_types["BlankContainer"] =  {
            "style": "fillColor=none;strokeColor=none;dashed=0;verticalAlign=top;fontStyle=0;fontColor=#232F3D;",
            "width": "130",
            "height": "130",
        }
        for node in self.diagroot.iter('mxCell'):
            type = node.attrib.get('value')
            if type is not None:
                style = node.attrib.get('style')
                geometries = node.findall('mxGeometry')
                if len(geometries) > 0:
                    width = geometries[0].attrib.get('width')
                    height = geometries[0].attrib.get('height')
                # if style is not None and width is not None and height is not None:
                if type not in node_types.keys():
                    node_types[type] = {
                        'style': style,
                        'width': width,
                        'height': height
                    }
        with open(outfile, 'w') as f:
            f.write(safe_dump(node_types, default_flow_style=False))

    def add_node(self, node_id: str, node_type: str, node_name: str, node_height:int = None, node_width: int = None, layer: int = 0, parent = None):
        """
        Adds a node to the diagram

        Parameters
        ----------
        node_id : str
            The ID of the node to be added
        node_type : str
            The type of the node to be added
        node_name : str
            The name of the node to be added
        node_height : int, optional
            The height of the node to be added. If not specified, the default height for the node type will be used.
        node_width : int, optional
            The width of the node to be added. If not specified, the default width for the node type will be used.
        layer : int, optional
            The layer of the node to be added. If not specified, the node will be added to layer 0.
        parent : Node, optional
            The parent node of the node to be added. If not specified, the node will be added to the root node.

        Returns
        -------
        node : Node
            The node that was added
        """
        if node_id in ["0", "1"]:
            raise ValueError("Node ID cannot be 0 or 1")
        existing_nodes = [node for node in self.diagroot if node.tag == "object" and node.attrib['id'] == node_id]
        if len(existing_nodes) > 0:
            raise ValueError(f"Node with ID {node_id} already exists")
        if node_type not in self.nodetypes:
            raise ValueError(f"Node type {node_type} not found")
        if node_height is None:
            height = self.nodetypes[node_type]['height']
        else:
            x = str(node_height)
        if node_width is None: 
            width = self.nodetypes[node_type]['width']
        else:
            width = str(node_width)
        if parent is None:
            parent_id = "1"
        elif not isinstance(parent, ET.Element):
            raise ValueError("Parent must be a Node")
        elif parent.attrib.get('type') not in self.nodetypes:
            raise ValueError("Parent must be a valid node type")
        # elif int(parent.attrib.get('layer')) >= layer:
        #     raise ValueError("Parent must be in a lower layer than the node")
        else:
            parent_id = parent.attrib.get('id')
            
        node = ET.SubElement(self.diagroot, 'object')
        node.set('label', node_name)
        node.set('id', node_id)
        node.set('type', node_type)
        node.set('layer', str(layer))
        mxcell = ET.SubElement(node, 'mxCell')
        mxcell.set('style', self.nodetypes[node_type]['style'])
        mxcell.set('vertex', '1')
        mxcell.set('parent', parent_id)
        mxgeometry = ET.SubElement(mxcell, 'mxGeometry')
        mxgeometry.set('x', '0')
        mxgeometry.set('y', '0')
        mxgeometry.set('width', width)
        mxgeometry.set('height', height)
        mxgeometry.set('as', 'geometry') 
        return node
    
    def add_edge(self, source: ET.Element, target: ET.Element, name: str = None):
        """
        Adds an edge between two nodes to the diagram

        Parameters
        ----------
        source : Node
            The source node of the edge to be added
        target : Node
            The target node of the edge to be added
        name : str, optional
            The name of the edge to be added. If not specified, the edge will have no name.

        Returns
        -------
        edge : Edge
            The edge that was added
        """
        default_style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
        if not isinstance(source, ET.Element):
            raise ValueError("Source must be a Node")
        if source.attrib.get('type') not in self.nodetypes:
            raise ValueError("Source must be a valid node type")
        if not isinstance(target, ET.Element):          
            raise ValueError("Target must be a Node")
        if target.attrib.get('type') not in self.nodetypes:
            raise ValueError("Target must be a valid node type")
        if name is None:
            name = ""
        id = f"{source.attrib.get('id')}-{target.attrib.get('id')}"
        existing_edges = [edge for edge in self.diagroot if edge.tag == "object" and edge.attrib.get('id') == id]
        if len(existing_edges) > 0:
            raise ValueError(f"Edge between {source.attrib.get('id')} and {target.attrib.get('id')} already exists")
        edge = ET.SubElement(self.diagroot, 'object')
        edge.set('label', name)
        edge.set('id', id)
        edge.set('type', 'edge')
        mxcell = ET.SubElement(edge, 'mxCell')
        mxcell.set('style', default_style)
        mxcell.set('edge', '1')
        mxcell.set('parent', '1')
        mxcell.set('source', source.attrib.get('id'))
        mxcell.set('target', target.attrib.get('id'))
        mxgeometry = ET.SubElement(mxcell, 'mxGeometry')
        mxgeometry.set('relative', '1')
        mxgeometry.set('as', 'geometry')
        return edge
    
    def compose_children(self, parent: ET.Element, cell_padding:int=20, text_padding:int=40, width:int=None, height:int=None, orientation:str="landscape", sorted:bool=False, hpack:bool=False, vpack:bool=False):
        """
        Composes the children of an explicitly specified parent node into a grid.

        Grid size is determined by the number of children and the specified width, height, or orientation. If width and height are not specified, the grid will be as square as possible. If width or height is specified, the required grid size will be calculated based on the specified value. If neither width nor height is specified and a square shape is not the optimal shape for the number of children, non-square grid shape will be determined by the orientation specified. Id no orientation is specified, the default orientation ("landscape") will be used.

        Parameters
        ----------
        parent : Node
            The parent node to be composed
        cell_padding : int, optional
            The padding between cells in the grid. If not specified, the default padding (20) will be used.
        text_padding : int, optional
            The padding between the text and the cell border. If not specified, the default padding (20) will be used.
        width : int, optional
            The width of the grid. If not specified, the grid width will be determined by the values provided in height or orientation. Specify either width or height, not both.
        height : int, optional
            The height of the grid. If not specified, the grid will be as tall as possible. If not specified, the grid height will be determined by the values provided in width or orientation. Specify either width or height, not both.
        orientation : {"landscape", "portrait"}, optional
            The orientation of the grid. If not specified, the default orientation ("landscape") will be used. This value is ignored if width or height are specified.
        sorted : bool, optional
            If true, sorts the contents of the parent by type then label. Default False
        
        Returns
        -------
        None
        """
        contents = [node for node in self.diagroot if node.tag == "object" and node.find('mxCell').attrib.get('parent',None) == parent.attrib.get('id')]
        if len(contents) == 0:
            return
        if sorted:
            contents.sort(key=lambda x: (x.attrib.get('type'), x.attrib.get('label', None)))
        # for x in contents:
        #     print(x.attrib.get('type'))
        #     print(x.attrib.get('label'))
        content_heights = [int(content.find('mxCell').find('mxGeometry').attrib.get('height')) for content in contents]
        content_widths = [int(content.find('mxCell').find('mxGeometry').attrib.get('width')) for content in contents]
        content_max_height = max(content_heights)
        content_max_width = max(content_widths)
        if orientation not in ["landscape", "portrait"]:
            raise ValueError("Orientation must be landscape or portrait")
        if width is not None and height is not None:
            raise ValueError("Cannot specify both width and height")
        if hpack and vpack:
            raise ValueError("Cannot specify both hpack and vpack")
        if vpack:
            grid_x = 1
            grid_y = len(contents)
        elif hpack:
            grid_x = len(contents)
            grid_y = 1
        else:
            if width is None and height is None and orientation == "landscape":
                grid_x = ceil(sqrt(len(contents)))
                grid_y = ceil(len(contents) / grid_x)
            elif width is None and height is None and orientation == "portrait":
                grid_y = ceil(sqrt(len(contents)))
                grid_x = ceil(len(contents) / grid_y)
            elif width is not None and height is None:
                grid_x = width
                grid_y = ceil(len(contents) / width)
            elif width is None and height is not None:
                grid_x = ceil(len(contents) / height)
                grid_y = height

        parent_width = max(
            int(parent.find('mxCell').find('mxGeometry').get('width')),
            cell_padding + ((content_max_width + cell_padding) * grid_x)
        )
        parent.find('mxCell').find('mxGeometry').set('width', str(parent_width))


        parent_height = max(
            int(parent.find('mxCell').find('mxGeometry').get('height')),
            text_padding + ((content_max_height + text_padding) * grid_y)
        )
        parent.find('mxCell').find('mxGeometry').set('height', str(parent_height))

        if hpack:
            parent_width = sum(content_widths) + (cell_padding * (len(content_widths)+1))
            parent.find('mxCell').find('mxGeometry').set('width', str(parent_width))
            current_width = cell_padding
            for element, content in enumerate(contents):
                element_x = current_width
                content.find('mxCell').find('mxGeometry').set('x', str(element_x))
                current_width = current_width + int(content.find('mxCell').find('mxGeometry').get('width')) + cell_padding

        if vpack:
            parent_height = sum(content_heights) + (text_padding * (len(content_heights)+1))
            parent.find('mxCell').find('mxGeometry').set('height', str(parent_height))
            current_height = text_padding
            for element, content in enumerate(contents):
                element_y = current_height
                content.find('mxCell').find('mxGeometry').set('y', str(element_y))
                current_height = current_height + int(content.find('mxCell').find('mxGeometry').get('height')) + text_padding

        width_pad = (parent_width - (grid_x * content_max_width))/(grid_x+1)
        height_pad = (parent_height - (grid_y * content_max_height))/(grid_y+1)
        for element, content in enumerate(contents):
            if not hpack:
                element_x = (
                    width_pad 
                    + ((element % grid_x) * (content_max_width + width_pad)) 
                    + ((content_max_width) / 2)
                    - (int(content.find('mxCell').find('mxGeometry').get('width')) / 2)
                )
                content.find('mxCell').find('mxGeometry').set('x', str(element_x))
            if not vpack:
                element_y = (
                    height_pad
                    + ((element // grid_x) * (content_max_height + height_pad))
                    + ((content_max_height) / 2)
                    - (int(content.find('mxCell').find('mxGeometry').get('height')) / 2)
                )
                content.find('mxCell').find('mxGeometry').set('y', str(element_y))


    def compose_parents(self, parent_types: list, cell_padding:int=20, text_padding:int=40, width:int=None, height:int=None, orientation:str="landscape"):
        """
        Composes the children of all parent nodes of the specified types into a grid as per the specification of compose_children method.

        Parameters
        ----------
        parent_types : list of str
            The types of the parent nodes to be composed
        cell_padding : int, optional
            The padding between cells in the grid. If not specified, the default padding (20) will be used.
        text_padding : int, optional
            The padding between the text and the cell border. If not specified, the default padding (40) will be used.
        width : int, optional
            The width of the grid. If not specified, the grid width will be determined by the values provided in height or orientation. Specify either width or height, not both.
        height : int, optional
            The height of the grid. If not specified, the grid height will be determined by the values provided in width or orientation. Specify either width or height, not both.
        orientation : {"landscape", "portrait"}, optional
            The orientation of the grid. If not specified, the default orientation ("landscape") will be used. This value is ignored if width or height are specified.

        Returns
        -------
        None
        """
        parents = [node for node in self.diagroot if node.tag == "object" and node.attrib.get('type') in parent_types]
        for parent in parents:
            self.compose_children(parent, cell_padding, text_padding, width, height, orientation)

    # def get_grid_size(self, elements:int):
    #     cols = ceil(sqrt(elements))
    #     rows = ceil(elements / cols)
    #     return (cols, rows)
    
    def write(self, filename=None):
        """
        Writes the diagram to a draw.io file

        Parameters
        ----------
        filename : str, optional
            The filename of the draw.io file to be written. If not specified, the filename specified in the constructor will be used. If no filename was specified in the constructor, a ValueError will be raised.
        """
        if filename is None:
            if self.filename is None:
                raise ValueError("No filename specified")
            else:
                filename = self.filename
        ET.ElementTree(self.root).write(filename)