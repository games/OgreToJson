from subprocess import call
import json
import os


ogre_converter = 'OgreXMLConverter'


def convert_mesh_to_xml(filename):
	name = filename.lower() + '.mesh'
	call([os.path.abspath(ogre_converter), os.path.abspath(name)])
	convert_xml_to_json(filename)



def convert_xml_to_json(filename):
	import xml.etree.ElementTree as ET
	
	mesh = {}

	materials = parse_materials(filename)

	tree = ET.parse(filename + '.mesh.xml')
	root = tree.getroot()

	sharedgeometry = parse_geometry(root.findall('./sharedgeometry'))
	if sharedgeometry is not None:
		mesh['sharedgeometry'] = sharedgeometry
	mesh['submeshes'] = parse_submeshes(root.findall('./submeshes/submesh'), materials)


	mesh_json = json.dumps(mesh)
	output_file = filename.lower() + '.json'
	f = open(output_file, 'w')
	f.write(mesh_json)
	f.close()
	print 'Export >>>>> ' + output_file



def parse_geometry(xml):
	if len(xml) == 0:
		return None
		
	geo_xml = xml[0]
	geo = {
		'vertexcount' : 0,
		'vertices' : [],
		'normals' : [],
		'texturecoords' : []
	}

	geo['vertexcount'] = float(geo_xml.attrib['vertexcount'])
	vertexbuffer = geo_xml.findall('./vertexbuffer')
	for vb in vertexbuffer:

		if 'positions' in vb.attrib:
			vertex_pos = vb.findall('./vertex/position')

			tmp_list = []
			for e in vertex_pos:
				tmp_list.append(float(e.attrib['x']))
				tmp_list.append(float(e.attrib['y']))
				tmp_list.append(float(e.attrib['z']))
			geo['vertices'] = tmp_list

		if 'normals' in vb.attrib:
			vertex_normals = vb.findall('./vertex/normal')
			tmp_list = []
			for e in vertex_normals:
				tmp_list.append(float(e.attrib['x']))
				tmp_list.append(float(e.attrib['y']))
				tmp_list.append(float(e.attrib['z']))
			geo['normals'] = tmp_list

		if 'texture_coords' in vb.attrib:
			texcoords = vb.findall('./vertex/texcoord')
			tmp_list = []
			for e in texcoords:
				tmp_list.append(float(e.attrib['u']))
				tmp_list.append(float(e.attrib['v']))
			geo['texturecoords'] = tmp_list
		

	return geo



def parse_submeshes(xml, materials):
	if len(xml) == 0:
		return []
	submeshes = []
	for sm in xml:
		mesh = {'material': materials[sm.attrib['material']], 'faces': []}
		faces = sm.findall('./faces/face')
		tmp_list = mesh['faces']
		for e in faces:
			tmp_list.append(float(e.attrib['v1']))
			tmp_list.append(float(e.attrib['v2']))
			tmp_list.append(float(e.attrib['v3']))

		usesharedvertices = sm.attrib['usesharedvertices'] == 'true'
		mesh['usesharedvertices'] = usesharedvertices
		if not usesharedvertices:
			mesh['geometry'] = parse_geometry(sm.findall('./geometry'))
		submeshes.append(mesh)
	return submeshes



def parse_materials(filename):
	materials = {}
	material = None
	file = open(filename + '.material', 'r')
	for line in file:
		l = line.strip()
		if l.startswith('material'):
			material = {}
			material['name'] = l.replace('material', '').strip()
			materials[material['name']] = material
		elif l.startswith('ambient'):
			material['ambient'] = parse_array(l.replace('ambient', ''))
		elif l.startswith('diffuse'):
			material['diffuse'] = parse_array(l.replace('diffuse', ''))
		elif l.startswith('specular'):
			material['specular'] = parse_array(l.replace('specular', ''))
		elif l.startswith('emissive'):
			material['emissive'] = parse_array(l.replace('emissive', ''))
		elif l.startswith('texture'):
			material['texture'] = l.replace('texture', '').strip().lower().replace('.png', '.dds')
	file.close()
	return materials



def parse_array(src):
	return [float(e) for e in src.strip().split(' ')]







if __name__ == "__main__":
	# convert_mesh_to_xml("HUM_F")
	# convert_mesh_to_xml("PET_WOLF")
	convert_xml_to_json('HUM_F')
	# convert_xml_to_json('NPC_HUF_TOWN_01')
	# print parse_materials('HUM_F')












