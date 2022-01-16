import prodigy
from prodigy.components.loaders import CSV
from prodigy.components.db import connect

@prodigy.recipe(
    "semanticsearch",
    dataset=("The dataset to use", "positional", None, str)
)
def semanticsearch(
        dataset: str):

    db = connect()
    input_hashes = db.get_input_hashes(dataset)

    def filter_stream(stream, input_hashes):
        for eg in stream:
            eg = prodigy.set_hashes(eg)
            if eg["_input_hash"] not in input_hashes:
                yield eg

    stream = CSV('./data/data.csv')
    stream = filter_stream(stream, input_hashes)

    blocks = [
        {"view_id": "html",
         "html_template": "<div style='background-color:SlateBlue;'><h1 style='color:White;'>{{label}}</h1></div>"},
        {"view_id": "html", "html_template": "<div>{{text}}</div>"}
    ]

    return {
        "view_id": "blocks",  # Annotation interface to use
        "dataset": dataset,  # Name of dataset to save annotations
        "stream": stream,  # Incoming stream of examples
        "config": {"blocks": blocks}
    }