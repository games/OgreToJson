import json
import os

def new_mesh(vertices, normals, texturecoords, faces):
	return {
		'geometry' : {
			'vertexcount' : len(vertices),
			'vertices' : vertices,
			'normals' : normals,
			'texturecoords' : texturecoords,
			'material' : {
				'texture': '',
				'ambient': [1.0, 1.0, 1.0],
				'diffuse': [1.0, 1.0, 1.0],
				'specular': [1.0, 1.0, 1.0, 1.0],
				'emissive': [0.0, 0.0, 0.0]
			}
		},
		'usesharedvertices': False,
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

	for line in lines:
		parts = line.split()
		if len(parts) > 0:
			# print parts
			if parts[0] == 'v':
				if read_vertex_end:
					mesh_list.append(new_mesh(vertices, normals, texturecoords, faces))
					vertices = []
					normals = []
					texturecoords = []
					faces = []
					read_vertex_end = False
				vertices.append(float(parts[1]))
				vertices.append(float(parts[2]))
				vertices.append(float(parts[3]))
			elif parts[0] == 'f':
				read_vertex_end = True

				faces.append(float(parts[1].split('/')[0]) - 1.0)
				faces.append(float(parts[2].split('/')[0]) - 1.0)
				faces.append(float(parts[3].split('/')[0]) - 1.0)
			elif parts[0] == 'vn':
				normals.append(float(parts[1]))
				normals.append(float(parts[2]))
				normals.append(float(parts[3]))
			elif parts[0] == 'vt':
				texturecoords.append(float(parts[1]))
				texturecoords.append(float(parts[2]))

	mesh = None
	if len(mesh_list) == 1:
		mesh = mesh_list[0]
	else:
		mesh = {
			'sharedgeometry' : None,
			'submeshes' : mesh_list,
			'faces' : []
		}

	mesh_json = json.dumps(mesh)
	output_file = filename.lower() + '.json'
	f = open(output_file, 'w')
	f.write(mesh_json)
	f.close()
	print 'Export >>>>> ' + output_file



if __name__ == "__main__":
	convert('mm')
