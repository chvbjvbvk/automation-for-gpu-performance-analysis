import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib

# Define paths for data collection and model storage
HISTORICAL_DATA_PATH = 'historical_data.csv'
MODEL_PATH = 'performance_model.pkl'

def preprocess_data():
    # Load historical data
    data = pd.read_csv(HISTORICAL_DATA_PATH)
    # Perform necessary preprocessing steps (e.g., handling missing values, normalization)
    data = data.dropna()
    return data

def train_model():
    data = preprocess_data()
    # Define feature columns and target column
    feature_cols = ['hash_enabled', 'gc_clock_freq', 'sbm_clock_freq', 'wr_rd_latency']
    target_col = 'performance_metric'
    
    X = data[feature_cols]
    y = data[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Model Mean Squared Error: {mse}")
    
    # Save the trained model
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

def load_model():
    # Load the trained model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"Model loaded from {MODEL_PATH}")
        return model
    else:
        print("No pre-trained model found. Training a new model...")
        train_model()
        return joblib.load(MODEL_PATH)

if __name__ == "__main__":
    train_model()
