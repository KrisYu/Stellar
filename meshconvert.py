#!/usr/bin/env python3

#!/usr/bin/env python3
# encoding: utf-8
"""
meshconvert.py

A script to convert between tetrahedral mesh formats.

Created by Bryan Klingner (stellar.b@overt.org) on 2006-12-07.
"""

import sys
import getopt
import os

help_message = '''
meshconvert.py - a script to convert between tetrahedral mesh formats.

Usage:
        meshconvert.py [-s scale] input_file output_file
        
                input_file    the input tetrahedral (or trianglar surface) mesh file. 
                                            This file must be in one of the following formats:
                                                    .node  - Jonathan Shewchuk's node file format.
                                                                    .node files must be accompanied by a
                                                                    .ele file that contains tetrahedra.
                                                    .tet   - AIM@SHAPE repository's tetrahedral mesh format.
                                                    
                output_file   the output tetrahedral (or triangular surface) mesh file.
                                            This file must be in one of the following formats:
                                                    .node  - Jonathan Shewchuk's mesh file format.
                                                                    An additional .ele file will also be 
                                                                    output that contains tetrahedra.
                                                    .tet   - AIM@SHAPE repository's tetrahedral mesh format.
                                                                    file is in .obj format, only boundary triangles
                                                                
                -s scale      optional vertex scale argument. All vertices geometric positions
                                            will be multiplied by scale in the output file.
'''

class Usage(Exception):
        def __init__(self, msg):
                self.msg = msg
            
def main(argv=None):
    # functions for reading 
    readDict = {}
    readDict['.node'] = readNodeEle
    readDict['.tet'] = readTet

    # functions for writing
    writeDict = {}
    writeDict['.node'] = writeNodeEle
    writeDict['.tet'] = writeTet

    if argv is None:
            argv = sys.argv
        
    doscale = False

    # if they invoke with arguments, parse them
    if len(argv) > 1:
            try:
                    try:
                            opts, args = getopt.getopt(argv[1:], "hs:", ["help",])
                    except getopt.error as msg:
                            raise Usage(msg)
                        
                    # option processing
                    for option, value in opts:
                            if option == "-s":
                                    doscale = True
                                    scale = float(value)
                            if option in ("-h", "--help"):
                                    print(help_message)
                                    return 1
            except Usage as err:
                    print(f"{sys.argv[0].split('/')[-1]}: {str(err.msg)}", file=sys.stderr)
                    print("\t for help use --help", file=sys.stderr)
                    return 2
    else:
            print(help_message)
            return 1

    if len(argv) < 3:
            print("Not enough arguments. For help, use --help.")
        
    # determine the input and output formats, and check that they make sense
    inFileName = argv[-2]
    outFileName = argv[-1]
    inFileNameBase, inType = os.path.splitext(inFileName)
    outFileNameBase, outType = os.path.splitext(outFileName)

    if inType not in readDict:
            print(f"Don't know how to read input format '{inType}'; invoke with --help for a list of supported formats.")
            return 2
    if outType not in writeDict:
            print(f"Don't know how to write output format '{outType}'; invoke with --help for a list of supported formats.")
            return 2

    # read the input mesh
    points, tets, boundFaces = readDict[inType](inFileNameBase)
    if doscale:
            print(f"Scaling vertices by {scale}")
            points = [vscale(scale, point) for point in points]
    # write the output mesh
    writeDict[outType](points, tets, boundFaces, outFileNameBase)
    
def readTet(meshFileName):
    """Read .tet format
    
    File Format:
        #number vertices
        #number inner tets
        #number outer tets
        followed by x ,y, z, points
        followed by 4 i0, i1, i2, i3, tet index
    """

    # append .mesh to file stem
    meshFileName += '.tet'

    # open input .tet file
    with open(meshFileName) as f:
        n_vertices = int(f.readline().split()[0])
        n_inner_tets = int(f.readline().split()[0])
        n_outer_tets = int(f.readline().split()[0])

        points = []
        # read in all the points
        for _ in range(n_vertices):
            x, y, z = map(float, f.readline().split())
            points.append([x, y, z])
            
        tets = []
        # read in the tets
        for _ in range(n_inner_tets + n_outer_tets):
            indices = list(map(int, f.readline().split()))
            tets.append(indices[1:])  # Skip the first number
                
    # correct orientation of tets
    for tetNum, tet in enumerate(tets):
        a = points[tet[0]-1]
        b = points[tet[1]-1]
        c = points[tet[2]-1]
        d = points[tet[3]-1]
        # if tet is negative orientation, flip two verts
        if orient3d(a,b,c,d) == 0:
            print("WHOA! input zero-volume tet...\n")
        if orient3d(a,b,c,d) < 0:
            temp = tet[0]
            tets[tetNum][0] = tet[1]
            tets[tetNum][1] = temp
            
    # this function doesn't attempt to recover boundary faces
    boundFaces = []

    return points, tets, boundFaces


