from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/analytics", methods=["POST"])
def write_to_file():  # this whole function is a trainwreck, but i wanted to upload it to maintain transparency
    to_export = {"os": request.form.get("os"),"v": request.form.get("v"), "id": request.form.get("id")}
    with open("data.json", "r") as inp:
        data_t = json.load(inp)
        inp.close()
    data_t["data"].append(to_export)
    with open("data.json", "w") as out:
        json.dump(data_t, out)
        out.close()
    return 200  # spoiler, it returns 200 no matter what


if __name__ == "__main__":
    app.run(debug=True)