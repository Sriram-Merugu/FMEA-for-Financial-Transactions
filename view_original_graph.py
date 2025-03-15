import networkx as nx
import plotly.graph_objects as go
from neo4j import GraphDatabase
import webbrowser


def visualize_transactions(driver):
    """
    Query Transaction nodes and only the NEXT and SIMILAR relationships from Neo4j.
    Build a NetworkX graph and generate a Plotly figure.
    Nodes are all colored blue.
    NEXT edges are colored green, SIMILAR edges are colored orange.
    """
    query = """
    MATCH (t:Transaction)-[r]->(t2:Transaction)
    WHERE type(r) IN ['NEXT', 'SIMILAR']
    RETURN t.Transaction_ID as source, 
           type(r) as rel_type, 
           t2.Transaction_ID as target
    """
    nodes = {}
    edges = []

    with driver.session() as session:
        results = session.run(query)
        for record in results:
            src = record["source"]
            tgt = record["target"]
            rel_type = record["rel_type"]

            # Add source and target nodes (if not already added)
            if src not in nodes:
                nodes[src] = {}
            if tgt not in nodes:
                nodes[tgt] = {}

            edges.append((src, tgt, rel_type))

    # Build the directed graph using NetworkX
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node)
    for edge in edges:
        G.add_edge(edge[0], edge[1], rel_type=edge[2])

    # Position nodes using a spring layout
    pos = nx.spring_layout(G, seed=42)

    # Build edge traces: color-code by relationship type
    edge_x = []
    edge_y = []
    edge_colors = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        # Choose color based on relationship type
        if edge[2]['rel_type'] == "NEXT":
            edge_colors.append("green")
        elif edge[2]['rel_type'] == "SIMILAR":
            edge_colors.append("orange")
        else:
            edge_colors.append("gray")

    # For simplicity, use one color for each edge type.
    # We'll create two separate traces: one for NEXT edges and one for SIMILAR edges.
    next_edge_x, next_edge_y = [], []
    similar_edge_x, similar_edge_y = [], []

    with driver.session() as session:
        results = session.run(query)
        for record in results:
            src = record["source"]
            tgt = record["target"]
            rel_type = record["rel_type"]
            x0, y0 = pos[src]
            x1, y1 = pos[tgt]
            if rel_type == "NEXT":
                next_edge_x.extend([x0, x1, None])
                next_edge_y.extend([y0, y1, None])
            elif rel_type == "SIMILAR":
                similar_edge_x.extend([x0, x1, None])
                similar_edge_y.extend([y0, y1, None])

    next_edge_trace = go.Scatter(
        x=next_edge_x, y=next_edge_y,
        line=dict(width=1, color='green'),
        hoverinfo='none',
        mode='lines',
        name="NEXT"
    )

    similar_edge_trace = go.Scatter(
        x=similar_edge_x, y=similar_edge_y,
        line=dict(width=1, color='orange'),
        hoverinfo='none',
        mode='lines',
        name="SIMILAR"
    )

    # Build node trace (all nodes in blue)
    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"Transaction ID: {node}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        marker=dict(
            color='blue',
            size=10,
            line_width=2
        ),
        text=node_text,
        hoverinfo='text'
    )

    layout = go.Layout(
        title=dict(text="Original Transaction Graph (NEXT & SIMILAR Relationships)", font=dict(size=16)),
        showlegend=True,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    fig = go.Figure(data=[next_edge_trace, similar_edge_trace, node_trace], layout=layout)
    return fig


def main():
    # Update connection details as needed
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"  # Replace with your Neo4j password

    driver = GraphDatabase.driver(uri, auth=(user, password))

    fig = visualize_transactions(driver)
    # Save the figure to an HTML file and open it in the default browser
    output_file = "assets/original_graph.html"
    fig.write_html(output_file)
    print(f"Graph saved to {output_file}. Opening in default browser...")
    webbrowser.open(output_file)

    driver.close()


if __name__ == "__main__":
    main()
