from flask import Flask, render_template, request
app = Flask(__name__)
#from my_functions import shortest_path
import my_functions
# Dummy functions for path and delay
def path(option):
    if option == "shortest":
        return my_functions.shortest_path()
    elif option == "longest":
        return my_functions.longest_path()

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        if request.form.get("action") == "shortest":
            result = path("shortest")
        elif request.form.get("action") == "longest":
            result = path("longest")
        elif request.form.get("action") == "delay":
            result = my_functions.best_delay_config()
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)

