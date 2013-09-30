import json
import os

def new_mesh(faces):
	return {
		'usesharedvertices': True,
		'submeshes' : [],
		'faces' : faces
	}

def convert(filename):
	file = open(filename + '.obj')

	vertices = []
	faces = []
	normals = []
	texturecoords = []
	read_vertex_end = False

	mesh_list = []

	lines = file.readlines()
	file.close()

	lines_parts = []
	# # read all vertices
	for line in lines:
		parts = line.split()
		if len(parts) == 0:
			continue
		if parts[0] == 'v':
			vertices.append(float(parts[1]))
			vertices.append(float(parts[2]))
			vertices.append(float(parts[3]))
		lines_parts.append(parts)

	# # read all normals
	all_normals = []
	for parts in lines_parts:
		if parts[0] == 'vn':
			all_normals.append(float(parts[1]))
			all_normals.append(float(parts[2]))
			all_normals.append(float(parts[3]))
	normals = list(all_normals)


	for line in lines:
		parts = line.split()
		if len(parts) > 0:
			# print parts
			if parts[0] == 'v':
				if read_vertex_end:
					mesh_list.append(new_mesh(faces))
					faces = []
					read_vertex_end = False
				# vertices.append(float(parts[1]))
				# vertices.append(float(parts[2]))
				# vertices.append(float(parts[3]))
			elif parts[0] == 'f':
				read_vertex_end = True
				
				faces_part1 = parts[1].split('/')
				faces_part2 = parts[2].split('/')
				faces_part3 = parts[3].split('/')

				faces.append(float(faces_part1[0]) - 1.0)
				faces.append(float(faces_part2[0]) - 1.0)
				faces.append(float(faces_part3[0]) - 1.0)

				normals[int(faces_part1[0]) - 1] = all_normals[int(faces_part1[2]) - 1]
				normals[int(faces_part2[0]) - 1] = all_normals[int(faces_part2[2]) - 1]
				normals[int(faces_part3[0]) - 1] = all_normals[int(faces_part3[2]) - 1]

			# elif parts[0] == 'vn':
			# 	normals.append(float(parts[1]))
			# 	normals.append(float(parts[2]))
			# 	normals.append(float(parts[3]))
			elif parts[0] == 'vt':
				texturecoords.append(float(parts[1]))
				texturecoords.append(float(parts[2]))

	mesh = None
	if len(mesh_list) == 1:
		mesh = mesh_list[0]
		mesh['geometry'] = {
			'vertexcount' : len(vertices),
			'vertices' : vertices,
			'normals' : normals,
			'texturecoords' : texturecoords
		}
		mesh['material'] = {
			'texture': '',
			'ambient': [1.0, 1.0, 1.0],
			'diffuse': [1.0, 1.0, 1.0],
			'specular': [1.0, 1.0, 1.0, 1.0],
			'emissive': [0.0, 0.0, 0.0]
		}
		del mesh['usesharedvertices']
	else:
		mesh = {
			'sharedgeometry' : {
				'vertexcount' : len(vertices),
				'vertices' : vertices,
				'normals' : normals,
				'texturecoords' : texturecoords
			},
			'material' : {
				'texture': '',
				'ambient': [1.0, 1.0, 1.0],
				'diffuse': [1.0, 1.0, 1.0],
				'specular': [1.0, 1.0, 1.0, 1.0],
				'emissive': [0.0, 0.0, 0.0]
			},
			'submeshes' : mesh_list
		}

	mesh_json = json.dumps(mesh)
	output_file = filename.lower() + '.json'
	f = open(output_file, 'w')
	f.write(mesh_json)
	f.close()
	print 'Export >>>>> ' + output_file



if __name__ == "__main__":
	convert('mm02')
