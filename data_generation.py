# data_generation.py

from faker import Faker
import numpy as np
import pandas as pd
import random
import bcrypt
import pyotp

fake = Faker()

def generate_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def generate_data(num_users=1000, login_attempts_per_user=10):
    data = []
    for _ in range(num_users):
        user_id = fake.unique.user_name()
        password = fake.password(length=10)
        password_hash = generate_password_hash(password)
        for _ in range(login_attempts_per_user):
            timestamp = fake.date_time_this_year()
            success = random.choices([True, False], weights=[0.8, 0.2])[0]  # 80% success rate
            device_type = random.choice(['Mobile', 'Desktop', 'Tablet'])
            os = random.choice(['Windows', 'macOS', 'Linux', 'Android', 'iOS'])
            browser = random.choice(['Chrome', 'Firefox', 'Safari', 'Edge'])
            location = fake.city()
            auth_method = random.choices(
                ['Password', 'OTP', 'Biometric'],
                weights=[0.6, 0.3, 0.1],
                k=1
            )[0]
            otp = pyotp.TOTP('base32secret3232').now() if auth_method == 'OTP' else None
            biometric_pattern = fake.password(length=6) if auth_method == 'Biometric' else None
            data.append([
                user_id, password_hash.decode('utf-8'), timestamp, success, device_type,
                os, browser, location, auth_method, otp, biometric_pattern
            ])
    df = pd.DataFrame(data, columns=[
        'UserID', 'PasswordHash', 'Timestamp', 'Success', 'DeviceType',
        'OperatingSystem', 'Browser', 'Location', 'AuthMethod', 'OTP', 'BiometricPattern'
    ])
    df.to_csv('mfa_simulated_data.csv', index=False)
    print("Data generation complete. Saved to mfa_simulated_data.csv")

if __name__ == "__main__":
    generate_data()
