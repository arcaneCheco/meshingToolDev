import meshio
import numpy as np
# import pickle
# from helpers import *
# from helpers import centroid, read_surface, get_face_normals, area, hex_contains, root_neighbour, bounding_box, triInBox
# import helpers
# import config

########################################################################

def centroid(vertexes):
     _x_list = [vertex [0] for vertex in vertexes]
     _y_list = [vertex [1] for vertex in vertexes]
     _z_list = [vertex [2] for vertex in vertexes]
     _len = len(vertexes)
     _x = sum(_x_list) / _len
     _y = sum(_y_list) / _len
     _z = sum(_z_list) / _len
     return(_x, _y, _z)

def read_surface(surfaceFile):
    ## write triangle cells, quad cells and surface points in numpy arrays ##
    surfaceMesh = meshio.read(surfaceFile)

    ##get cells##
    triangle_cells = np.array([])
    quad_cells = np.array([])
    for cell in surfaceMesh.cells:
        if cell.type == "triangle":
            if triangle_cells.size == 0:
                triangle_cells = cell.data
            else:
                triangle_cells = np.concatenate((triangle_cells, cell.data))
            # print(cell.data)
        elif cell.type == "quad":
            if quad_cells.size == 0:
                quad_cells = cell.data
            else:
                quad_cells = np.concatenate((quad_cells, cell.data))

    ##get surface points##
    surfacePoints = surfaceMesh.points

    return triangle_cells, quad_cells, surfacePoints

def get_face_normals(points, triangles, quads):
    # build face normals
    triNormal = np.ndarray((len(triangles), 3), dtype = np.float64)
    quadNormal = np.ndarray((len(quads), 3), dtype = np.float64)
    for i, triFace in enumerate(triangles):
        coor = points[triFace, :]
        triNormal[i, :] = np.cross(coor[1] - coor[0], coor[2] - coor[0])
    for i, quadFace in enumerate(quads):
        coor = points[quadFace, :]
        quadNormal[i, :] = np.cross(coor[1] - coor[0], coor[2] - coor[0])
    # normalize
    triNormal = triNormal / np.linalg.norm(triNormal, axis = 1)[: , None]
    quadNormal = quadNormal / np.linalg.norm(quadNormal, axis = 1)[: , None]

    return triNormal, quadNormal

#area of polygon poly
def area(poly, unitNormal):
    if len(poly) < 3: # not a plane - no area
        return 0

    total = [0, 0, 0]
    for i in range(len(poly)):
        vi1 = poly[i]
        if i is len(poly)-1:
            vi2 = poly[0]
        else:
            vi2 = poly[i+1]
        prod = np.cross(vi1, vi2)
        total[0] += prod[0]
        total[1] += prod[1]
        total[2] += prod[2]
    result = np.dot(total, unitNormal)
    return abs(result/2)

def hex_contains(hex_points, x): # points need to satisfy certain order
    # n1 = np.cross(hex_points[1] - hex_points[0], hex_points[2] - hex_points[0])
    n1 = np.array([0, 0, 1])
    x1 = np.dot(x - hex_points[0], n1)
    if x1 < 0:
        return False
    # n2 = np.cross(hex_points[7] - hex_points[4], hex_points[6] - hex_points[4])
    n2 = np.array([0, 0, -1])
    x2 = np.dot(x - hex_points[4], n2)
    if x2 < 0:
        return False
    # n3 = np.cross(hex_points[3] - hex_points[0], hex_points[7] - hex_points[0])
    n3 = np.array([1, 0, 0])
    x3 = np.dot(x - hex_points[0], n3)
    if x3 < 0:
        return False
    # n4 = np.cross(hex_points[5] - hex_points[1], hex_points[6] - hex_points[1])
    n4 = np.array([-1, 0, 0])
    x4 = np.dot(x - hex_points[1], n4)
    if x4 < 0:
        return False
    # n5 = np.cross(hex_points[4] - hex_points[0], hex_points[5] - hex_points[0])
    n5 = np.array([0, 1, 0])
    x5 = np.dot(x - hex_points[0], n5)
    if x5 < 0:
        return False
    # n6 = np.cross(hex_points[2] - hex_points[3], hex_points[6] - hex_points[3])
    n6 = np.array([0, -1, 0])
    x6 = np.dot(x - hex_points[3], n6)
    if x6 < 0:
        return False
    return True

