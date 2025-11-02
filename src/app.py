"""
app.py
Main application file for the expense tracker.
Sets up Flask routes and handles incoming requests.
"""

# Import necessary libraries
import os
from flask import Flask, request, jsonify, render_template
from src.api.sheets_service import append_expense_row
import logging

logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__, template_folder='templates') 

# ---------------------------------------------------------------
# Route to render the expense entry form
# ---------------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# ---------------------------------------------------------------
# Route to handle expense submission
# ---------------------------------------------------------------
@app.route('/add_expense', methods=['POST'])
def add_expense():
    try:
        # Parse JSON request body
        data = request.get_json()
        product_name = data.get('product_name')
        amount = data.get('amount')
        month = data.get('month')

        # Validate input data
        if not all([product_name, amount, month]):
            return jsonify({"status": "error", "message": "Missing product name, amount, or month"}), 400

        # Append the expense row to Google Sheets
        append_expense_row(product_name, amount, month)

        # Return success response
        return jsonify({"status": "success", "message": "Expense recorded successfully!"})

    

    except Exception as e:
        logging.exception("An error occurred while processing an expense submission.")
        return jsonify({"status": "error", "message": f"Server error: {e}"}), 500

# ---------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------
if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
