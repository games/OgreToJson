from subprocess import call

def convert_mesh_to_xml(filename):
	name = filename.lower()
	call("OgreXMLConverter.exe " + name)
	convert_xml_to_json(name + '.xml')


def read_xml(filename):
	file = open(filename, 'r')
	source = file.read()
	file.close()
	print source

def convert_xml_to_json(filename):
	import xml.etree.ElementTree as ET
	
	mesh = {
		'sharedgeometry' : {
			'vertexcount' : 0,
			'vertices' : [],
			'normals' : [],
			'texturecoords' : []
		}, 
		'submeshes' : []
	}

	tree = ET.parse(filename)
	root = tree.getroot()

	mesh.sharedgeometry = parse_geometry(root.findall('./sharedgeometry'))



def parse_geometry(xml):
	if len(xml) == 0:
		return {}
		
	geo_xml = xml[0]
	geo = {
		'vertexcount' : 0,
		'vertices' : [],
		'normals' : [],
		'texturecoords' : []
	}

	geo['vertexcount'] = geo_xml.attrib['vertexcount']
	vertexbuffer = geo_xml.findall('./vertexbuffer')
	vertexbuffer






if __name__ == "__main__":
	# convert_mesh_to_xml("HUM_F.MESH")
	# convert_xml_to_json('HUM_F.MESH.xml')
	convert_xml_to_json('NPC_HUF_TOWN_01.MESH.xml')