def bounding_box(points):
    P0 = np.min(points, axis = 0)
    P6 = np.max(points, axis = 0)
    dist = P6 - P0
    P1 = P0.copy()
    P1[0] += dist[0]
    P2 = P1.copy()
    P2[1] += dist[1]
    P3 = P0.copy()
    P3[1] += dist[1]
    P4 = P0.copy()
    P4[2] += dist[2]
    P5 = P1.copy()
    P5[2] += dist[2]
    P7 = P3.copy()
    P7[2] += dist[2]
    bbox = np.concatenate(([P0], [P1], [P2], [P3], [P4], [P5], [P6], [P7]), axis = 0)
    return bbox

def triInBox(AABB, triangle):
    h = np.abs((AABB[1, 0] - AABB[0, 0]) / 2)
    c = AABB[0] + h
    triangle -= c
    # test 1, a00
    p0 = triangle[0, 2] * triangle[1, 1] - triangle[0, 1] * triangle[1, 2]
    p2 = triangle[2, 2] * (triangle[1, 1] - triangle[0, 1]) - triangle[2, 1] * (triangle[1, 2] - triangle[0, 2])
    min_p = min(p0, p2)
    max_p = max(p0, p2)
    r = (np.abs(triangle[1, 2] - triangle[0, 2]) + np.abs(triangle[1, 1] - triangle[0, 1])) * h
    if r < min_p or -r > max_p:
        return 0; # False, no overlap
    # test 2, a10
    p0 = triangle[0, 0] * triangle[1, 2] - triangle[0, 2] * triangle[1, 0]
    p2 = triangle[2, 0] * (triangle[1, 2] - triangle[0, 2]) - triangle[2, 2] * (triangle[1, 0] - triangle[0, 0])
    min_p = min(p0, p2)
    max_p = max(p0, p2)
    r = (np.abs(triangle[1, 2] - triangle[0, 2]) + np.abs(triangle[1, 0] - triangle[0, 0])) * h
    if r < min_p or -r > max_p:
        return 0; # False, no overlap
    # test 3, a20
    p0 = triangle[0, 1] * triangle[1, 0] - triangle[0, 0] * triangle[1, 1]
    p2 = triangle[2, 1] * (triangle[1, 0] - triangle[0, 0]) - triangle[2, 0] * (triangle[1, 1] - triangle[0, 1])
    min_p = min(p0, p2)
    max_p = max(p0, p2)
    r = (np.abs(triangle[1, 1] - triangle[0, 1]) + np.abs(triangle[1, 0] - triangle[0, 0])) * h
    if r < min_p or -r > max_p:
        return 0; # False, no overlap
    # test 4, a01
    p0 = triangle[0, 2] * (triangle[2, 1] - triangle[1, 1]) - triangle[0, 1] * (triangle[2, 2] - triangle[1, 2])
    p1 = triangle[1, 2] * triangle[2, 1] - triangle[1, 1] * triangle[2, 2]
    min_p = min(p0, p1)
    max_p = max(p0, p1)
    r = (np.abs(triangle[2, 2] - triangle[1, 2]) + np.abs(triangle[2, 1] - triangle[1, 1])) * h
    if r < min_p or -r > max_p:
        return 0; # False, no overlap
    # test 5, a11
    p0 = triangle[0, 0] * (triangle[2, 2] - triangle[1, 2]) - triangle[0, 2] * (triangle[2, 0] - triangle[1, 0])
    p1 = triangle[1, 0] * triangle[2, 2] - triangle[1, 2] * triangle[2, 0]
    min_p = min(p0, p1)
    max_p = max(p0, p1)
    r = (np.abs(triangle[2, 2] - triangle[1, 2]) + np.abs(triangle[2, 0] - triangle[1, 0])) * h
    if r < min_p or -r > max_p:
        return 0; # False, no overlap
    # test 6, a21
    p0 = triangle[0, 1] * (triangle[2, 0] - triangle[1, 0]) - triangle[0, 0] * (triangle[2, 1] - triangle[1, 1])
    p1 = triangle[1, 1] * triangle[2, 0] - triangle[1, 0] * triangle[2, 1]
    min_p = min(p0, p1)
    max_p = max(p0, p1)
    r = (np.abs(triangle[2, 1] - triangle[1, 1]) + np.abs(triangle[2, 0] - triangle[1, 0])) * h
    if r < min_p or -r > max_p:
        return 0; # False, no overlap
    # test 7, a02
    p0 = triangle[0, 1] * triangle[2, 2] - triangle[0, 2] * triangle[2, 1]
    p1 = triangle[1, 2] * (triangle[0, 1] - triangle[2, 1]) - triangle[1, 1] * (triangle[0, 2] - triangle[2, 2])
    min_p = min(p0, p1)
    max_p = max(p0, p1)
    r = (np.abs(triangle[0, 2] - triangle[2, 2]) + np.abs(triangle[0, 1] - triangle[2, 1])) * h
    if r < min_p or -r > max_p:
        return 0; # False, no overlap
    # test 8, a12
    p0 = triangle[0, 2] * triangle[2, 0] - triangle[0, 0] * triangle[2, 2]
    p1 = triangle[1, 0] * (triangle[0, 2] - triangle[2, 2]) - triangle[1, 2] * (triangle[0, 0] - triangle[2, 0])
    min_p = min(p0, p1)
    max_p = max(p0, p1)
    r = (np.abs(triangle[0, 2] - triangle[2, 2]) + np.abs(triangle[0, 0] - triangle[2, 0])) * h
    if r < min_p or -r > max_p:
        return 0; # False, no overlap
    # test 9, a22
    p0 = triangle[0, 0] * triangle[2, 1] - triangle[0, 1] * triangle[2, 0]
    p1 = triangle[1, 1] * (triangle[0, 0] - triangle[2, 0]) - triangle[1, 0] * (triangle[0, 1] - triangle[2, 1])
    min_p = min(p0, p1)
    max_p = max(p0, p1)
    r = (np.abs(triangle[0, 1] - triangle[2, 1]) + np.abs(triangle[0, 0] - triangle[2, 0])) * h
    if r < min_p or -r > max_p:
        return 0; # False, no overlap
    # test 10, x-plane
    min_e = min(triangle[:, 0])
    max_e = max(triangle[:, 0])
    if h < min_e or -h > max_e:
        return 0; # False, no overlap
    # test 11, y-plane
    min_e = min(triangle[:, 1])
    max_e = max(triangle[:, 1])
    if h < min_e or -h > max_e:
        return 0; # False, no overlap
    # test 12, z-plane
    min_e = min(triangle[:, 2])
    max_e = max(triangle[:, 2])
    if h < min_e or -h > max_e:
        return 0; # False, no overlap
    # test 13, triangle normal
    n = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
    v = triangle[0]
    min_v = -1 * v
    max_v = min_v.copy()
    for i, nor in enumerate(n):
        if nor > 0:
            min_v[i] -= h
            max_v[i] += h
        else:
            min_v[i] += h
            max_v[i] -= h
    res = np.dot(n, min_v)
    res2 = np.dot(n, max_v)
    if res > 0:
        return 0; # False, no overlap
    elif res2 > 0:
        # print("N:True, possibly overlap") # possibly overlap
        pass
    else:
        return 0; # False, no overlap
    return 1; # triangle intersects all 12 planes, and box intersects normal plane




