structure
===================


```
{
  materials : {
    material_name : {
        texture : url,
        name : material_name,
        <<parameters ...>>
    },
    ...
  },
  
  mesh : {
    jointweights : [w00, w01, w02, w03, ...],
    jointindices : [i00, i01, i02, i03, ...],
    skeleton : {
        joints :[{
            name : '', 
            position : [v0, v1, v2, v3],
            rotation: angle, axis,
            id,
            parent
        },
        ...
        ]
    },
    geometry : {
        normals, texturecoords, positions, vertexcount
    },
    submeshes : [<same as mesh> ...]
  }

}
```
