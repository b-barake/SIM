import networkx as nx
import matplotlib.pyplot as plt


def create_product_structure_graph(bom_data):
    """
    Create a directed graph representing the product structure (Graph 1).

    Parameters:
    -----------
    bom_data : list of dict
        Bill of Material data with assembly, component, and quantity information

    Returns:
    --------
    G : networkx.DiGraph
        Directed graph representing the product structure
    """
    G = nx.DiGraph() # empty directed graph

    # Track node roles - helps with proper assignment
    node_roles = {}

    # First pass: identify all roles a node plays
    for bom_entry in bom_data:
        assembly = bom_entry['Assembly']
        component = bom_entry['Component']

        # initialize role sets if parts haven't been seen yet
        if assembly not in node_roles:
            node_roles[assembly] = set()
        if component not in node_roles:
            node_roles[component] = set()

        # Record the roles each part plays
        node_roles[assembly].add('assembly')
        node_roles[component].add('component')

    # Add nodes with appropriate type information
    for node, roles in node_roles.items():
        if 'assembly' in roles and 'component' in roles:
            G.add_node(node, type='subassembly')
        elif 'assembly' in roles:
            G.add_node(node, type='assembly')
        else:
            G.add_node(node, type='component') # only a component

    # Add edges to connect the nodes
    for bom_entry in bom_data:
        assembly = bom_entry['Assembly']
        component = bom_entry['Component']
        quantity = bom_entry['QuantityPer']
        scrap = bom_entry.get('Scrap', 0)

        quantity = bom_entry['QuantityPer']
        scrap = bom_entry.get('Scrap', 0)

        # Add edge from assembly to component
        G.add_edge(assembly, component, quantity=quantity, scrap=scrap)

    return G


# def visualize_graph(G, title="Product Structure Graph"):
#     """
#     Visualize the product structure graph using matplotlib.
#
#     Parameters:
#     -----------
#     G : networkx.Graph
#         Graph to visualize
#     title : str
#         Title for the plot
#     """
#     plt.figure(figsize=(12, 8))
#     pos = nx.spring_layout(G, 0.5, iterations=50)
#
#     # Define node colors based on type
#     node_colors = []
#     for node in G.nodes():
#         node_type = G.nodes[node].get('type', 'unknown')
#         if node_type == 'assembly':
#             node_colors.append('lightcoral')
#         elif node_type == 'subassembly':
#             node_colors.append('gold')
#         elif node_type == 'component':
#             node_colors.append('lightblue')
#         else:
#             node_colors.append('lightgray')
#
#     # Create a legend mapping
#     legend_elements = [
#         plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral',
#                    markersize=10, label='Assembly'),
#         plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gold',
#                    markersize=10, label='Subassembly'),
#         plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue',
#                    markersize=10, label='Component')
#         ]
#
#     # Draw nodes with different colors based on type
#     nx.draw_networkx_nodes(G, pos, node_size=700, node_color=node_colors)
#
#     # Draw edge labels with quantity information
#     nx.draw_networkx_edges(G, pos, width=1.0, arrows=True, arrowstyle='->', arrowsize=15)
#
#     # Draw node labels
#     nx.draw_networkx_labels(G, pos, font_size=10)
#
#     # Draw edge labels with quantity information
#     edge_labels = {(u, v): f"Qty: {d['quantity']}" for u, v, d in G.edges(data=True)}
#     nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
#
#
#     plt.title(title)
#     plt.axis('off')
#     plt.legend(handles=legend_elements, loc='upper right')
#     plt.tight_layout()
#     return plt