####################################################

surface_triangles_ini, surface_quads_ini, surface_points = read_surface("./sphere.obj")

######################################################################

#change orientation
surface_triangles = surface_triangles_ini.copy()
surface_quads = surface_quads_ini.copy()
reverseOrientation = 1
if reverseOrientation == 1:
    surface_triangles[:,[1, 2]] = surface_triangles[:,[2, 1]]
    surface_quads[:,[1, 3]] = surface_quads[:,[3, 1]]

######################################

nPoints = len(surface_points)
nTriFaces = len(surface_triangles)
nQuadFaces = len(surface_quads)
nFaces = nTriFaces + nQuadFaces

# get list of face normals
triangleNormals, quadNormals = get_face_normals(surface_points, surface_triangles, surface_quads)

# build neighbour faces for each point on surface mesh
triFaceIndices = [] # [nPoints, number_of_attached_triangle_faces]
quadFaceIndices = [] # [nPoints, number_of_attached_quad_faces]
directValence = [] # [nPoints, 1]
for index in range(nPoints):
    # get face indices for each point split into quad and tri lists
    mask1 = np.isin(surface_triangles, index)
    triFaceIndices.append(np.nonzero(mask1)[0].tolist())
    # triFaceIndices.extend(np.nonzero(mask1)[0])
    mask2 = np.isin(surface_quads, index)
    quadFaceIndices.append(np.nonzero(mask2)[0].tolist())
    # quadFaceIndices.extend(np.nonzero(mask2)[0])

    # get total number of attached faces for each point = direct valence
    indexValence = len(np.nonzero(mask1)[0]) + len(np.nonzero(mask2)[0])
    directValence.append(indexValence)


