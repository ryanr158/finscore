import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

def kalman(mi, me, ms, age, rt, roth, k401):
    # Fetch S&P 500 historical data
    sp500_data = yf.Ticker("^GSPC")
    sp500_history = sp500_data.history(period="1mo")  # Adjust period as needed
    sp500 = sp500_history["Close"].values  # Use closing values

    # Define Kalman filter parameters
    num_months = len(sp500)  # Number of months based on S&P 500 data
    initial_state = np.array([mi, me, ms, age, rt, roth, k401, sp500[0]])  # Initial state with initial S&P 500 value
    initial_covariance = np.eye(8) * 1.0
    process_noise = np.eye(8) * 0.1
    measurement_noise = 1.0

    # Initialize Kalman filter
    current_state = initial_state
    current_covariance = initial_covariance
    scores = []

    # Adjusted weights for each measurement
    weights = np.array([0.15, 0.1, 0.1, 0.05, 0.1, 0.15, 0.15, 0.2])  # Adjust weights based on interpretation

    for i in range(num_months):
        # Prediction step
        predicted_state = current_state
        predicted_covariance = current_covariance + process_noise

        # Update step with measurements
        measurements = np.array([
            ms, mi, me, age, rt, roth, k401, sp500[i]
        ])
        kalman_gains = current_covariance.diagonal() / (current_covariance.diagonal() + measurement_noise)
        current_state = predicted_state + kalman_gains * (measurements - predicted_state)
        current_covariance = np.diag(1 - kalman_gains) * predicted_covariance

        # Calculate the financial score
        score = np.dot(current_state, weights)
        scores.append(score)

    # Plotting the results
    plt.figure(figsize=(12, 6))
    plt.plot(scores, label='Financial Score', linestyle='-', marker='o')
    plt.xlabel('Month')
    plt.ylabel('Financial Score')
    plt.legend()
    plt.title('Kalman Filter for Financial Metrics Prediction with Adjusted Financial Score')
    plt.show()

    return scores[-1]

# Example usage of the function with initial parameters
final_score = kalman(mi=20000, me=10000, ms=10000, age=30, rt=0.5, roth=5000, k401=10000)
print("Final financial score:", final_score)