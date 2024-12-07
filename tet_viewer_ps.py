#!/usr/bin/env python3

import numpy as np
import polyscope as ps
import matplotlib.pyplot as plt
import sys
from pathlib import Path

def read_tet_mesh(filename):
    """
    Read a tetrahedral mesh file.
    
    Args:
        filename: Path to the mesh file
        
    Returns:
        vertices: Nx3 array of vertex coordinates
        tets: Mx4 array of tetrahedral connectivity
    """
    vertices = []
    tets = []
    
    with open(filename, 'r') as f:
        # Read header
        n_vertices = int(f.readline().split()[0])
        n_inner_tets = int(f.readline().split()[0])
        n_outer_tets = int(f.readline().split()[0])
        
        # Read vertices
        for _ in range(n_vertices):
            x, y, z = map(float, f.readline().split())
            vertices.append([x, y, z])
            
        # Read tetrahedra
        for _ in range(n_inner_tets + n_outer_tets):
            indices = list(map(int, f.readline().split()))
            tets.append(indices[1:])  # Skip the first number
            
    return np.array(vertices), np.array(tets)

def plot_tet_mesh(vertices, tets):
    """
    Plot the tetrahedral mesh using Polyscope, showing only the edges.
    
    Args:
        vertices: Nx3 array of vertex coordinates
        tets: Mx4 array of tetrahedral connectivity
    """
    # Clear any existing structures
    ps.remove_all_structures()

    # Initialize polyscope
    ps.init()
    
    # Register the tetrahedral mesh
    ps_mesh = ps.register_volume_mesh("tet mesh", vertices, tets)
    
    # Hide the tet faces
    ps_mesh.set_enabled(False)
    
    # Create rainbow colors for tets
    tet_colors = plt.cm.rainbow(np.linspace(0, 1, len(tets)))[:, :3]  # Get RGB values

    # Add colors to the tets
    ps_mesh.add_color_quantity("tet colors", tet_colors, defined_on='cells', enabled=True)

    # Make tets fully transparent
    ps_mesh.set_transparency(0.08)  # 1.0 is fully transparent
    
    # Create edges array
    edges = set()
    for tet in tets:
        for i in range(4):
            for j in range(i+1, 4):
                # Sort vertices to avoid duplicates
                edge = tuple(sorted([tet[i], tet[j]]))
                edges.add(edge)
    
    # Convert edges to numpy array
    edges_array = np.array(list(edges))
    
    # Register the edges as a curve network
    ps_edges = ps.register_curve_network("tet edges", vertices, edges_array)
    
    # Set visualization options
    ps.set_ground_plane_mode("none")
    
    # You can customize the edge appearance
    ps_edges.set_radius(0.001)  # Make edges thinner
    ps_edges.set_color((0.1, 0.1, 0.8))  # Set edge color (RGB)
    
    # Set the camera angle
    ps.reset_camera_to_home_view()
    
    # Show the mesh
    ps.show()

def get_tet_edges(tets):
    """Helper function to extract unique edges from tetrahedral mesh"""
    edges = set()
    for tet in tets:
        for i in range(4):
            for j in range(i+1, 4):
                edge = tuple(sorted([tet[i], tet[j]]))
                edges.add(edge)
    return np.array(list(edges))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_tet_file>")
        print("Example: python script.py files_starter/tets/example.tet")
        sys.exit(1)
        
    tet_file = sys.argv[1]
    
    if not Path(tet_file).exists():
        print(f"Error: File '{tet_file}' not found")
        sys.exit(1)
        
    if not tet_file.endswith('.tet'):
        print("Warning: File does not have .tet extension")
    
    try:
        vertices, tets = read_tet_mesh(tet_file)
        plot_tet_mesh(vertices, tets)
    except Exception as e:
        print(f"Error reading or plotting mesh: {e}")
        sys.exit(1)