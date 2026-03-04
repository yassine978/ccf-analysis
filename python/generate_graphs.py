"""
Graph generator for CCF benchmarking.

Generates several families of synthetic graphs:

1. Scalability graphs — single connected component, increasing size
   small   — 500 nodes,     1 000 edges
   medium  — 10 000 nodes,  50 000 edges
   large   — 100 000 nodes, 500 000 edges
   xlarge  — 500 000 nodes, 2 500 000 edges

2. Multi-component graph — fixed number of isolated components
   multicomp — 5 components × 200 nodes × 400 edges

3. Density-variation graphs — same node count, varying edge density
   sparse  — 1 000 nodes, ~1 000 edges  (density ≈ 1× nodes)
   medium_density — 1 000 nodes, ~5 000 edges
   dense   — 1 000 nodes, ~20 000 edges

All files are saved as whitespace-separated edge lists with a comment header.
"""

import random
import os

OUTPUT_DIR = "/app/data"


# ──────────────────────────────────────────────────────────────────────────────
# Graph generators
# ──────────────────────────────────────────────────────────────────────────────

def generate_connected_graph(num_nodes, num_edges, seed=42):
    """
    Generate a single connected component random graph.

    Strategy:
      1. Shuffle nodes and link consecutive pairs → random spanning tree
         guarantees full connectivity of the base component.
      2. Add random edges until reaching num_edges (no self-loops, no duplicates).

    Returns a set of (u, v) tuples with u < v.
    """
    rng = random.Random(seed)
    edges = set()

    nodes = list(range(1, num_nodes + 1))
    rng.shuffle(nodes)

    # Spanning tree: n-1 edges connecting all nodes
    for i in range(1, min(num_nodes, num_edges)):
        u, v = nodes[i - 1], nodes[i]
        edges.add((min(u, v), max(u, v)))

    # Fill up to num_edges with random edges
    attempts = 0
    while len(edges) < num_edges and attempts < num_edges * 10:
        u = rng.randint(1, num_nodes)
        v = rng.randint(1, num_nodes)
        if u != v:
            edges.add((min(u, v), max(u, v)))
        attempts += 1

    return edges


def generate_multi_component_graph(n_components, nodes_per_comp, edges_per_comp, seed=99):
    """
    Generate a graph with exactly n_components isolated connected components.

    Each component is a connected random graph on `nodes_per_comp` nodes with
    approximately `edges_per_comp` edges. Components share no edges.

    Returns (list of (u,v) edge tuples, true number of components).
    """
    rng = random.Random(seed)
    all_edges = []
    offset = 0

    for comp_idx in range(n_components):
        local_nodes = list(range(offset + 1, offset + nodes_per_comp + 1))
        rng.shuffle(local_nodes)
        local_edges = set()

        # Spanning tree within this component
        for i in range(1, nodes_per_comp):
            u, v = local_nodes[i - 1], local_nodes[i]
            local_edges.add((min(u, v), max(u, v)))

        # Fill up to edges_per_comp
        attempts = 0
        while len(local_edges) < edges_per_comp and attempts < edges_per_comp * 10:
            u = rng.randint(offset + 1, offset + nodes_per_comp)
            v = rng.randint(offset + 1, offset + nodes_per_comp)
            if u != v:
                local_edges.add((min(u, v), max(u, v)))
            attempts += 1

        all_edges.extend(sorted(local_edges))
        offset += nodes_per_comp

    return all_edges, n_components


def generate_density_graph(num_nodes, density_factor, seed=42):
    """
    Generate a connected graph whose edge count is density_factor × num_nodes.

    density_factor = 1  → sparse (near-tree)
    density_factor = 5  → medium density
    density_factor = 20 → dense

    Returns a set of (u, v) edge tuples with u < v.
    """
    num_edges = int(num_nodes * density_factor)
    return generate_connected_graph(num_nodes, num_edges, seed=seed)


# ──────────────────────────────────────────────────────────────────────────────
# File writer helper
# ──────────────────────────────────────────────────────────────────────────────

def write_edge_list(path, edges, header_comment):
    """Write an edge list file with a comment header line."""
    with open(path, "w") as f:
        f.write(f"# {header_comment}\n")
        for u, v in sorted(edges):
            f.write(f"{u} {v}\n")


# ──────────────────────────────────────────────────────────────────────────────
# Graph specifications
# ──────────────────────────────────────────────────────────────────────────────

SCALABILITY_GRAPHS = {
    "graph_small.txt":  (500,     1_000),
    "graph_medium.txt": (10_000,  50_000),
    "graph_large.txt":  (100_000, 500_000),
    "graph_xlarge.txt": (500_000, 2_500_000),
}

DENSITY_GRAPHS = {
    "graph_density_sparse.txt":  (1_000, 1),
    "graph_density_medium.txt":  (1_000, 5),
    "graph_density_dense.txt":   (1_000, 20),
}


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── 1. Scalability graphs ─────────────────────────────────────────────────
    print("=== Scalability graphs ===")
    for filename, (n_nodes, n_edges) in SCALABILITY_GRAPHS.items():
        path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(path):
            print(f"[skip] {filename}")
            continue
        print(f"Generating {filename}  (nodes={n_nodes}, edges≈{n_edges}) ...")
        edges = generate_connected_graph(n_nodes, n_edges)
        write_edge_list(path, edges, f"nodes={n_nodes} edges={len(edges)}")
        print(f"  -> saved {len(edges)} edges to {path}")

    # ── 2. Multi-component graph ──────────────────────────────────────────────
    print("\n=== Multi-component graph ===")
    mc_path = os.path.join(OUTPUT_DIR, "graph_multicomp.txt")
    if os.path.exists(mc_path):
        print("[skip] graph_multicomp.txt")
    else:
        print("Generating graph_multicomp.txt  (5 components × 200 nodes × 400 edges) ...")
        mc_edges, mc_comps = generate_multi_component_graph(
            n_components=5, nodes_per_comp=200, edges_per_comp=400)
        with open(mc_path, "w") as f:
            f.write(f"# components={mc_comps} nodes_per_comp=200 edges_per_comp=400\n")
            for u, v in mc_edges:
                f.write(f"{u} {v}\n")
        print(f"  -> saved {len(mc_edges)} edges to {mc_path}")

    # ── 3. Density-variation graphs ───────────────────────────────────────────
    print("\n=== Density-variation graphs (1 000 nodes) ===")
    for filename, (n_nodes, df) in DENSITY_GRAPHS.items():
        path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(path):
            print(f"[skip] {filename}")
            continue
        n_edges_approx = n_nodes * df
        print(f"Generating {filename}  (nodes={n_nodes}, density={df}×, edges≈{n_edges_approx}) ...")
        edges = generate_density_graph(n_nodes, df)
        write_edge_list(path, edges, f"nodes={n_nodes} density_factor={df} edges={len(edges)}")
        print(f"  -> saved {len(edges)} edges to {path}")

    print("\nAll graphs ready.")


if __name__ == "__main__":
    main()