triangleFaceArea = [] #new
quadFaceArea = [] #new
triangleTargetLevel = [] #new
quadTargetLevel = [] #new
triSizeFieldFactor = 2 * 3 ** -0.25
maxCellSize = 1.2
maxLevel = 10
transLayers = 2

for i, face in enumerate(surface_triangles):
    # faceCentroids.append(centroid(surface_points[face]))
    triArea = area(surface_points[face], triangleNormals[i])
    # faceArea.append(triArea)
    triangleFaceArea.append(triArea) #new
    edgeSize = triSizeFieldFactor * (triArea ** 0.5)
    # sizeField.append(edgeSize)
    # triangleSizeField.append(edgeSize) #new
    r = np.log2(maxCellSize/edgeSize)
    triangleTargetLevel.append(r) #new
for i, face in enumerate(surface_quads):
    quadArea = area(surface_points[face], quadNormals[i])
    quadFaceArea.append(quadArea) #new
    edgeSize = quadArea ** 0.5
    r = np.log2(maxCellSize/edgeSize)
    quadTargetLevel.append(r) #new
triangleFaceArea = np.array(triangleFaceArea) #new
quadFaceArea = np.array(quadFaceArea) #new
triangleTargetLevel = np.array(triangleTargetLevel) #new
quadTargetLevel = np.array(quadTargetLevel) #new

# compute target level / size field of each surface point, weighted average of neighbour faces
pointTargetLevel = []
for index in range(nPoints):
    neigh_targetLevels = np.concatenate((triangleTargetLevel[triFaceIndices[index]], quadTargetLevel[quadFaceIndices[index]]), axis = 0)
    neigh_weights = np.concatenate((triangleFaceArea[triFaceIndices[index]], quadFaceArea[quadFaceIndices[index]]), axis = 0)
    avg_target = np.average(neigh_targetLevels, weights = neigh_weights)

    if np.abs(2 ** np.int(avg_target) - maxCellSize) < np.abs(2 ** (np.int(avg_target) + 1) - maxCellSize):
        pointTargetLevel.append(np.int(avg_target))
    else:
        pointTargetLevel.append(np.int(avg_target) + 1)

pointTargetLevel = np.array(pointTargetLevel)
maxLevel = min(np.max(pointTargetLevel), maxLevel)
if maxLevel == 0:
    print("nothing to refine")
minLevel = min(pointTargetLevel)

# set up base mesh
bBox_origin = np.array([0.0, 0.0, 0.0])
xmin = 6.0
xmax = 6.0
ymin = 6.0
ymax = 6.0
zmin = 6.0
zmax = 6.0
bBox = np.array([-xmin, xmax, -ymin, ymax, -zmin, zmax])
bBox_length = np.array([xmin + xmax, ymin + ymax, zmin + zmax])
nDivisions = np.array(bBox_length / maxCellSize, dtype = np.int)
p0 = bBox_origin - np.array([xmin, ymin, zmin]) # coordinates of bottom-left-forward corner

# get basemesh points
Px = []
for x in range(nDivisions[0] + 1):
    Px.append([x, 0, 0])
Px = np.array(Px)
Py = []
for y in range(nDivisions[1] + 1):
    Py.extend(Px + [0, y, 0])
Py = np.array(Py)
Pz = []
for z in range(nDivisions[2] + 1):
    Pz.extend(Py + [0, 0, z])
