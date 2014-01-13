import subprocess
import json
import os
import xml.etree.ElementTree as ET


ogre_converter = 'OgreXMLConverter.exe'


def convert_mesh_to_xml(filename):
	name = filename.lower() + '.mesh'
	print [os.path.abspath(ogre_converter), os.path.abspath(name)]
	subprocess.call([os.path.abspath(ogre_converter), os.path.abspath(name)])

	name = filename.lower() + '.skeleton'
	subprocess.call([os.path.abspath(ogre_converter), os.path.abspath(name)])

	convert_xml_to_json(filename)


materials = {}

def convert_xml_to_json(filename):
	tree = ET.parse(filename + '.mesh.xml')
	xml_root = tree.getroot()

	# parse materials
	materials = _parse_materials(filename)

	# parse meshes
	mesh_root = _parse_mesh(xml_root)

	out = {
		'materials': materials,
		'mesh': mesh_root
	}

	mesh_json = json.dumps(out)
	output_file = filename.lower() + '.json'
	f = open(output_file, 'w')
	f.write(mesh_json)
	f.close()
	print 'Export >>>>> ' + output_file


def _parse_materials(filename):
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


def _parse_mesh(xml):
	mesh = {}

	# parse geometry
	geo_xml = xml.find('sharedgeometry')
	if not geo_xml:
		geo_xml = xml.find('geometry')
	if geo_xml is not None:
		mesh["geometry"] = _parse_geometry(geo_xml)

	faces_xml = xml.find('faces')
	if faces_xml is not None:
		mesh['faces'] = _parse_faces(faces_xml)

	bones_assignments_xml = xml.find('bonesassignments')
	if bones_assignments_xml is not None:
		mesh['bonesassignments'] = _parse_bones_assignments(bones_assignments_xml)

	
	if 'material' in xml.attrib:
		mesh['material'] = xml.attrib['material']

	# parse skeleton
	skeletonlink = xml.find('skeletonlink')
	if skeletonlink is not None:
		mesh['skeleton'] = _parse_skeleton(skeletonlink.attrib['name'])

	submeshes_xml = xml.findall('./submeshes/submesh')
	if submeshes_xml is not None and len(submeshes_xml) > 0:
		mesh['submeshes'] = []
		for sm in submeshes_xml:
			mesh['submeshes'].append(_parse_mesh(sm))

	return mesh


def _parse_geometry(xml):
	geometry = {}
	geometry['vertexcount'] = xml.attrib['vertexcount']
	geometry['positions'] = []
	geometry['normals'] = []
	geometry['texturecoords'] = []

	vertexbuffer = xml.findall('./vertexbuffer')
	for vb in vertexbuffer:
		if 'positions' in vb.attrib:
			vertex_pos = vb.findall('./vertex/position')

			tmp_list = []
			for e in vertex_pos:
				tmp_list.append(float(e.attrib['x']))
				tmp_list.append(float(e.attrib['y']))
				tmp_list.append(float(e.attrib['z']))
			geometry['positions'] = tmp_list

		if 'normals' in vb.attrib:
			vertex_normals = vb.findall('./vertex/normal')
			tmp_list = []
			for e in vertex_normals:
				tmp_list.append(float(e.attrib['x']))
				tmp_list.append(float(e.attrib['y']))
				tmp_list.append(float(e.attrib['z']))
			geometry['normals'] = tmp_list

		if 'texture_coords' in vb.attrib:
			texcoords = vb.findall('./vertex/texcoord')
			tmp_list = []
			for e in texcoords:
				tmp_list.append(float(e.attrib['u']))
				tmp_list.append(float(e.attrib['v']))
			geometry['texturecoords'] = tmp_list
	return geometry


def _parse_faces(xml):
	faces_xml = xml.findall('./face')
	tmp_list = []
	for e in faces_xml:
		tmp_list.append(float(e.attrib['v1']))
		tmp_list.append(float(e.attrib['v2']))
		tmp_list.append(float(e.attrib['v3']))
	return tmp_list


def _parse_bones_assignments(xml):
	bones_xml = xml.findall('./bonesassignments/vertexboneassignment')
	tmp_list = []
	for e in bones_xml:
		tmp_list.append(float(e.attrib['vertexindex']))
		tmp_list.append(float(e.attrib['boneindex']))
		tmp_list.append(float(e.attrib['weight']))
	return tmp_list


def _parse_skeleton(filename):
	skeleton_xml = ET.parse(filename + '.xml').getroot()
	
	skeleton = {}
	if 'blendmode' in skeleton_xml.attrib:
		skeleton['blendmode'] = skeleton_xml.attrib['blendmode']

	# bind pose
	joints = []
	joints_map = {}
	joints_xml = skeleton_xml.findall('./bones/bone')
	for e in joints_xml:
		joint = {}
		joint['id'] = float(e.attrib['id'])
		joint['name'] = e.attrib['name']
		joint['position'] = []
		
		pos = e.find('position')
		joint['position'].append(float(pos.attrib['x']))
		joint['position'].append(float(pos.attrib['y']))
		joint['position'].append(float(pos.attrib['z']))

		rot = e.find('rotation')
		axis = rot.find('axis')
		joint['rotation'] = {
			'angle': rot.attrib['angle'],
			'axis': [float(axis.attrib['x']), float(axis.attrib['y']), float(axis.attrib['z'])]
		}
		joints.append(joint)
		joints_map[joint['name']] = joint
	skeleton['joints'] = joints

	# hierarchy of joints
	hierarchy_xml = skeleton_xml.findall('./bonehierarchy/boneparent')
	for e in hierarchy_xml:
		name = e.attrib['bone']
		parent = e.attrib['parent']
		joint = joints_map[name]
		if parent == 'root':
			joint['parent'] = -1
		else:
			joint['parent'] = joints_map[parent]['id']

	return skeleton


def parse_array(src):
	return [float(e) for e in src.strip().split(' ')]



if __name__ == "__main__":
	# convert_mesh_to_xml("HUM_F")
	# convert_mesh_to_xml("PET_WOLF")
	# convert_xml_to_json('HUM_F')
	# convert_xml_to_json('NPC_HUF_TOWN_01')
	# print parse_materials('HUM_F')
	# convert_mesh_to_xml('GREATSWORD21')
	# convert_skeleton_to_xml('IDLE_BOW')

	convert_mesh_to_xml('HUM_F')