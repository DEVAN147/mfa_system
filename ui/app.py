# ui/app.py

from flask import Flask, render_template, request, redirect, url_for, session
from mfa_authentication import MFAAuthentication
from adaptive_authentication import AdaptiveAuthentication
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Load user data (for simplicity, load from CSV)
user_df = pd.read_csv('../mfa_simulated_data.csv')

# Initialize Adaptive Authentication Model
adaptive_auth = AdaptiveAuthentication('../mfa_analyzed_data.csv')
adaptive_auth.load_model()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['username']
        password = request.form['password']
        user_record = user_df[user_df['UserID'] == user_id].iloc[0] if not user_df[user_df['UserID'] == user_id].empty else None
        if user_record:
            mfa = MFAAuthentication(user_record)
            if mfa.verify_password(password):
                session['user_id'] = user_id
                # Determine if additional authentication is needed
                user_features = {
                    'DeviceType': user_record['DeviceType'],
                    'OperatingSystem': user_record['OperatingSystem'],
                    'Browser': user_record['Browser'],
                    'AuthMethod': user_record['AuthMethod'],
                    'Hour': pd.to_datetime(user_record['Timestamp']).hour,
                    'DayOfWeek': pd.to_datetime(user_record['Timestamp']).dayofweek
                }
                anomaly = adaptive_auth.predict_anomaly(user_features)
                session['anomaly'] = anomaly
                if anomaly:
                    return redirect(url_for('additional_auth'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid Credentials')
        else:
            return render_template('login.html', error='User not found')
    return render_template('login.html')

@app.route('/additional_auth', methods=['GET', 'POST'])
def additional_auth():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    user_record = user_df[user_df['UserID'] == user_id].iloc[0]
    auth_method = user_record['AuthMethod']
    if request.method == 'POST':
        credential = request.form['credential']
        mfa = MFAAuthentication(user_record)
        if mfa.authenticate(auth_method, credential):
            return redirect(url_for('dashboard'))
        else:
            return render_template('additional_auth.html', error='Authentication Failed', auth_method=auth_method)
    return render_template('additional_auth.html', auth_method=auth_method)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        feedback = request.form['feedback']
        # Save feedback (for simplicity, append to a CSV)
        with open('../feedback.csv', 'a') as f:
            f.write(f"{session['user_id']},{feedback}\n")
        return render_template('feedback.html', message='Thank you for your feedback!')
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # Ensure the working directory is correct
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app.run(debug=True)
