import json
import os



def convert(filename):
	file = open(filename + '.obj')
	vertices = []
	faces = []
	for line in file.readlines():
		parts = line.split(' ')
		if len(parts) == 4:
			if parts[0] == 'v':
				vertices.append(float(parts[1]))
				vertices.append(float(parts[2]))
				vertices.append(float(parts[3]))
			elif parts[0] == 'f':
				faces.append(float(parts[1]) - 1.0)
				faces.append(float(parts[2]) - 1.0)
				faces.append(float(parts[3]) - 1.0)
		else:
			print parts
	file.close()

	mesh = {
		'sharedgeometry' : {
			'vertexcount' : len(vertices),
			'vertices' : vertices,
			'normals' : [],
			'texturecoords' : [],
			'material' : {
				'texture': '',
				'ambient': [1.0, 1.0, 1.0],
				'diffuse': [1.0, 1.0, 1.0],
				'specular': [1.0, 1.0, 1.0, 1.0],
				'emissive': [0.0, 0.0, 0.0]
			}
		},
		'submeshes' : [],
		'faces' : faces
	}

	print(str(len(vertices)) + ', ' + str(len(faces)))

	mesh_json = json.dumps(mesh)
	output_file = filename.lower() + '.json'
	f = open(output_file, 'w')
	f.write(mesh_json)
	f.close()
	print 'Export >>>>> ' + output_file



if __name__ == "__main__":
	convert('teapot')
