import os

def save_graph_image(app, file_path="graph.png"):
    """
    Takes a compiled LangGraph app and saves the architecture as an image.
    """
    try:
        # LangGraph provides a get_graph() method
        graph_png = app.get_graph().draw_mermaid_png()
        with open(file_path, "wb") as f:
            f.write(graph_png)
        print(f"✅ Graph visualization saved to {file_path}")
    except Exception as e:
        print(f"⚠️ Could not save graph image: {e}")
        print("Note: Ensure 'pygraphviz' or 'mermaid' dependencies are installed.")