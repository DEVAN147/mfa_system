# adaptive_authentication.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

class AdaptiveAuthentication:
    def __init__(self, analyzed_data_path='mfa_analyzed_data.csv'):
        self.df = pd.read_csv(analyzed_data_path)
        self.model = None
        self.prepare_data()

    def prepare_data(self):
        # Define features and target
        features = ['DeviceType', 'OperatingSystem', 'Browser', 'AuthMethod', 'Hour', 'DayOfWeek']
        self.X = self.df[features]
        self.y = self.df['Anomaly']

    def train_model(self):
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        accuracy = self.model.score(X_test, y_test)
        print(f"Adaptive Authentication Model Accuracy: {accuracy:.2f}")
        # Save the model for later use
        joblib.dump(self.model, 'adaptive_auth_model.pkl')
        print("Model trained and saved as adaptive_auth_model.pkl")

    def load_model(self):
        self.model = joblib.load('adaptive_auth_model.pkl')

    def predict_anomaly(self, user_features):
        """
        user_features: dict containing feature values, e.g.,
        {
            'DeviceType': 1,
            'OperatingSystem': 2,
            'Browser': 0,
            'AuthMethod': 1,
            'Hour': 14,
            'DayOfWeek': 2
        }
        """
        if not self.model:
            self.load_model()
        df = pd.DataFrame([user_features])
        prediction = self.model.predict(df)[0]
        return prediction  # 1 indicates anomaly, 0 indicates normal

if __name__ == "__main__":
    aa = AdaptiveAuthentication()
    aa.train_model()
