from flask import Flask, jsonify

from passport_service import BadRequestError, NotFoundError, generate_data_passport

app = Flask(__name__)


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
