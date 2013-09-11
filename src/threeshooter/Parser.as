package threeshooter {

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
		 * 		  material: string,
		 * 		  faces : [v1, v2, v3 ...] 
		 *     },
		 * 	   ...
		 *   ]
		 * }
		 * 
		 */		
		public static function parseMesh(meshXml:XML):Object {
			
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
				var submeshObj:Object = {material: String(submesh.@material)};
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
	}
}
