from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql
from PIL import Image
import io
from flask import send_file, render_template

import uuid

app = Flask("Form_Submission")

db_config = {'host': 'dpg-csfn4jg8fa8c73a0r4jg-a',
        'user': 'user',
        'password': '1RlVgjGFv4zunjyX6XJHQZKxFdb3XN0J',
        'dbname': 'form_submission_f4ny',
        'port': 5432
}

# Database connection
conn = psycopg2.connect(**db_config)

# Create table
with conn.cursor() as cur:
    cur.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id SERIAL PRIMARY KEY,
        submission_id UUID NOT NULL,
        name TEXT,
        contact_number TEXT,
        email TEXT,
        image BYTEA
    )
    """)
    conn.commit()

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
    name = request.form['name']
    contact_number = request.form['contact_number']
    email = request.form['email']
    image_file = request.files['image']

    # Generate a unique submission ID
    submission_id = uuid.uuid4()

    # Convert image to binary format
    image_data = io.BytesIO()
    image = Image.open(image_file)
    image.save(image_data, format=image.format)
    image_data = image_data.getvalue()

    # Insert data into database
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("INSERT INTO submissions (submission_id, name, contact_number, email, image) VALUES (%s, %s, %s, %s, %s)"),
            [str(submission_id), name, contact_number, email, psycopg2.Binary(image_data)]
        )

        conn.commit()

    return jsonify({"submission_id": str(submission_id)}), 201


@app.route('/view_image/<submission_id>', methods=['GET'])
def view_image(submission_id):
    with conn.cursor() as cur:
        cur.execute("SELECT image FROM submissions WHERE submission_id = %s", (submission_id,))
        result = cur.fetchone()

    if result is None:
        return "Image not found", 404

    image_data = result[0]
    image = io.BytesIO(image_data)

    return send_file(image, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(debug=True)