def readNodeEle(filename, computeTopo=False):
    """Read a tetrahedral mesh in .node/.ele format, Jonathan Shewchuk's format.
            The .node file specifies the vertex locations and the .ele format specfies
            the tetrahedra. The .node file might start with an index of one or zero."""

    points, startFromZero = ReadNode(filename)
    tets = ReadEle(filename, startFromZero)

    # correct orientation of tets
    for tetNum, tet in enumerate(tets):
        a = points[tet[0]]
        b = points[tet[1]]
        c = points[tet[2]]
        d = points[tet[3]]
        # if tet is negative orientation, flip two verts
        if orient3d(a,b,c,d) == 0.0:
            print(f"WHOA! input zero-volume tet#{tetNum}...")
            print(f"a= {' '.join(['{:0.18g}'.format(x) for x in a])}")
            print(f"b= {' '.join(['{:0.18g}'.format(x) for x in b])}")
            print(f"c= {' '.join(['{:0.18g}'.format(x) for x in c])}")
            print(f"d= {' '.join(['{:0.18g}'.format(x) for x in d])}")
        if orient3d(a,b,c,d) < 0.0:
            print(f"correcting inverted tet #{tetNum}")
            temp = tet[0]
            tets[tetNum][0] = tet[1]
            tets[tetNum][1] = temp
            
    # build face topology information
    if computeTopo:
        faces, boundFaces, face2tet = GetFaceTopo(tets)
    else:
        boundFaces = None
    
    return points, tets, boundFaces

def GetFaceTopo(tets):
    """Recover topological information about faces"""
    
    # first, build list of all passible faces
    faces = []
    for tet in tets:
        # append each (outward oriented) face of the tet
        faces.append([tet[0], tet[1], tet[2]])
        faces.append([tet[0], tet[2], tet[3]])
        faces.append([tet[0], tet[3], tet[1]])
        faces.append([tet[1], tet[3], tet[2]])
        
    # sort the faces so the indices are in consistent order
    sortedFaces = [sorted(face) for face in faces]
    
    # get the unique faces
    uniqueFaces = unique(sortedFaces)
    
    uFaceDict = {}
    # build a dictionary of unique faces to speed lookup
    for facenum, face in enumerate(uniqueFaces):
        uFaceDict[tuple(face)] = facenum
        
    # build the tet -> face mapping by finding the index
    # into the unique face list for each face of each tet
    tet2face = []
    for tetNum in range(len(tets)):
        tet2face.append([uFaceDict[tuple(sortedFaces[tetNum*4])],
                        uFaceDict[tuple(sortedFaces[tetNum*4+1])],
                        uFaceDict[tuple(sortedFaces[tetNum*4+2])],
                        uFaceDict[tuple(sortedFaces[tetNum*4+3])]])
        
    # build the face -> tet mapping by finding the one or two tets
    # that contain each face in the unique face list
    face2tet = []
    for face in uniqueFaces:
        face2tet.append([-1, -1])     
        
    for tetNum, tetfaces in enumerate(tet2face):
        for face in tetfaces:
            if face2tet[face][0] == -1:
                face2tet[face][0] = tetNum
            else:
                if (face2tet[face][1] != -1):
                    print("whoa, found more than two tets for a face?")
                    print(f"tetnum is {tetNum}, face2tet[face] is {face2tet[face]}")
                assert(face2tet[face][1] == -1)
                face2tet[face][1] = tetNum
                
    boundaryFaces = []
    # finally, get the list of boundary faces by building
    # list of all faces with just one tet
    for faceNum, facetets in enumerate(face2tet):
        if facetets[1] == -1:
            # this face has just one tet; it's a boundary face
            tet = tets[facetets[0]]
            tetfaces = [[tet[0], tet[1], tet[2]],
                       [tet[0], tet[2], tet[3]],
                       [tet[0], tet[3], tet[1]],
                       [tet[1], tet[3], tet[2]]]
            
            # find the properly oriented face
            foundface = False
            for face in tetfaces:
                if (uniqueFaces[faceNum] == sorted(face)):
                    boundaryFaces.append(face)
                    foundface = True
            assert(foundface)
            foundface = False
            
    return uniqueFaces, boundaryFaces, face2tet


