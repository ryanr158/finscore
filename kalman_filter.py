import numpy as np
import matplotlib.pyplot as plt

def kalman(mi,me,ms,age,rt,roth,k401,sp500):
    # Define Kalman filter parameters
    initial_state = np.array([mi, me, ms, age, rt, roth, k401, sp500])  # Initial state: [monthly_income, monthly_expenses, monthly_savings, age, risk_tolerance, roth_ira, k401, sp500]
    initial_covariance = np.eye(8) * 1.0  # Initial covariance matrix
    process_noise = np.eye(8) * 0.1  # Process noise covariance
    measurement_noise = 1.0  # Measurement noise variance

    # Simulated historical data for Roth IRA, 401(k), and S&P 500
    num_months = 60
    roth_ira = np.random.normal(5000, 1000, num_months)
    k401 = np.random.normal(10000, 2000, num_months)
    sp500 = np.random.normal(2000, 500, num_months)

    # Provided inputs
    monthly_income = np.full(num_months, 20000)
    monthly_expenses = np.full(num_months, 10000)
    monthly_savings = np.full(num_months, 10000)
    age = np.full(num_months, 24)
    risk_tolerance = np.linspace(0.0, 1.0, num_months)  # Adjusted risk tolerance range

    # Kalman filter initialization
    current_state = initial_state
    current_covariance = initial_covariance

    # Initialize lists to store states and scores
    filtered_states = []
    predicted_states = []
    scores = []

    # Adjusted weights for each measurement
    weights = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.15, 0.15, 0.2])  # Adjust weights based on interpretation

    # Kalman filter loop
    for i in range(num_months):
        # Prediction step
        predicted_state = current_state
        predicted_covariance = current_covariance + process_noise

        # Update step for each measurement
        measurements = np.array([
            monthly_savings[i], monthly_income[i], monthly_expenses[i], age[i], risk_tolerance[i],
            roth_ira[i], k401[i], sp500[i]
        ])
        kalman_gains = current_covariance.diagonal() / (current_covariance.diagonal() + measurement_noise)
        current_state = predicted_state + kalman_gains * (measurements - predicted_state)
        current_covariance = np.diag(1 - kalman_gains) * predicted_covariance

        # Calculate the aggregated score
        score = np.dot(current_state, weights)
        scores.append(score)

        # Store results for plotting
        filtered_states.append(current_state.copy())
        predicted_states.append(predicted_state.copy())

    # Convert lists to NumPy arrays for plotting
    filtered_states = np.array(filtered_states)
    predicted_states = np.array(predicted_states)

    # Plotting Results
    plt.figure(figsize=(12, 6))

    plt.plot(scores, label='Financial Score', linestyle='-', marker='o')

    plt.xlabel('Month')
    plt.ylabel('Financial Score')
    plt.legend()
    plt.title('Kalman Filter for Financial Metrics Prediction with Adjusted Financial Score')
    plt.show()
        