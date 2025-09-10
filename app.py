from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    settlements = []
    if request.method == "POST":
        names = request.form.getlist("name")
        amounts = request.form.getlist("amount")

        expenses = []
        for name, amount in zip(names, amounts):
            try:
                amt = float(amount)
            except:
                amt = 0
            expenses.append({"name": name, "amount": amt})

        total = sum(exp["amount"] for exp in expenses)
        per_person = total / len(expenses) if expenses else 0

        balances = []
        for exp in expenses:
            balance = round(exp["amount"] - per_person, 2)
            balances.append({"name": exp["name"], "balance": balance})

        # Prepare settlements
        debtors = sorted([b for b in balances if b["balance"] < 0], key=lambda x: x["balance"])
        creditors = sorted([b for b in balances if b["balance"] > 0], key=lambda x: -x["balance"])

        d_idx = 0
        c_idx = 0

        while d_idx < len(debtors) and c_idx < len(creditors):
            debtor = debtors[d_idx]
            creditor = creditors[c_idx]

            debt = -debtor["balance"]
            credit = creditor["balance"]

            amount = round(min(debt, credit), 2)

            settlements.append({
                "from": debtor["name"],
                "to": creditor["name"],
                "amount": amount
            })

            debtor["balance"] += amount
            creditor["balance"] -= amount

            if round(debtor["balance"], 2) == 0:
                d_idx += 1
            if round(creditor["balance"], 2) == 0:
                c_idx += 1

        result = {
            "total": total,
            "per_person": per_person,
            "balances": balances
        }

    return render_template("index.html", result=result, settlements=settlements)

if __name__ == "__main__":
    app.run(debug=True)