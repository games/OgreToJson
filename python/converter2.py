import subprocess
import json
import os
import glob
import sys
import xml.etree.ElementTree as ET


ogre_converter = 'OgreXMLConverter'
ogre_upgrader = 'OgreMeshUpgrader'

dir_name = ''
file_name = ''

def full_name(n):
	return os.path.join(dir_name, os.path.basename(n))

def convert_mesh_to_xml(name):
	global dir_name, file_name, ogre_converter, ogre_upgrader

	dir_name = os.path.dirname(os.path.abspath(name))
	file_name = os.path.basename(name).replace('.MESH', '')

	platform = sys.platform
	if platform.startswith('win'):
		ogre_converter += '.exe'
		ogre_upgrader += '.exe'

	upgrader = os.path.abspath(ogre_upgrader)
	converter = os.path.abspath(ogre_converter)

	ogre_files = []
	for f in os.listdir(dir_name):
		if f.lower().endswith(".skeleton"):
			ogre_files.append(full_name(f))
	# mesh file
	ogre_files.append(os.path.abspath(name))

	for f in ogre_files:
		p = subprocess.Popen((upgrader, f))
		p.wait()
		p = subprocess.Popen((converter, f))
		p.wait()
	
	convert_xml_to_json(file_name)




def convert_xml_to_json(filename):

	tree = ET.parse(full_name(filename + '.mesh.xml'))
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
	print('Export >>>>> ' + output_file)


def _parse_materials(filename):
	materials = {}
	material = None
	file = open(full_name(filename + '.material'), 'r')
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
		elif l.startswith('texture_unit'):
			pass
		elif l.startswith('texture'):
			material['texture'] = l.replace('texture', '').strip().lower().replace('.dds', '.png')
			_convert_texture(material['texture'])
	file.close()
	return materials

# maybe : no work on windows 64-bit
# http://nullege.com/codes/show/src%40p%40i%40pilgrim-HEAD%40pilgrim%40codecs%40__init__.py/9/dds.DDS/python
# http://freeimage.sourceforge.net/download.html
def _convert_texture(filename):
	return
	filename = full_name(filename)
	name, extension = os.path.splitext(filename.lower())
	dds_filename = full_name(name + '.dds')
	if os.path.exists(dds_filename):
		import pyglet
		texture = pyglet.image.load(dds_filename)
		texture.get_texture().save(dds_filename.replace('.dds', '.png'))


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

	bones_assignments_xml = xml.find('boneassignments')
	if bones_assignments_xml is not None:
		mesh['boneassignments'] = _parse_bones_assignments(bones_assignments_xml)

	
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
	geometry['vertexcount'] = int(xml.attrib['vertexcount'])
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

		# def _parse_xyz(target, source):
		# 	target.append(float(source.attrib['x']))
		# 	target.append(float(source.attrib['y']))
		# 	target.append(float(source.attrib['z']))

		# def _parse_uv(target, source):
		# 	target.append(float(source.attrib['u']))
		# 	target.append(float(source.attrib['v']))

		# tmp_list = []
		# for e in vertex:
		# 	if has_position:
		# 		_parse_xyz(tmp_list, e.find('position'))
		# 	if has_normal:
		# 		_parse_xyz(tmp_list, e.find('normal'))
		# 	if has_texcoord:
		# 		_parse_uv(tmp_list, e.find('texcoord'))

	return geometry


def _parse_faces(xml):
	faces_xml = xml.findall('./face')
	tmp_list = []
	for e in faces_xml:
		tmp_list.append(int(e.attrib['v1']))
		tmp_list.append(int(e.attrib['v2']))
		tmp_list.append(int(e.attrib['v3']))
	return tmp_list


def _parse_bones_assignments(xml):
	bones_xml = xml.findall('./vertexboneassignment')
	tmp_list = []
	for e in bones_xml:
		tmp_list.append(int(e.attrib['vertexindex']))
		tmp_list.append(int(e.attrib['boneindex']))
		tmp_list.append(float(e.attrib['weight']))
	return tmp_list


def _parse_skeleton(filename):
	skeleton_xml = ET.parse(full_name(filename + '.xml')).getroot()
	
	skeleton = {}
	if 'blendmode' in skeleton_xml.attrib:
		skeleton['blendmode'] = skeleton_xml.attrib['blendmode']

	# bind pose
	joints = []
	joints_map = {}
	joints_xml = skeleton_xml.findall('./bones/bone')
	for e in joints_xml:
		joint = {}
		joint['id'] = int(e.attrib['id'])
		joint['name'] = e.attrib['name']
		joint['position'] = []
		
		pos = e.find('position')
		joint['position'].append(float(pos.attrib['x']))
		joint['position'].append(float(pos.attrib['y']))
		joint['position'].append(float(pos.attrib['z']))

		rot = e.find('rotation')
		axis = rot.find('axis')
		joint['rotation'] = {
			'angle': float(rot.attrib['angle']),
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

	convert_mesh_to_xml('./BOSS_STURM/BOSS_STURM.MESH')
	# convert_mesh_to_xml('./ALRIC/ALRIC.MESH')