Pz = np.array(Pz)
l0_points = maxCellSize * Pz + p0

#get base mesh cells
z_lay = (nDivisions[0] + 1) * (nDivisions[1] + 1) # number of points of each z=constant plane

x_hexas = []
for x in range(nDivisions[0]):
    # hex = [x, nDivisions[0] + x + 1, nDivisions[0] + x + 2, x + 1]
    hex = [x, x + 1, nDivisions[0] + x + 2, nDivisions[0] + x + 1]
    hex.extend(hex + z_lay)
    x_hexas.append(hex)
x_hexas = np.array(x_hexas)
y_hexas = []
for y in range(nDivisions[1]):
    y_hexas.extend(x_hexas + y * (nDivisions[0] + 1))
y_hexas = np.array(y_hexas)
z_hexas = []
for z in range(nDivisions[2]):
    z_hexas.extend(y_hexas + z * z_lay)
z_hexas = np.array(z_hexas)

# print("export base mesh")
# voxel1 = [("hexahedron", z_hexas)]
# mesh = meshio.Mesh(points = l0_points, cells = voxel1)
# meshio.write("./basemesh.vtk", mesh, file_format="vtk", binary=False)
# meshio.write("./basemesh.msh", mesh, file_format="gmsh22", binary=False)


rootIndex = np.arange(z_hexas.shape[0])

# down side:
DS = np.arange(nDivisions[0] * nDivisions[1])
# top Side:
TS = DS + nDivisions[0] * nDivisions[1] * (nDivisions[2] - 1)
# left side
LS = []
for a in range(nDivisions[1]):
    for b in range(nDivisions[2]):
        LS.append(a * nDivisions[0] + b * (nDivisions[0] * nDivisions[1]))
LS = np.array(LS)
# right side:
RS = LS + (nDivisions[0] - 1)
# front side:
FS = []
for c in range(nDivisions[0]):
    for d in range(nDivisions[2]):
        FS.append(c + d * (nDivisions[0] * nDivisions[1]))
FS = np.array(FS)
# back side:
BS = FS + (nDivisions[0] * (nDivisions[1] - 1))


############################################################
octreeMap = {'U': [[4, "H"], [5, "H"], [6, "H"], [7, "H"], [0, "U"], [1, "U"], [2, "U"], [3, "U"]],
             'B': [[3, "H"], [2, "H"], [1, "B"], [0, "B"], [7, "H"], [6, "H"], [5, "B"], [4, "B"]],
             'R': [[1, "H"], [0, "R"], [3, "R"], [2, "H"], [5, "H"], [4, "R"], [7, "R"], [6, "H"]],
             'D': [[4, "D"], [5, "D"], [6, "D"], [7, "D"], [0, "H"], [1, "H"], [2, "H"], [3, "H"]],
             'F': [[3, "F"], [2, "F"], [1, "H"], [0, "H"], [7, "F"], [6, "F"], [5, "H"], [4, "H"]],
             'L': [[1, "L"], [0, "H"], [3, "H"], [2, "L"], [5, "L"], [4, "H"], [7, "H"], [6, "L"]]}
octreeMap2 = [[[4, "H"], [3, "H"], [1, "H"], [4, "D"], [3, "F"], [1, "L"]],
              [[5, "H"], [2, "H"], [0, "R"], [5, "D"], [2, "F"], [0, "H"]],
              [[6, "H"], [1, "B"], [3, "R"], [6, "D"], [1, "H"], [3, "H"]],
              [[7, "H"], [0, "B"], [2, "H"], [7, "D"], [0, "H"], [2, "L"]],
              [[0, "U"], [7, "H"], [5, "H"], [0, "H"], [7, "F"], [5, "L"]],
              [[1, "U"], [6, "H"], [4, "R"], [1, "H"], [6, "F"], [4, "H"]],
              [[2, "U"], [5, "B"], [7, "R"], [2, "H"], [5, "H"], [7, "H"]],
              [[3, "U"], [4, "B"], [6, "H"], [3, "H"], [4, "H"], [6, "L"]]]

################################################################


