import gradio as gr
from search import Search

search = Search("config.yaml")

with gr.Blocks() as demo:
    gr.Markdown("Search fairness paper using this demo.")
    with gr.Tabs():
        with gr.TabItem("Title Search"):
            title_input = gr.Textbox(label="Input Title")
            title_dropdown = gr.Dropdown([5, 10, 20, 30, 40, 50], label="Top K")
            title_button = gr.Button("Search")
            title_output = gr.Dataframe()
        with gr.TabItem("Abstract Search"):
            abst_input = gr.Textbox(label="Input Abstract")
            abst_dropdown = gr.Dropdown([5, 10, 20, 30, 40, 50], label="Top K")
            abst_button = gr.Button("Search")
            abst_output = gr.Dataframe()

    title_button.click(
        search.search_title, inputs=[title_input, title_dropdown], outputs=title_output
    )
    abst_button.click(
        search.search_abst, inputs=[abst_input, abst_dropdown], outputs=abst_output
    )

demo.launch()
