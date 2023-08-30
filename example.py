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