def all_root_neighbours2(target):
    U = nDivisions[0] * nDivisions[1]
    D = -nDivisions[0] * nDivisions[1]
    B = nDivisions[0]
    F = -nDivisions[0]
    R = 1
    L = -1
    if target in TS:
        U = 0
    else:
        if target in DS:
            D = 0
    if target in FS:
        F = 0
    else:
        if target in BS:
            B = 0
    if target in LS:
        L = 0
    else:
        if target in RS:
            R = 0
    N = np.array([U, U + F, U + B, U + L, U + R, U + F + L, U + F + R, U + B + L, U + B + R,
                  D, D + F, D + B, D + L, D + R, D + F + L, D + F + R, D + B + L, D + B + R,
                  F, B, L, R, F + L, F + R, B + L, B + R]) + target
    N = np.unique(N, axis = 0)
    N = [x for x in N if x != target]
    return N

def level0_intersects_surface(cellIndex):
    # h = maxCellSize / 2 ** (level + 1)
    # h = maxCellSize / 2
    # c = level0_midpoints[cellIndex]
    # AABB = c + h * inflationTemplate
    AABB = all_points[level0_mesh[cellIndex]]
    c = level0_midpoints[cellIndex]
    dist = c - surface_points
    dist = np.linalg.norm(dist, axis = 1)[: , None]
    a = np.argmin(dist) # surface mesh index closest to voxel centre
    cut_tris = triFaceIndices[a]
    cut_quads = quadFaceIndices[a]
    if len(cut_tris) > 0:
        for cut_tri in cut_tris:
            if triInBox(AABB, surface_points[surface_triangles[cut_tri]]):
                return True
    elif len(cut_quads) > 0:
        for cut_quad in cut_quads:
            quad = surface_quads[cut_quad]
            tri1 = [quad[0], quad[1], quad[2]]
            tri2 = [quad[1], quad[2], quad[3]]
            if triInBox(AABB, surface_points[tri1]):
                return True
            elif triInBox(AABB, surface_points[tri2]):
                return True
    return False




all_points = l0_points.copy()
level0_mesh = z_hexas.copy()

# def all_root_neighbours3(target):
#     for corner in level0_mesh[target]:
#
cell = level0_mesh[0]
print("target cell", cell)
# corner = cell[1]
# print(corner)
# print(level0_mesh[0:20])
# print(np.where(level0_mesh == cell))
# test = [x for x in N if x != target]
# test = [np.any(cell) for row in level0_mesh]
# print(test)
# print(len(test))
for index, root in zip(rootIndex, level0_mesh):
    neighbours
    if np.isin(root,cell).any():
        print(root)
# print(np.any(cell))

# mask = level0_mesh == cell.any()
# mask = np.where(level0_mesh == cell.any())
# mask = np.isin(level0_mesh[:],cell).any()
# print(mask)
# neigh = [mask, :]
# print(neigh)

# start_cell = 545
# neigh = all_root_neighbours2(start_cell)

# voxel1 = [("hexahedron", level0_mesh[[start_cell]])]
# mesh = meshio.Mesh(points = all_points, cells = voxel1)
# meshio.write("./root_start.vtk", mesh, file_format="vtk", binary=False)
# voxel1 = [("hexahedron", level0_mesh[neigh])]
# mesh = meshio.Mesh(points = all_points, cells = voxel1)
# meshio.write("./root_neigh.vtk", mesh, file_format="vtk", binary=False)
##########################################################
# level = 0
# level0_midpoints = all_points[level0_mesh[:, 0]] + maxCellSize * 0.5 ** (level + 1)
# distToMidpoint = np.sum((surface_points[0] - level0_midpoints) ** 2, axis = 1)
# start_cell = np.argmin(distToMidpoint)
# neighbours = all_root_neighbours2(start_cell)
# for cell in neighbours:
#     if level0_intersects_surface(cell):
#         level0_intersecting_tmp.append(cell)