def ReadNode(fileName):
    inFileName = fileName + '.node'
    
    with open(inFileName) as infile:
        # fetch the number of points
        firstline = list(map(int, infile.readline().strip().split()))
        numPoints = firstline[0]
        numMarkers = firstline[-1]
        
        # read in all the points
        points = []
        for iter in range(numPoints):
            # check whether point numbering starts at 1 (instead of 0)
            if iter == 0:
                firstline = infile.readline().strip().split()
                startFromZero = firstline[0] != '1'
                # now put in the actual first point
                if numMarkers != 0:
                    points.append(list(map(float, firstline[1:-numMarkers])))
                else:
                    points.append(list(map(float, firstline[1:])))
            else:
                if numMarkers != 0:
                    points.append(list(map(float, infile.readline().strip().split()[1:-numMarkers])))
                else:
                    points.append(list(map(float, infile.readline().strip().split()[1:])))
                    
    return points, startFromZero

def ReadEle(fileName, startFromZero=True):
    inFileName = fileName + '.ele'
    
    with open(inFileName) as infile:
        # fetch the number of tets
        firstline = list(map(int, infile.readline().strip().split()))
        numTets = firstline[0]
        numMarkers = firstline[-1]
        
        # read in all the tets
        tets = []
        for _ in range(numTets):
            # skip the tet number
            line = list(map(int, infile.readline().strip().split()))
            if numMarkers == 0:
                tets.append(line[1:])
            else:
                tets.append(line[1:-numMarkers])
                
    # if vert indices started at one, decrement all the indices
    if not startFromZero:
        for index, tet in enumerate(tets):
            tets[index] = vsubscalar(1, tet)
            
    return tets

def writeNode(points, outFileName):
    if '.node' not in outFileName:
        outFileName += '.node'
    with open(outFileName, 'w') as outfile:
        outfile.write(f"{len(points)} 3 0 0\n")
        for i, point in enumerate(points):
            outfile.write(f"{i+1} {' '.join(f'{x:.18g}' for x in point)}\n")
            
def writeNodeEle(points, tets, boundFaces, outFileName):
    writeNode(points, outFileName)
    writeEle(tets, outFileName)

def writeEle(tets, outFileName):
    outFileName += '.ele'
    with open(outFileName, 'w') as outfile:
        outfile.write(f"{len(tets)} 4 0\n")
        for i, tet in enumerate(tets):
            tets[i] = vaddscalar(1, tet)
            outfile.write(f"{i+1} {' '.join(map(str, tets[i]))}\n")

def writeTet(points, tets, boundFaces, outFileName):
    outFileName += '.tet'
    with open(outFileName, 'w') as f:
        # Write number of vertices
        f.write(f"{len(points)} vertices\n")
        # Since we don't track inner/outer tets separately, write all as inner
        f.write(f"{len(tets)} inner tets\n")
        f.write("0 outer tets\n")  # No outer tets
        
        # Write points
        for point in points:
            f.write(f"{point[0]} {point[1]} {point[2]}\n")
            
        # Write tets (add index 1 at start since format expects it)
        for i, tet in enumerate(tets):
            f.write(f"1 {' '.join(map(str, tet))}\n")
    
def vadd(v1, v2):
    """Add two vectors"""
    return [a + b for a, b in zip(v1, v2)]

def vsub(v1, v2):
    """Subtract two vectors"""
    return [a - b for a, b in zip(v1, v2)]

def vlength(v):
    """Calculate vector length"""
    return sum(x * x for x in v) ** 0.5

def vscale(scale, v):
    """Scale a vector"""
    return [x * scale for x in v]

def vnorm(v):
    """Normalize a vector"""
    length = vlength(v)
    return vscale(1/length, v)

def vaddscalar(scalar, v):
    """Add scalar to vector"""
    return [x + scalar for x in v]

def vsubscalar(scalar, v):
    """Subtract scalar from vector"""
    return [x - scalar for x in v]

def orient3d(a, b, c, d):
    """Compute the orientation of 4 points in 3D"""
    m11 = a[0] - d[0]
    m12 = a[1] - d[1]
    m13 = a[2] - d[2]
    m21 = b[0] - d[0]
    m22 = b[1] - d[1]
    m23 = b[2] - d[2]
    m31 = c[0] - d[0]
    m32 = c[1] - d[1]
    m33 = c[2] - d[2]
    
    det = (m11 * m22 * m33) + (m12 * m23 * m31) + (m13 * m21 * m32) - \
          (m11 * m23 * m32) - (m12 * m21 * m33) - (m13 * m22 * m31)
    
    return det

def unique(s):
    """Return a list of the elements in s, but without duplicates."""
    if not s:
        return []
    
    try:
        return list({tuple(x) if isinstance(x, list) else x: 1 for x in s}.keys())
    except TypeError:
        # If items aren't hashable, try sorting
        try:
            t = list(s)
            t.sort()
            return [x for i, x in enumerate(t) if i == 0 or t[i-1] != x]
        except TypeError:
            # Brute force if sorting fails
            u = []
            for x in s:
                if x not in u:
                    u.append(x)
            return u
        
if __name__ == "__main__":
    sys.exit(main())