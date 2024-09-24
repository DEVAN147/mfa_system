# user_behavior_analysis.py

import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns

class UserBehaviorAnalysis:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path, parse_dates=['Timestamp'])
        self.preprocess_data()

    def preprocess_data(self):
        # Feature Engineering
        self.df['Hour'] = self.df['Timestamp'].dt.hour
        self.df['DayOfWeek'] = self.df['Timestamp'].dt.dayofweek
        self.df['Success'] = self.df['Success'].astype(int)

        # Encode categorical variables
        self.df['DeviceType'] = self.df['DeviceType'].astype('category').cat.codes
        self.df['OperatingSystem'] = self.df['OperatingSystem'].astype('category').cat.codes
        self.df['Browser'] = self.df['Browser'].astype('category').cat.codes
        self.df['AuthMethod'] = self.df['AuthMethod'].astype('category').cat.codes

    def detect_anomalies(self):
        features = ['DeviceType', 'OperatingSystem', 'Browser', 'AuthMethod', 'Hour', 'DayOfWeek']
        X = self.df[features]
        model = IsolationForest(contamination=0.01, random_state=42)
        self.df['Anomaly'] = model.fit_predict(X)
        self.df['Anomaly'] = self.df['Anomaly'].map({1: 0, -1: 1})  # 1 indicates anomaly

    def visualize_anomalies(self):
        sns.scatterplot(x='Hour', y='DayOfWeek', hue='Anomaly', data=self.df, palette='coolwarm')
        plt.title('Anomaly Detection in User Login Patterns')
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
        plt.show()

    def save_analyzed_data(self):
        self.df.to_csv('mfa_analyzed_data.csv', index=False)
        print("Anomaly detection complete. Results saved to mfa_analyzed_data.csv")

if __name__ == "__main__":
    uba = UserBehaviorAnalysis('mfa_simulated_data.csv')
    uba.detect_anomalies()
    uba.visualize_anomalies()
    uba.save_analyzed_data()
