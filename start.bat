call conda activate ML
set FLASK_APP=webApp.py
set FLASK_ENV=development
start chrome http://127.0.0.1:5000/
flask run