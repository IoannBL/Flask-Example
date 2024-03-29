from flask import Flask
from flask import render_template
from markupsafe import escape

from collections import Counter
from itertools import product

from functools import reduce
import operator

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<h1> Hello World </h1>"


@app.route("/home")
def hello_home():
    return "<h1> Hello Home </h1>"


names = {0: "Vasya", 1: "Petya", 2: "Anya"}


@app.route("/user/<int:_id>")
def hello_user_id(_id):
    if _id in names:
        return f"<h1> Hello {names[_id]} </h1>"
    return f"<h1> Hello Unknown </h1>"


@app.route("/user/<name>")
def hello_user(name):
    return f"<h1> Hello {escape(name)} </h1>"


@app.route("/alert")
def hello_alert():
    param = '<script>alert("bad")</script>'
    return f"<h1> Hello {escape(param)} </h1>"


@app.route("/number/<int:number>")
def hello_number(number):
    _n = number
    if _n < 2:
        return render_template("base.html", number=number)

    prime_dividers = []
    divider = 2
    while _n ** (1/2) >= divider:
        if _n % divider == 0:
            prime_dividers.append(divider)
            _n //= divider
        else:
            divider += 1
    if _n > 1:
        prime_dividers.append(_n)

    if len(prime_dividers) == 1:
        return render_template("number_prime.html", number=number)
    else:
        c = Counter(prime_dividers)
        # c = {2: 4, 3: 1, 5: 2} 1200 = 2*2*2*2*3*5*5
        # iterators = [[2, 4, 8, 16], [3], [5, 25]]
        iterators = [[prime ** l for l in range(0, count+1)] for prime, count in c.items()]
        dividers = [reduce(operator.mul, items, 1) for items in product(*iterators)]
        dividers.sort()
        return render_template("number_not_prime.html", number=number, dividers=dividers)


app.run("localhost", "8000")
