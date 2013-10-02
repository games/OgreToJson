import json
import os

def new_mesh(faces):
	return {
		'usesharedvertices': True,
		'faces' : faces
	}

def new_material():
	return {
		'texture': '',
		'ambient': [1.0, 1.0, 1.0],
		'diffuse': [1.0, 1.0, 1.0],
		'specular': [1.0, 1.0, 1.0, 1.0],
		'emissive': [0.0, 0.0, 0.0]
	}

def new_geometry(vertices, normals, texturecoords):
	return {
		'vertexcount' : len(vertices),
		'vertices' : vertices,
		'normals' : normals,
		'texturecoords' : texturecoords
	}

def convert(filename):
	vertices = []
	faces = []
	texturecoords = []
	mesh_list = []

	read_vertex_end = False

	file = open(filename + '.obj')
	lines = file.readlines()
	file.close()

	all_normals = []

	# # read all vertices
	line_parts = []
	for line in lines:
		parts = line.split()
		if len(parts) == 0:
			continue
		line_parts.append(parts)
		if parts[0] == 'v':
			vertices.append(float(parts[1]))
			vertices.append(float(parts[2]))
			vertices.append(float(parts[3]))
		elif parts[0] == 'vn':
			all_normals.append([float(parts[1]), float(parts[2]), float(parts[3])])
	normals = range(0, len(vertices))


	for parts in line_parts:
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

			v0 = int(faces_part1[0]) - 1
			v1 = int(faces_part2[0]) - 1
			v2 = int(faces_part3[0]) - 1

			n0 = int(faces_part1[2]) - 1
			n1 = int(faces_part2[2]) - 1
			n2 = int(faces_part3[2]) - 1

			faces.append(v0)
			faces.append(v1)
			faces.append(v2)

			def set_normals(v, n):
				start = v * 3
				no = all_normals[n]
				normals[start] = no[0]
				normals[start + 1] = no[1]
				normals[start + 2] = no[2]

			set_normals(v0, n0)
			set_normals(v1, n1)
			set_normals(v2, n2)

		# elif parts[0] == 'vn':
		# 	normals.append(float(parts[1]))
		# 	normals.append(float(parts[2]))
		# 	normals.append(float(parts[3]))
		elif parts[0] == 'vt':
			texturecoords.append(float(parts[1]))
			texturecoords.append(float(parts[2]))

	if len(faces) > 0:
		mesh_list.append(new_mesh(faces))
		faces = []

	mesh = None
	if len(mesh_list) == 1:
		mesh = mesh_list[0]
		mesh['geometry'] = new_geometry(vertices, normals, texturecoords)
		mesh['material'] = new_material()
		del mesh['usesharedvertices']
	else:
		mesh = {
			'sharedgeometry' : new_geometry(vertices, normals, texturecoords),
			'material' : new_material(),
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