def visualize_graph(G, title="Hierarchical Product Structure"):
    """
    Visualize the product structure graph with hierarchical layout and color-coded nodes.
    Uses custom hierarchical layout based on node ranks.

    Parameters:
    -----------
    G : networkx.DiGraph
        Directed Graph to visualize with 'type' node attributes
    title : str
        Title for the plot
    """
    plt.figure(figsize=(14, 10))

    # First, ensure we're working with a directed graph
    if not isinstance(G, nx.DiGraph):
        G = nx.DiGraph(G)

    # Find root nodes (those with no incoming edges)
    roots = [n for n in G.nodes() if G.in_degree(n) == 0]

    # If no roots found (might be a cycle), use nodes with minimum in-degree
    if not roots:
        min_in_degree = min(dict(G.in_degree()).values())
        # Fix the list comprehension by properly iterating through in_degree tuples
        roots = [node for node, degree in G.in_degree() if degree == min_in_degree]

    # Calculate the rank (distance from root) for each node
    # Initialize all nodes with rank of -1 (unvisited)
    for node in G.nodes():
        G.nodes[node]['rank'] = -1

    # Use BFS to assign ranks (distance from roots)
    for root in roots:
        # Root nodes have rank 0
        G.nodes[root]['rank'] = 0
        # Queue for BFS: (node, current_rank)
        queue = [(root, 0)]
        visited = set([root])

        while queue:
            current, rank = queue.pop(0)
            # Process all children of the current node
            for child in G.successors(current):
                # If child not visited or we found a longer path to it
                new_rank = rank + 1
                if child not in visited or new_rank > G.nodes[child]['rank']:
                    G.nodes[child]['rank'] = new_rank
                    visited.add(child)
                    queue.append((child, new_rank))

    # Group nodes by their rank
    nodes_by_rank = {}
    for node in G.nodes():
        rank = G.nodes[node]['rank']
        if rank not in nodes_by_rank:
            nodes_by_rank[rank] = []
        nodes_by_rank[rank].append(node)

    # Create custom positions based on rank
    pos = {}
    max_rank = max(nodes_by_rank.keys())
    for rank, nodes in nodes_by_rank.items():
        # X position based on rank (normalized between 0 and 1)
        x = rank / max(1, max_rank)

        # Distribute nodes vertically at this rank
        total_nodes = len(nodes)
        for i, node in enumerate(nodes):
            # Y position evenly distributed for nodes at the same rank
            y = (i - (total_nodes - 1) / 2) / max(1, total_nodes)
            pos[node] = (x, y)

    # Define node colors based on type
    node_colors = []
    for node in G.nodes():
        node_type = G.nodes[node].get('type', 'unknown')
        if node_type == 'assembly':
            node_colors.append('lightcoral')  # Red for assemblies
        elif node_type == 'subassembly':
            node_colors.append('gold')  # Yellow/gold for subassemblies
        elif node_type == 'component':
            node_colors.append('lightblue')  # Blue for components
        else:
            node_colors.append('lightgray')  # Gray for unknown types

    # Create legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral',
                   markersize=10, label='Assembly'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gold',
                   markersize=10, label='Subassembly'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue',
                   markersize=10, label='Component')
    ]

    # Draw nodes with different colors based on type
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color=node_colors, alpha=0.9)

    # Draw edges with arrow
    nx.draw_networkx_edges(G, pos, width=1.0, arrows=True, arrowstyle='->', arrowsize=15)

    # Draw node labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

    # Draw edge labels with quantity information
    edge_labels = {(u, v): f"Qty: {d['quantity']}" for u, v, d in G.edges(data=True)
                   if 'quantity' in d}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    plt.title(title, fontsize=16)
    plt.axis('off')
    plt.legend(handles=legend_elements, loc='upper right')
    plt.tight_layout()
    plt.show()
    return plt.gcf()  # Return the current figure