######################################################################
# identify start cell
# add start_cell to L0_targets and L0_cut
# translayers; get rInf
# get neighbours
# add neighbours to L0_targets
# for each neighbour
#     check for intersection and add neighbour to L0_cut if yes (also add to targets)
# get intersection first
# for each intersected cell, get neighbour adn engihbours neighbour translayer times
##################################
# initialize cut_cell (cell intersecting surface), cut_cell = []
# initialize targets (cell needed to refine), targets = []
# initialize list of cells checked for intersection, cut_cell_checked = []
# initialize list of cells checked for refinement, targets_checked = []
# compute influence radius
# compute coordinates of midpoints of each level 0 cell
# locate starting cell (level0 cell that needs refinement):
#       create mask of surface points whose level is above 0 (target_mask)
#       select random point from mask
#       locate start cell (cell whose midpoint is closest to seleceted surface point)
# add start_cell to cut_cell
# add start_cell to targets
# add start_cell to cut_cell_checked
# add start_cell to targets_checked
# tmp = []
# targets_tmp = []
# cut_cell_tmp = []
# neighbours_tmp = []
# get neighbours of start_cell
# add neighbours to neighbours_tmp
#(# store neighbours)
# for each neighbour in neighbours_tmp
#   retrive midpoint
#   get surface point from target_mask closest to midpoint PT
#   check if PT is contained in inflated neighbour
#   if yes:
#       add neighbour to targets_tmp
#   get surface point closest to midpoint P
#   check if P is contained in neighbour
#   if yes:
#       add neighbour to cut_cell_tmp
# add neighbours_tmp to cut_cell_checked
# add neighbours_tmp to targets_checked

########################################
# initialize cut_cell (cell that intersect surface), cut_cell = []
# initialize list of cells checked for intersection, cut_cell_checked = []
# (compute influence radius)
# compute coordinates of midpoints of each level 0 cell
# locate starting cell:
#       select random point from surface points
#       locate start cell (cell whose midpoint is closest to seleceted surface point)
# add start_cell to cut_cell
# add start_cell to cut_cell_checked
# tmp = []
# cut_cell_tmp = []
# neighbours_tmp = []
# get neighbours of start_cell
# add neighbours to neighbours_tmp
# (store neighbours [[root_index], U, UF, UFR, ...])
# for each neighbour in neighbours_tmp
#   retrive midpoint
#   get surface point P closest to midpoint
#   check if P is contained in neighbour
#   if yes:
#       add neighbour to cut_cell_tmp
# if cut_cell_tmp is empty, break out of loop
# add neighbours_tmp to cut_cell_checked
# neighbours_tmp = []
# add cut_cell_tmp to cut_cell
# for each cell in cut_cell_tmp:
#   retrive neighbours (either from stored list or compute directly)
#   add neighbours to neighbours_tmp
#   (store neighbours [[root_index], U, UF, UFR, ...])
# cut_cell_tmp = []
# remove duplicates from neighbours_tmp
# remove entries from neighbours_tmp also present in cut_cell_checked
# restart loop

# compute influence radius
# initialize targets, targets = []
# initilize list of cells checked for refinement, targets_checked = []
# targets_tmp = []
# neighbours_tmp = []
# for each cell in cut_cell:
#   retrive its midpoint
#   get surface point P whose target is above 0 closest to midpoint
#   check if P in contained in inflated cell
#   if yes:
#       add cell to targets_tmp
# add targets_tmp to targets
# add cut_cell to targets_checked
# for each cell in targets_tmp:
#   retrive or compute neighbours
#   (store neighbours)
#   add neighbours to neighbours_tmp
# remove duplicates from neighbours_tmp
# remove entries from neighbours_tmp also present in targets_checked
# targets_tmp = []
# for each cell in neighbours_tmp:
#   retrive midpoint
#   get surface point P whose target is above 0 closest to midpoint
#   check if P in contained in inflated cell
#   if yes:
#       add cell to targets_tmp
# if targets_tmp is empty break out of loop
# add targets_tmp to targets
# restart loop

# output: list of targets, targets
#         list of intersecting cells, cut_cells
#         list of root indices, and neighbours

# refine targets

# get list of root cells present in both cut_cells and targets, to_search
# for root in to_search:
#   for octant in root:
        # .
        # .
        # .
# output: cut_cells

# for each cut_cell:

#############################################

# level = 0
# create mask of surface points with target == maxLevel ()
# get first intersection cell (start_cell)
# get midpoint of start_cell
# surface point whose level = maxLevel closest to midpoint
# for target in range[maxLevel, maxlevel - 1, maxLevel - 2, ..., currentLevel +]
#






