import gradio as gr
import os

port = int(os.environ.get("GRADIO_SERVER_PORT"))
host = os.environ.get("GRADIO_HOST")
root_path = f"/node/{host}/{port}"

def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)

demo = gr.Interface(
    fn=greet,
    inputs=["text", "slider"],
    outputs=["text"],
)

demo.launch(server_port=port, server_name="0.0.0.0", root_path=root_path)

