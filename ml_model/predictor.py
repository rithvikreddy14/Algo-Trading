# ml_model/predictor.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier # Or LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import pandas_ta as ta # For MACD and other indicators
import logging

logger = logging.getLogger(__name__)

def create_ml_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates features for the ML model from the stock data.
    Features include RSI, MACD components, Volume, and the target variable.

    Args:
        df (pd.DataFrame): DataFrame with 'close' prices and 'volume'.

    Returns:
        pd.DataFrame: DataFrame with added features and the 'next_day_movement' target.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.error("Input DataFrame is invalid or empty for ML feature creation.")
        return pd.DataFrame()

    df_copy = df.copy()

    # Calculate next day movement as target variable (1 if price goes up, 0 if down/same)
    df_copy['next_day_movement'] = (df_copy['close'].shift(-1) > df_copy['close']).astype(int)

    # Add technical indicators as features
    df_copy.ta.rsi(append=True) # RSI_14
    df_copy.ta.macd(append=True) # MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9

    # Drop rows with NaN values that result from indicator calculations or shift operations
    # This is crucial as ML models cannot handle NaNs
    df_copy.dropna(inplace=True)
    
    if df_copy.empty:
        logger.warning("DataFrame became empty after creating features and dropping NaNs.")

    return df_copy

def train_and_predict(data: pd.DataFrame) -> tuple[any, float] | tuple[None, None]:
    """
    Trains a simple Decision Tree model to predict next-day movement
    and evaluates its accuracy.

    Args:
        data (pd.DataFrame): DataFrame containing historical stock data with 'close' and 'volume'.

    Returns:
        tuple[any, float] | tuple[None, None]: A tuple containing the trained model and its accuracy,
                                               or (None, None) if training fails.
    """
    logger.info("Starting ML model training and prediction...")
    
    processed_df = create_ml_features(data)
    
    if processed_df.empty:
        logger.error("Cannot train ML model: Processed data is empty.")
        return None, None

    # Define features (X) and target (y)
    # Ensure these feature columns exist after `create_ml_features`
    features = ['RSI_14', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9', 'volume']
    target = 'next_day_movement'
    
    # Check if all required features exist in the DataFrame
    missing_features = [f for f in features if f not in processed_df.columns]
    if missing_features:
        logger.error(f"Missing required features for ML training: {missing_features}")
        return None, None

    X = processed_df[features]
    y = processed_df[target]

    # Split data into training and testing sets
    # Use stratify=y to maintain the same proportion of target classes in both sets
    if len(X) < 2: # Need at least 2 samples for train_test_split
        logger.warning(f"Not enough data points ({len(X)}) for ML training after feature creation. Skipping ML for this stock.")
        return None, None

    # Handle cases where a class might have only one sample (stratify would fail)
    if y.nunique() < 2:
        logger.warning("Target variable has only one class. Skipping stratified split.")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    if X_train.empty or X_test.empty:
        logger.warning("Training or testing set is empty. Skipping ML model.")
        return None, None

    try:
        # Initialize and train the Decision Tree Classifier model
        model = DecisionTreeClassifier(random_state=42)
        model.fit(X_train, y_train)
        
        # Make predictions on the test set
        predictions = model.predict(X_test)
        
        # Calculate accuracy
        accuracy = accuracy_score(y_test, predictions)
        
        logger.info(f"ML Model Training Complete. Accuracy: {accuracy:.4f}")
        logger.debug(f"Classification Report:\n{classification_report(y_test, predictions)}")
        
        return model, accuracy
    
    except Exception as e:
        logger.error(f"Error during ML model training or prediction: {e}")
        return None, None

if __name__ == "__main__":
    # This block runs only when predictor.py is executed directly
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    print("\n--- Testing ML Model Predictor ---")
    # Create a dummy DataFrame with enough data for indicators and ML
    data = {
        'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100],
        'high': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 101],
        'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99],
        'close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100],
        'volume': [100000] * 120
    }
    dates = pd.date_range(start='2024-01-01', periods=len(data['close']), freq='D')
    dummy_df = pd.DataFrame(data, index=dates)

    model, accuracy = train_and_predict(dummy_df)
    
    if model is not None and accuracy is not None:
        print(f"\nML Model trained. Accuracy: {accuracy:.2f}")
    else:
        print("\nML Model training failed or skipped.")
