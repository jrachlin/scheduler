from flask import Flask, render_template, request

from config import get_live_instances

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def hello_world():

    if request.method == 'POST':
        #instance_name = request.form['instanceName']
        print(request.form)
        #print(instance_name)

    instances = get_live_instances()

    live = [(i, k[1]) for i, k in enumerate(instances)]
    if len(instances) == 0:
        selected = 'None'
    else:
        pass

    return render_template('base.html', selected=selected, live=live)