import subprocess
import json
import os
import glob
import sys
import xml.etree.ElementTree as ET

version = '0.1'
file_extension = '.orange'

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

	skeleton_files = []
	ogre_files = []
	for f in os.listdir(dir_name):
		if f.lower().endswith(".skeleton"):
			skeleton_files.append(full_name(f))
	# mesh file
	ogre_files = [f for f in skeleton_files]
	ogre_files.append(os.path.abspath(name))

	try:
		for f in ogre_files:
			break
			p = subprocess.Popen((upgrader, f))
			p.wait()
			p = subprocess.Popen((converter, f))
			p.wait()
	except Exception as e:
		pass
	finally:
		convert_xml_to_json(file_name, skeleton_files)




def convert_xml_to_json(mesh_filename, skeleton_files):

	tree = ET.parse(full_name(mesh_filename + '.mesh.xml'))
	xml_root = tree.getroot()

	# parse materials
	materials = _parse_materials(mesh_filename)

	# parse meshes
	mesh_root = _parse_mesh(xml_root)

	# parse animations
	animations = []
	for f in skeleton_files:
		skeleton = _parse_skeleton(f)
		if 'animation' in skeleton:
			animations.append(skeleton)

	orange_model = {
		'version': version,
		'materials': materials,
		'mesh': mesh_root,
		'animations': animations
	}

	model_json = json.dumps(orange_model)
	output_file = mesh_filename.lower() + file_extension
	f = open(output_file, 'w')
	f.write(model_json)
	f.close()
	print('export model >>>>> ' + output_file)



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
	if bones_assignments_xml is not None and len(bones_assignments_xml) > 0:
		(joint_indices, joint_weights) = _parse_bones_assignments(bones_assignments_xml)
		mesh['jointindices'] = joint_indices
		mesh['jointweights'] = joint_weights

	
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

	return geometry


def _parse_faces(xml):
	faces_xml = xml.findall('./face')
	tmp_list = []
	for e in faces_xml:
		tmp_list.append(int(e.attrib['v1']))
		tmp_list.append(int(e.attrib['v2']))
		tmp_list.append(int(e.attrib['v3']))
	return tmp_list


# http://www.ogre3d.org/docs/manual/manual_46.html
def _parse_bones_assignments(xml):
	bones_xml = xml.findall('./vertexboneassignment')

	joint_indices = []
	joint_weights = []

	bone_assignments = []
	last_vertex = -1
	vertex_index = -1
	
	for e in bones_xml:
		
		vertex_index = int(e.attrib['vertexindex'])
		bone_index = int(e.attrib['boneindex'])
		weight = float(e.attrib['weight'])

		if last_vertex != -1 and last_vertex != vertex_index:
			# normalize, only 4 joints be apply to per vertex
			indices, weights = _normalize_joint_weights(bone_assignments, last_vertex)
			joint_indices = joint_indices + indices
			joint_weights = joint_weights + weights
			# clear 
			bone_assignments = []
		
		last_vertex = vertex_index
		bone_assignments.append({'vertex': vertex_index, 'bone': bone_index, 'weight': weight})

	indices, weights = _normalize_joint_weights(bone_assignments, vertex_index)
	joint_indices = joint_indices + indices
	joint_weights = joint_weights + weights

	return (joint_indices, joint_weights)

# normalize, only 4 joints be apply to per vertex
def _normalize_joint_weights(bone_assignments, vertex_index):
	joint_indices = []
	joint_weights = []

	l = len(bone_assignments)
	if l > 4:
		list.sort(bone_assignments, key = lambda item: item["weight"], reverse = True)
	elif l < 4:
		for x in range(4 - l):
			bone_assignments.append({'vertex': vertex_index, 'bone': 0, 'weight': 0.0})
	
	total_weight = 0.0;
	for x in range(4):
		j = bone_assignments[x]
		total_weight += j['weight']

	adjust_weight = 0.0
	if total_weight < 1.0:
		adjust_weight = (1.0 - total_weight) / 4

	for x in range(4):
		j = bone_assignments[x]
		joint_indices.append(j['bone'])
		joint_weights.append(j['weight'] + adjust_weight)

	return (joint_indices, joint_weights)



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
		
		joint['parent'] = -1
		joints.append(joint)
		joints_map[joint['name']] = joint
	skeleton['joints'] = joints

	# hierarchy of joints
	hierarchy_xml = skeleton_xml.findall('./bonehierarchy/boneparent')
	for e in hierarchy_xml:
		name = e.attrib['bone']
		parent = e.attrib['parent']
		joint = joints_map[name]
		joint['parent'] = joints_map[parent]['id']

	skeleton['name'] = os.path.basename(filename).lower().replace('.skeleton', '')
	animations = skeleton_xml.find('./animations')
	animation = None
	if animations is not None and len(animations) > 0:
		animation_xml = animations[0]
		animation = {}
		if 'name' in animation_xml.attrib:
			skeleton['name'] = animation_xml.attrib['name']
			animation['name'] = animation_xml.attrib['name']
		if 'length' in animation_xml.attrib:
			animation['length'] = float(animation_xml.attrib['length'])

		tracks = []
		tracks_xml = animation_xml.findall('./tracks/track')
		if tracks_xml is not None and len(tracks_xml) > 0:
			for track_xml in tracks_xml:
				track = {}
				joint_name = track_xml.attrib['bone']
				track['joint'] = joints_map[joint_name]['id']
				track['keyframes'] = []
				keyframes = []
				keyframes_xml = track_xml.findall('./keyframes/keyframe')
				for keyframe_xml in keyframes_xml:
					keyframe = {}
					keyframe['time'] = float(keyframe_xml.attrib['time'])

					translate_xml = keyframe_xml.find('translate')
					keyframe['translate'] = []
					keyframe['translate'].append(float(translate_xml.attrib['x']))
					keyframe['translate'].append(float(translate_xml.attrib['y']))
					keyframe['translate'].append(float(translate_xml.attrib['z']))

					rotate_xml = keyframe_xml.find('rotate')
					keyframe['rotate'] = {}
					keyframe['rotate']['angle'] = float(rotate_xml.attrib['angle'])
					keyframe['rotate']['axis'] = []
					axis_xml = rotate_xml.find('axis')
					keyframe['rotate']['axis'].append(float(axis_xml.attrib['x']))
					keyframe['rotate']['axis'].append(float(axis_xml.attrib['y']))
					keyframe['rotate']['axis'].append(float(axis_xml.attrib['z']))

					keyframes.append(keyframe)

				track['keyframes'] = keyframes
				tracks.append(track)
			animation['tracks'] = tracks
	if animation is not None and 'tracks' in animation and len(animation['tracks']) > 0:
		skeleton['animation'] = animation
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

	# convert_mesh_to_xml('./BOSS_STURM/BOSS_STURM.MESH')
	convert_mesh_to_xml('./ALRIC/ALRIC.MESH')


