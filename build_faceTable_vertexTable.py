import meshio
import numpy as np
# import math
from helpers import *

surface_triangles, surface_quads, surface_points = read_surface("./testGeometries/sphere.obj")
d1 = 0.1
d2 = 0.12
level1, level2, level3 = build_ref_mesh_points(surface_points, surface_triangles, surface_quads, d1, d2, 1)
nSurfacePoints = len(surface_points)
level1_triangles = surface_triangles
level1_quads = surface_quads
level2_triangles = level1_triangles + nSurfacePoints
level2_quads = level1_quads + nSurfacePoints
level3_triangles = level2_triangles + nSurfacePoints
level3_quads = level2_quads + nSurfacePoints
allPoints = np.concatenate((level1, level2, level3))

######################################################################

#build face normal table
# | face index | quad or tri (4 for quad, 3 for tri) | point indices (4 entries, if triangle then last entry is -1) | face normal, not normalized (3 entries) |

nFaces = len(level1_triangles) + len(level1_quads)
faceTable = np.ndarray((nFaces,9),dtype = object)
for i in range(nFaces):
    faceTable[i, 0] = int(i)

for i, cell in enumerate(level1_triangles):
    faceTable[i, 1] = 3
    faceTable[i, 2:5] = cell
    faceTable[i, 5] = -1
    pointCoor = np.array([level1[cell[0]], level1[cell[1]], level1[cell[2]]])

    faceTable[i, 6:9] = getAbsNormals(pointCoor)

for i, cell in enumerate(level1_quads):
    faceTable[i + len(level1_triangles), 1] = 4
    faceTable[i + len(level1_triangles), 2:6] = cell
    pointCoor = np.array([level1[cell[0]], level1[cell[1]], level1[cell[2]], level1[cell[3]]])
    faceTable[i + len(level1_triangles), 6:9] = getAbsNormals(pointCoor)

#############################################################################

#build vertex table:
# | point index (entry 0) | point coordinates (entries 1,2,3) | number of faces attached (entry 4) | face indices of attached faces (entries 5, 6, 7...) |

vertexIndex = np.ndarray((nSurfacePoints, 1), dtype = object)
for i in range(nSurfacePoints):
    vertexIndex[i] = i

vertexTable = np.append(vertexIndex, level1, axis=1)

neighbourFaces = []
nNeighbourFaces = np.ndarray((nSurfacePoints, 1), dtype = object)
for P in range(nSurfacePoints):
    neighbourFacesTemp = []
    for j in range(nFaces):
        if P in faceTable[j, 2:6]:
            neighbourFacesTemp.append(j)

    nNeighbourFaces[P] = len(neighbourFacesTemp)
    neighbourFaces.append(neighbourFacesTemp)

vertexTable = np.append(vertexTable, nNeighbourFaces, axis=1)

maxNeighbours = len(max(neighbourFaces, key=len))

for i, neighbours in enumerate(neighbourFaces):
    j = len(neighbours)
    k = maxNeighbours - j
    if k > 0:
        for l in range(k):
            neighbourFaces[i].append(-1)
neighbourFaces = np.array(neighbourFaces)
vertexTable = np.append(vertexTable, neighbourFaces, axis=1)

################################################################

# add vertex normals to to vertex table
allVNormals = np.zeros((nSurfacePoints, 3), dtype = object)
for v in range(nSurfacePoints):
    vNormal = np.zeros((1, 3), dtype = object)

    nF = vertexTable[v, 4]

    for f in range(nF):
        vNormal += faceTable[vertexTable[v, 5 + f], 6:9]

    norm = np.linalg.norm(vNormal)
    vNormal = vNormal / norm

    allVNormals[v, :] = vNormal
vertexTable = np.insert(vertexTable, [4], allVNormals, axis=1)

#####################################

#build level 2 faceTable | not complete, need to update face normals
level2FaceTable = faceTable.copy()
level2FaceTable[:, 0] += nFaces
for f in range(nFaces):
    if level2FaceTable[f, 1] == 3:
        level2FaceTable[f, [2, 3, 4]] += nSurfacePoints
    elif level2FaceTable[f, 1] == 4:
        level2FaceTable[f, [2, 3, 4, 5]] += nSurfacePoints

######################################

#build level2 vertex table | incomplete, need to update vertex normals
level2VertexTable = vertexTable.copy()
level2VertexTable[:, 0] += nSurfacePoints
for v in range(nSurfacePoints):
    level2VertexTable[v, 8:(level2VertexTable[v, 7] - maxNeighbours)] += nFaces
    level2VertexTable[v, [1, 2, 3]] = level2[v, :]

#######################################

#update level 2 face table normals
for f in range(nFaces):
    if faceTable[f, 1] == 3:
        pointCoor = np.array([level2[faceTable[f, 2]], level2[faceTable[f, 3]], level2[faceTable[f, 4]]])
    elif faceTable[f, 1] == 4:
        pointCoor = np.array([level2[faceTable[f, 2]], level2[faceTable[f, 3]], level2[faceTable[f, 4]], level2[faceTable[f, 5]]])
    level2FaceTable[f, [6, 7, 8]] = getAbsNormals(pointCoor)

#######################################

# update level2 vertex table vertex normals
for v in range(nSurfacePoints):
    vNormal = np.zeros((1, 3), dtype = object)
    nF = vertexTable[v, 7]
    for f in range(nF):
        vNormal += level2FaceTable[vertexTable[v, 8 + f], 6:9]
    norm = np.linalg.norm(vNormal)
    vNormal = vNormal / norm
    level2VertexTable[v, [4, 5, 6]] = vNormal


#######################################

# np.save('./dataOutput/faceTable.npy', faceTable)
# np.save('./dataOutput/level2FaceTable.npy', level2FaceTable)
# np.save('./dataOutput/vertexTable.npy', vertexTable)
# np.save('./dataOutput/level2VertexTable.npy', level2VertexTable)
