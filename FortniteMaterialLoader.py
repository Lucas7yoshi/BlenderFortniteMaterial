import bpy
import os
from mathutils import Vector

#inputs, configure it here
#You can shift right click a selected folder/file in windows explorer 
#and click "copy as path" and put it in the correct paths (after the r)

#Enter the path to the .mat file for the textures, make sure you copy the .mat file
#into the same folder as all the textures!
DotMatPath = r"E:\Downloads\umodel latest\UmodelExport\Game\Characters\Enemies\Cattus\Textures\MI_IceCliff_01_Cattus.mat"

outputMaterialName = "" # Change to just "" to make the material be named the same as the .mat file

ApplyMaterialToCurrentlySelectedObject = False # read the variable lol, disable if object has multiple materials and apply manually from shading tab
#END INPUTS, DO NOT TOUCH ANY CODE BELOW

# make the material
if not outputMaterialName:
    outputMaterialName = os.path.basename(DotMatPath)

mat = bpy.data.materials.new(name=outputMaterialName)
mat.use_nodes = True
materialOutput = mat.node_tree.nodes.get('Material Output')
principleBSDF = mat.node_tree.nodes.get('Principled BSDF')
mat.node_tree.links.remove(principleBSDF.outputs[0].links[0]) # remove inital link

addShader = mat.node_tree.nodes.new("ShaderNodeAddShader")
mat.node_tree.links.new(principleBSDF.outputs[0], addShader.inputs[0])
mat.node_tree.links.new(addShader.outputs[0], materialOutput.inputs[0])
addShader.location = Vector((400, -250))
materialOutput.location = Vector((650, -250))

textureBasePath = os.path.dirname(DotMatPath)

with open(DotMatPath) as f:
    for l in f:
        line = l.rstrip()
        if line.startswith("Diffuse="):
            diffuseImgPath = textureBasePath + r"/" + line.replace("Diffuse=", "") + ".tga"
            print(diffuseImgPath)
            #diffuse texture
            diffuseTex = mat.node_tree.nodes.new("ShaderNodeTexImage")
            diffuseImg = bpy.data.images.load(filepath = diffuseImgPath)
            diffuseTex.image = diffuseImg
            diffuseTex.location = Vector((-400,450))
            #diffuseTex.hide = True
            #connect diffuseTexture to principle
            mat.node_tree.links.new(diffuseTex.outputs[0], principleBSDF.inputs[0])
            #diffuse end
        elif line.startswith("Normal="):
            normalImgPath = textureBasePath + r"/" + line.replace("Normal=", "") + ".tga"
            print(normalImgPath)
            #normal begin
            normY = -125

            normTex = mat.node_tree.nodes.new("ShaderNodeTexImage")
            normCurve = mat.node_tree.nodes.new("ShaderNodeRGBCurve")
            normMap = mat.node_tree.nodes.new("ShaderNodeNormalMap")
            normImage = bpy.data.images.load(filepath = normalImgPath)
            #location crap
            normTex.location = Vector((-800, normY))
            normCurve.location = Vector((-500, normY))
            normMap.location = Vector((-200, normY))

            normImage.colorspace_settings.name = 'Non-Color'
            normTex.image = normImage
            #normTex.hide = True
            #setup rgb curve
            normCurve.mapping.curves[1].points[0].location = (0,1)
            normCurve.mapping.curves[1].points[1].location = (1,0)
            #connect everything
            mat.node_tree.links.new(normTex.outputs[0], normCurve.inputs[1])
            mat.node_tree.links.new(normCurve.outputs[0], normMap.inputs[1])
            mat.node_tree.links.new(normMap.outputs[0], principleBSDF.inputs['Normal'])
            #normal end
        elif line.startswith("Specular="):
            specularImgPath = textureBasePath + r"/" + line.replace("Specular=", "") + ".tga"
            print (specularImgPath)
            #specular start
            specY = 140

            specTex = mat.node_tree.nodes.new("ShaderNodeTexImage")

            specSeperateRGB = mat.node_tree.nodes.new("ShaderNodeSeparateRGB")
            specSeperateRGB.location = Vector((-250, specY))
            #specSeperateRGB.hide = True

            specImage = bpy.data.images.load(filepath = specularImgPath)
            specImage.colorspace_settings.name = 'Non-Color'

            specTex.image = specImage
            specTex.location = Vector((-600, specY))
            #specTex.hide = True
            #connect spec texture to rgb split
            mat.node_tree.links.new(specTex.outputs[0], specSeperateRGB.inputs[0])
            #connect rgb splits to principle
            mat.node_tree.links.new(specSeperateRGB.outputs[0], principleBSDF.inputs['Specular'])
            mat.node_tree.links.new(specSeperateRGB.outputs[1], principleBSDF.inputs['Metallic'])
            mat.node_tree.links.new(specSeperateRGB.outputs[2], principleBSDF.inputs['Roughness'])
            #specular end
        elif line.startswith("Emissive="):
            emissiveImgPath = textureBasePath + r"/" + line.replace("Emissive=", "") + ".tga"
            print (emissiveImgPath)
            #emission start
            emiTex = mat.node_tree.nodes.new("ShaderNodeTexImage")
            emiShader = mat.node_tree.nodes.new("ShaderNodeEmission")
            emiImage = bpy.data.images.load(filepath = emissiveImgPath)
            emiTex.image = emiImage
            #emission - location
            emiTex.location = Vector((-200, -425))
            emiShader.location = Vector((100, -425))
            #connecting
            mat.node_tree.links.new(emiTex.outputs[0], emiShader.inputs[0])
            mat.node_tree.links.new(emiShader.outputs[0], addShader.inputs[1])

            #emission end           

            
           #ending stuff
if ApplyMaterialToCurrentlySelectedObject:
    bpy.context.active_object.data.materials[0] = mat