# find first cut_cell with target > 0 (start_cell)
# get 1st_degree neighbours and 2nd degree neighbours (and transLayer degree neighbour)
# find intersection among 1st_degree neighbours
# for each intersecting cell
# check if nearest
# get 1stdegree neighbours and 2nd degree neighbours (and transLayer degree neighbour)


# level0_intersecting = [] # all level0_mesh indices intersecting the surface
# level0_inter_checked = [] # all level0 cell indices that have been checked for intersection
# level0_inter_neighbours = []
# level0_intersecting_tmp = []
#
# level0_intersecting.append(start_cell)
# level0_inter_checked.append(start_cell)
# level0_inter_neighbours = all_root_neighbours(start_cell)
# #begin "while True"-loop
# while True:
#     level0_intersecting_tmp = []
#     for cell in level0_inter_neighbours:
#         if level0_intersects_surface(cell):
#             level0_intersecting_tmp.append(cell)
#     if len(level0_intersecting_tmp) == 0:
#         print("all level 0 intersecting cells have been found")
#         break
#     level0_intersecting.extend(level0_intersecting_tmp)
#     level0_inter_checked.extend(level0_inter_neighbours)
#     level0_inter_neighbours = []
#     for cell in level0_intersecting_tmp:
#         level0_inter_neighbours.extend(all_root_neighbours(cell))
#     level0_inter_neighbours = list(set(level0_inter_neighbours))
#     level0_inter_neighbours = [x for x in level0_inter_neighbours if x not in level0_inter_checked]
#
# # voxel1 = [("hexahedron", level0_mesh[[start_cell]])]
# # mesh = meshio.Mesh(points = all_points, cells = voxel1)
# # meshio.write("./inter_l0_start.vtk", mesh, file_format="vtk", binary=False)
# # voxel1 = [("hexahedron", level0_mesh[level0_inter_neighbours])]
# # mesh = meshio.Mesh(points = all_points, cells = voxel1)
# # meshio.write("./inter_l0_start_neigh.vtk", mesh, file_format="vtk", binary=False)
#
# ##################################################################


# # begin loop for identifying targets for refinement:
# while True:
#     tempTargets = []
#     for cellIndex in root_neighbours:
#         midpoint = level0_midpoints[cellIndex] # midpoint of neighbour
#         distToMidpoint = np.sum((surface_points[surface_0_plus_mask] - midpoint) ** 2, axis = 1) ** 0.5 # distance between midpoint and surface_points whose level is above 0
#         test_surface_point = surface_points[surface_0_plus_mask[np.argmin(distToMidpoint)]] # coordinates of surface point closest to midpoint
#         hex = np.tile(midpoint, (8, 1)) + rInf * inflationTemplate # coordinates of inflated neighbour
#         if hex_contains(hex, test_surface_point): # condition for whether neighbour needs to be refined
#             tempTargets.append(cellIndex)
#     if len(tempTargets) == 0:
#         break
#     else:
#         level0_targets.extend(tempTargets)
#     level0_checked.extend(root_neighbours)
#     root_neighbours = []
#     for cellIndex in tempTargets:
#         root_neighbours.extend(all_root_neighbours(cellIndex))
#     root_neighbours = list(set(root_neighbours))
#     root_neighbours = [x for x in root_neighbours if x not in level0_checked]
# level0_non_targets = np.delete(level0_non_targets, level0_targets)
#
# # refine seleceted targets from level 0 to level 1
# level1_mesh = []
# for targetCell in level0_mesh[level0_targets]:
#     # split level 0 target cell into 8 children and add children to level1_mesh:
#     children = np.diag(targetCell)
#     template = newLevelTemplate + all_points.shape[0]
#     np.fill_diagonal(template, 0)
#     children += template
#     level1_mesh.extend(children)
#     # compute coordinates of children cells:
#     chidlren_coords = newPointsTemplate * 0.5 ** (level + 1) * maxCellSize + all_points[targetCell[0]]
#     all_points = np.concatenate((all_points, chidlren_coords), axis = 0)
# level1_mesh = np.array(level1_mesh)
