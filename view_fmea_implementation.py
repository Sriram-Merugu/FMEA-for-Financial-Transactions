import networkx as nx
import plotly.graph_objects as go
from neo4j import GraphDatabase
import webbrowser


def visualize_graph(driver):
    """
    Query transactions and relationships from Neo4j, build a NetworkX graph,
    and generate a Plotly figure. High Risk transactions are shown in red; others in blue.
    """
    query = """
    MATCH (t:Transaction)
    OPTIONAL MATCH (t)-[r]->(t2:Transaction)
    RETURN t.Transaction_ID as source, t.RPN as source_rpn, t.failure_mode as source_mode, 
           t2.Transaction_ID as target, t2.RPN as target_rpn, t2.failure_mode as target_mode, 
           type(r) as rel_type
    """
    nodes = {}
    edges = []

    with driver.session() as session:
        results = session.run(query)
        for record in results:
            src = record["source"]
            if src not in nodes:
                nodes[src] = {
                    "RPN": record["source_rpn"],
                    "failure_mode": record["source_mode"]
                }
            tgt = record["target"]
            if tgt is not None:
                if tgt not in nodes:
                    nodes[tgt] = {
                        "RPN": record["target_rpn"],
                        "failure_mode": record["target_mode"]
                    }
                edges.append((src, tgt, record["rel_type"]))

    # Build a directed graph using NetworkX
    G = nx.DiGraph()
    for node, attr in nodes.items():
        G.add_node(node, RPN=attr["RPN"], failure_mode=attr["failure_mode"])
    for edge in edges:
        G.add_edge(edge[0], edge[1], label=edge[2])

    # Use a spring layout for positioning
    pos = nx.spring_layout(G, seed=42)

    # Build edge traces for Plotly
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Build node traces with color coding based on failure_mode
    node_x = []
    node_y = []
    node_color = []
    node_text = []
    for node, attr in G.nodes(data=True):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_color.append("red" if attr["failure_mode"] == "High Risk" else "blue")
        node_text.append(f"ID: {node}<br>RPN: {attr['RPN']}<br>Mode: {attr['failure_mode']}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        marker=dict(
            color=node_color,
            size=10,
            line_width=2
        ),
        text=node_text,
        hoverinfo='text'
    )

    # Updated layout using new title structure
    layout = go.Layout(
        title=dict(text='Transaction Graph with FMEA Results', font=dict(size=16)),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=[dict(
            text="Red nodes indicate High Risk transactions",
            showarrow=False,
            xref="paper", yref="paper",
            x=0.005, y=-0.002
        )],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
    return fig


def main():
    # Update these connection variables as needed
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"  # Replace with your Neo4j password

    # Create the Neo4j driver instance
    driver = GraphDatabase.driver(uri, auth=(user, password))

    # Generate the graph figure using the visualization function
    fig = visualize_graph(driver)

    # Save the figure to an HTML file and open it in the default browser
    output_file = "assets/transaction_graph.html"
    fig.write_html(output_file)
    print(f"Graph saved to {output_file}. Opening in default browser...")
    webbrowser.open(output_file)

    driver.close()


if __name__ == "__main__":
    main()
