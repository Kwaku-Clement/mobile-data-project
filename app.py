from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import re

app = Flask(__name__)
app.secret_key = "razilhub_secret_key"

# Simulated wallet (for demo)
user_wallet = {"balance": 50.00}

# ----------------------------
# LOGIN PAGE
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()

        # Normalize +233 format to local 0 format
        if phone.startswith("+233"):
            phone = "0" + phone[4:]

        # Ghana valid prefixes
        ghana_pattern = re.compile(r"^0(20|23|24|25|26|27|28|29|50|53|54|55|56|57|58|59)\d{7}$")

        if not ghana_pattern.match(phone):
            flash("❌ Please enter a valid Ghana mobile number (e.g. 0541234567 or +233541234567)", "error")
            return render_template("login.html")

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        session["otp"] = otp
        session["phone"] = phone

        # Show OTP on screen for demo
        flash(f"📱 OTP for {phone} is: {otp}", "success")
        flash("✅ Please verify to continue.", "info")
        return redirect(url_for("verify"))

    return render_template("login.html")

# ----------------------------
# VERIFY PAGE
# ----------------------------
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()
        correct_otp = session.get("otp")

        if entered_otp == correct_otp:
            flash(" Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("❌ Invalid OTP. Please try again.", "error")

    return render_template("verify.html")

# ----------------------------
# DASHBOARD
# ----------------------------
@app.route("/dashboard")
def dashboard():
    if "phone" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    balance = user_wallet["balance"]
    return render_template("dashboard.html", balance=balance)

# ----------------------------
# DATA SERVICES PAGE
# ----------------------------
@app.route("/data")
def data():
    if "phone" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    balance = user_wallet["balance"]
    return render_template("data_services.html", balance=balance)

# ----------------------------
# BUY DATA PAGE (ADD THIS MISSING ROUTE)
# ----------------------------
@app.route("/buy_data_page")
def buy_data_page():
    if "phone" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    balance = user_wallet["balance"]
    return render_template("buy_data.html", balance=balance)

# ----------------------------
# OTHER SERVICES
# ----------------------------
@app.route("/car_wash")
def car_wash():
    return render_template("car_wash.html")

@app.route("/delivery")
def delivery():
    return render_template("delivery.html")

@app.route("/food")
def food():
    return render_template("food.html")

# ----------------------------
# BUY DATA (FIXED - REMOVED DUPLICATE LINES)
# ----------------------------
@app.route("/buy_data", methods=["POST"])
def buy_data():
    network = request.form.get("network")
    price = float(request.form.get("price", 0))
    recipient = request.form.get("recipient", "")

    # Validate recipient number format
    ghana_pattern = re.compile(r"^0(20|23|24|25|26|27|28|29|50|53|54|55|56|57|58|59)\d{7}$")

    if not recipient or not ghana_pattern.match(recipient):
        flash("❌ Please enter a valid Ghana mobile number", "error")
        return redirect(url_for("buy_data_page"))

    if price <= 0:
        flash("❌ Invalid package selected.", "error")
        return redirect(url_for("buy_data_page"))

    if user_wallet["balance"] < price:
        flash("❌ Insufficient balance. Please deposit to continue.", "error")
        return redirect(url_for("buy_data_page"))

    # Deduct and confirm
    user_wallet["balance"] -= price

    # Map prices to data amounts for confirmation message
    data_plans = {
        10: "1GB", 18: "2GB", 40: "5GB",  # MTN
        9: "1GB", 25: "3GB", 40: "5GB",   # Telecel
        8: "1GB", 22: "3GB", 35: "5GB"    # AirtelTigo
    }

    plan = data_plans.get(price, f"GHS {price}")
    flash(f" Successfully purchased {plan} {network} data for {recipient} at GHS {price:.2f}!", "success")
    return redirect(url_for("buy_data_page"))

# ----------------------------
# DEPOSIT
# ----------------------------
@app.route("/deposit", methods=["POST"])
def deposit():
    amount = float(request.form.get("amount", 0))
    if amount <= 0:
        flash("Enter a valid deposit amount.", "error")
    else:
        user_wallet["balance"] += amount
        flash(f"Deposited GHS {amount:.2f} successfully.", "success")
    return redirect(url_for("dashboard"))

# ----------------------------
# WITHDRAW
# ----------------------------
@app.route("/withdraw", methods=["POST"])
def withdraw():
    amount = float(request.form.get("amount", 0))
    if amount <= 0:
        flash("Enter a valid withdrawal amount.", "error")
    elif amount > user_wallet["balance"]:
        flash("Insufficient balance for withdrawal.", "error")
    else:
        user_wallet["balance"] -= amount
        flash(f"Withdrew GHS {amount:.2f} successfully.", "success")
    return redirect(url_for("dashboard"))

# ----------------------------
# MAIN ENTRY POINT
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)