# EcoFields 🌱  
A sustainable e-commerce web application built with **Flask** and **MySQL**, promoting eco-friendly shopping and sustainable products.

---

## 🚀 Features
- Browse eco-friendly products
- Add items to cart
- User authentication (Login/Signup)
- MySQL database integration
- Clean and simple UI with Flask templates

---

## 🛠️ Tech Stack
- **Backend:** Python (Flask)
- **Frontend:** HTML, CSS (Jinja2 templates)
- **Database:** MySQL
- **ORM:** SQLAlchemy

---

## 📂 Project Structure
Ecofinds/
│── app.py # Main Flask application
│── templates/ # HTML templates (frontend)
│── static/ # CSS, JS, Images (if added)
│── requirements.txt # Python dependencies
│── README.md # Project documentation

yaml
Copy code

---

## ⚙️ Installation & Setup

Clone the repo
   ```bash
   git clone https://github.com/f4zill/Ecofinds.git
   cd Ecofinds
Create a virtual environment (optional but recommended)

bash
Copy code
python -m venv ecofinds-env
source ecofinds-env/bin/activate   # Linux/Mac
ecofinds-env\Scripts\activate      # Windows
Install dependencies

bash
Copy code
pip install -r requirements.txt
Set up MySQL database

Create a database (e.g., ecofinds_db)

Update database config inside app.py

Run the app

bash
Copy code
python app.py
Open http://127.0.0.1:5000 in your browser.