# src/simulation/time_space_network.py
def create_time_space_network(product_graph, events):
    """
    Create a time-space network (Graph 2) based on product structure and events.

    Parameters:
    -----------
    product_graph : networkx.DiGraph
        Product structure graph
    events : list of dict
        List of events with node, time, and event_type information

    Returns:
    --------
    TSN : networkx.DiGraph
        Time-space network graph
    """
    TSN = nx.DiGraph()

    # Sort events by time
    sorted_events = sorted(events, key=lambda x: x['time'])

    # Create time-space nodes for each event
    for event in sorted_events:
        node = event['node']
        time = event['time']
        event_type = event['event_type']

        # Create a unique identifier for this time-space node
        ts_node = f"{node}_{time}"

        # Add the time-space node to the graph
        TSN.add_node(ts_node,
                     original_node=node,
                     time=time,
                     event_type=event_type)

    # Connect time-space nodes with edges
    nodes_by_original = {}
    for ts_node in TSN.nodes:
        original = TSN.nodes[ts_node]['original_node']
        if original not in nodes_by_original:
            nodes_by_original[original] = []
        nodes_by_original[original].append(ts_node)

    # For each original node, connect its time-space nodes chronologically
    for original, ts_nodes in nodes_by_original.items():
        sorted_ts_nodes = sorted(ts_nodes, key=lambda x: TSN.nodes[x]['time'])
        for i in range(len(sorted_ts_nodes) - 1):
            from_node = sorted_ts_nodes[i]
            to_node = sorted_ts_nodes[i + 1]
            from_time = TSN.nodes[from_node]['time']
            to_time = TSN.nodes[to_node]['time']
            lead_time = to_time - from_time

            TSN.add_edge(from_node, to_node, lead_time=lead_time)

    # Add edges between related nodes at different original nodes (e.g., assembly to component)
    for u, v in product_graph.edges():
        u_ts_nodes = sorted(nodes_by_original.get(u, []),
                            key=lambda x: TSN.nodes[x]['time'])
        v_ts_nodes = sorted(nodes_by_original.get(v, []),
                            key=lambda x: TSN.nodes[x]['time'])

        for u_node in u_ts_nodes:
            u_time = TSN.nodes[u_node]['time']

            # Find the next v_node after u_time
            next_v_node = None
            for v_node in v_ts_nodes:
                v_time = TSN.nodes[v_node]['time']
                if v_time > u_time:
                    next_v_node = v_node
                    break

            if next_v_node:
                v_time = TSN.nodes[next_v_node]['time']
                lead_time = v_time - u_time
                TSN.add_edge(u_node, next_v_node,
                             lead_time=lead_time,
                             relationship='assembly-component')

    return TSN


def visualize_time_space_network(TSN, title="Time-Space Network"):
    """
    Visualize the time-space network.

    Parameters:
    -----------
    TSN : networkx.DiGraph
        Time-space network to visualize
    title : str
        Title for the plot
    """
    plt.figure(figsize=(14, 10))

    # Create node positions - time on x-axis, original node on y-axis
    pos = {}
    orig_node_map = {}

    # Map original nodes to y-positions
    for node in TSN.nodes:
        orig_node = TSN.nodes[node]['original_node']
        if orig_node not in orig_node_map:
            orig_node_map[orig_node] = len(orig_node_map)

    # Set node positions
    for node in TSN.nodes:
        orig_node = TSN.nodes[node]['original_node']
        time = TSN.nodes[node]['time']
        pos[node] = (time, orig_node_map[orig_node])

    # Color nodes by event type
    event_types = set(nx.get_node_attributes(TSN, 'event_type').values())
    color_map = {}
    colors = plt.cm.tab10(np.linspace(0, 1, len(event_types)))

    for i, event_type in enumerate(event_types):
        color_map[event_type] = colors[i]

    node_colors = [color_map[TSN.nodes[node]['event_type']] for node in TSN.nodes]

    # Draw the graph
    nx.draw_networkx_nodes(TSN, pos, node_size=500, node_color=node_colors, alpha=0.8)
    nx.draw_networkx_edges(TSN, pos, width=1.0, arrows=True)

    # Add node labels
    labels = {node: f"{TSN.nodes[node]['original_node']}\n(t={TSN.nodes[node]['time']:.1f})"
              for node in TSN.nodes}
    nx.draw_networkx_labels(TSN, pos, labels=labels, font_size=8)

    # Add legend for event types
    from matplotlib.patches import Patch
    legend_elements = [Patch(color=color, label=event_type)
                       for event_type, color in color_map.items()]
    plt.legend(handles=legend_elements, loc='upper right')

    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    return plt