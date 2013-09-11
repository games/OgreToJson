package threeshooter {
	import flash.utils.Dictionary;
	
	import mx.utils.StringUtil;

	public class Parser {

		/**
		 *
		 * @param meshXml
		 * @return
		 *
		 * var mesh = {
		 * 	 geometry : {
		 * 		vertexcount : int,
		 *      vertices : [x, y, z ...],
		 *      normals : [x, y, z ...],
		 *      texturecoords : [u, v ...]
		 *   },
		 *
		 *   submeshes : [
		 *     {
		 * 		  material: {
		 * 			name: String,
		 * 			texture: String,
		 * 			ambient: [],
		 * 			specular: [],
		 * 			diffuse: [],
		 * 			emissive: []
		 * 		  },
		 * 		  faces : [v1, v2, v3 ...]
		 *     },
		 * 	   ...
		 *   ]
		 * }
		 *
		 */
		public static function parseMesh(meshXml:XML, materials:Dictionary):Object {

			var mesh:Object = {};
			mesh.geometry = {};
			mesh.geometry.vertexcount = int(meshXml.sharedgeometry.@vertexcount);
			mesh.geometry.vertices = [];
			mesh.geometry.normals = [];

			var vertexBuffers:XMLList = meshXml.sharedgeometry.vertexbuffer;
			var vertexBuffer:XML;
			if (vertexBuffers.length() > 0) {
				vertexBuffer = vertexBuffers[0];
				for each (var vertex:XML in vertexBuffer.vertex) {
					mesh.geometry.vertices.push(Number(vertex.position.@x));
					mesh.geometry.vertices.push(Number(vertex.position.@y));
					mesh.geometry.vertices.push(Number(vertex.position.@z));
					mesh.geometry.normals.push(Number(vertex.normal.@x));
					mesh.geometry.normals.push(Number(vertex.normal.@y));
					mesh.geometry.normals.push(Number(vertex.normal.@z));
				}
			}

			mesh.geometry.texturecoords = [];
			if (vertexBuffers.length() > 1) {
				vertexBuffer = vertexBuffers[1];
				for each (var uv:XML in vertexBuffer.vertex) {
					mesh.geometry.texturecoords.push(Number(uv.texcoord.@u));
					mesh.geometry.texturecoords.push(Number(uv.texcoord.@v));
				}
			}

			mesh.submeshes = [];
			var subMeshes:XMLList = meshXml.submeshes;
			for each (var submesh:XML in subMeshes.submesh) {
				var submeshObj:Object = {material: materials[String(submesh.@material)]};
				submeshObj.faces = [];
				for each (var face:XML in submesh.faces.face) {
					submeshObj.faces.push(Number(face.@v1));
					submeshObj.faces.push(Number(face.@v2));
					submeshObj.faces.push(Number(face.@v3));
				}
				mesh.submeshes.push(submeshObj);
			}

			return mesh;
		}

		public static function parseMaterials(source:String):Dictionary {
			var materials:Dictionary = new Dictionary();
			var material:Object;
			var lines:Array = source.split("\n");
			for each (var line:String in lines) {
				line = StringUtil.trim(line);
				if (line.indexOf("material") == 0) {
					material = {};
					material.name = StringUtil.trim(line.replace("material", ""));
					materials[material.name] = material;
				} else if (line.indexOf("ambient") == 0) {
					material.ambient = parseArray(line.replace("ambient", ""), 3);
				} else if (line.indexOf("diffuse") == 0) {
					material.diffuse = parseArray(line.replace("diffuse", ""), 3);
				} else if (line.indexOf("specular") == 0) {
					material.specular = parseArray(line.replace("specular", ""), 4);
				} else if (line.indexOf("emissive") == 0) {
					material.emissive = parseArray(line.replace("emissive", ""), 3);
				} else if (line.indexOf("texture ") == 0) {
					material.texture = StringUtil.trim(line.replace("texture", ""));
				}
			}
			return materials;
		}
		
		

		private static function parseArray(src:String, count:int):Array {
			var arr:Array = StringUtil.trim(src).split(" ");
			var result:Array = [];
			for (var i:int = 0; i < count; i++) {
				result.push(Number(arr[i]));
			}
			return result;
		}
	}
}





















