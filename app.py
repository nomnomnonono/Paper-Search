import gradio as gr
from search import Search

search = Search("config.yaml")

with gr.Blocks() as demo:
    gr.Markdown("Search fairness paper using this demo.")
    with gr.Tabs():
        with gr.TabItem("Title Search"):
            with gr.Row():
                with gr.Column(scale=1):
                    title_input = gr.Textbox(label="Input Title")
                    title_dropdown = gr.Dropdown(
                        [5, 10, 20, 30, 40, 50], value="20", label="Top K"
                    )
                    title_button = gr.Button("Search")
                with gr.Column(scale=2):
                    title_output = gr.Dataframe()
        with gr.TabItem("Abstract Search"):
            with gr.Row():
                with gr.Column(scale=1):
                    abst_input = gr.Textbox(label="Input Abstract")
                    abst_dropdown = gr.Dropdown(
                        [5, 10, 20, 30, 40, 50], value="20", label="Top K"
                    )
                    abst_button = gr.Button("Search")
                with gr.Column(scale=2):
                    abst_output = gr.Dataframe()
        with gr.TabItem("Keyword Search"):
            with gr.Row():
                with gr.Column(scale=1):
                    keyword_target = gr.Radio(
                        ["Title", "Abstract"], value="Title", label="Search Target"
                    )
                    with gr.Row():
                        keyword_input1 = gr.Textbox(label="Keyword 1")
                        keyword_input2 = gr.Textbox(label="Keyword 2")
                        keyword_input3 = gr.Textbox(label="Keyword 3")
                    keyword_dropdown = gr.Dropdown(
                        [5, 10, 20, 30, 40, 50], value="20", label="Top K"
                    )
                    keyword_button = gr.Button("Search")
                with gr.Column(scale=2):
                    keyword_output = gr.Dataframe()

    title_button.click(
        search.search_title, inputs=[title_input, title_dropdown], outputs=title_output
    )
    abst_button.click(
        search.search_abst, inputs=[abst_input, abst_dropdown], outputs=abst_output
    )
    keyword_button.click(
        search.search_keyword,
        inputs=[
            keyword_input1,
            keyword_input2,
            keyword_input3,
            keyword_target,
            keyword_dropdown,
        ],
        outputs=keyword_output,
    )

demo.launch()
