from flask import Flask, jsonify, render_template_string

from passport_service import (
    BadRequestError,
    NotFoundError,
    format_identifier,
    generate_data_passport,
    load_data,
)

app = Flask(__name__)

INDEX_TEMPLATE = """
<!doctype html>
<title>Passport Playground</title>
<h1>Passport Playground</h1>
<ul>
{% for dataset in datasets %}
  <li><a href="{{ url_for('get_data_passport', dataset_identifier=dataset.identifier) }}">{{ dataset.identifier }} &mdash; {{ dataset.name }}</a></li>
{% endfor %}
</ul>
"""


@app.get("/")
def index():
    data = load_data()
    datasets = [
        {"identifier": format_identifier(d["alias"]), "name": d.get("name", "")}
        for d in data["datasets"]
    ]
    return render_template_string(INDEX_TEMPLATE, datasets=datasets)


@app.get("/api/passport/dataset/<dataset_identifier>")
def get_data_passport(dataset_identifier):
    try:
        passport = generate_data_passport(dataset_identifier)
        return jsonify(passport)
    except BadRequestError as e:
        return jsonify({"message": str(e)}), 400
    except NotFoundError as e:
        return jsonify({"message": str(e)}), 404


if __name__ == "__main__":
    app.run(debug=True, port=8080)
