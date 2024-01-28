import tkinter as tk
from tkinter import ttk 
import customtkinter
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import openai
from tkinter import messagebox
from kalman_filter import kalman

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("FinScore")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        number_of_rows = 50  
        for row_index in range(number_of_rows):
            self.sidebar_frame.grid_rowconfigure(row_index, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="FinScore", font=customtkinter.CTkFont(size=40, weight="bold", family="Bubblies"), text_color="#3C97DF")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))


        # Age input
        self.age_label = customtkinter.CTkLabel(self.sidebar_frame, text="Enter your age:", anchor="w")
        self.age_label.grid(row=1, column=0, padx=20, pady=(20, 0), sticky="w")
        self.age_entry = customtkinter.CTkEntry(self.sidebar_frame, font=customtkinter.CTkFont(size=14))
        self.age_entry.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")

        # Income input
        self.income_label = customtkinter.CTkLabel(self.sidebar_frame, text="Enter your monthly income:", anchor="w")
        self.income_label.grid(row=3, column=0, padx=20, pady=(20, 0), sticky="w")
        self.income_entry = customtkinter.CTkEntry(self.sidebar_frame, font=customtkinter.CTkFont(size=14))
        self.income_entry.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="w")

        # Risk tolerance slider
        self.risk_slider_label = customtkinter.CTkLabel(self.sidebar_frame, text="Set Risk Tolerance:", anchor="w")
        self.risk_slider_label.grid(row=5, column=0, padx=20, pady=(20, 0))
        self.slider_1 = customtkinter.CTkSlider(self.sidebar_frame, from_=0, to=1, number_of_steps=4)
        self.slider_1.grid(row=6, column=0, padx=(20, 10), pady=(0, 10), sticky="ew")

        # Display mode
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=46, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark"],
                                                                    command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=47, column=0, padx=20, pady=(10, 10))

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=1100, height=700)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Investing")
        self.tabview.add("Spending")
        self.tabview.add("Saving")
        self.tabview.add("Recommendations")
        self.tabview.tab("Investing").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabview.tab("Spending").grid_columnconfigure(0, weight=1)

        # set default values
        self.appearance_mode_optionemenu.set("Light")


        self.plot_canvas = customtkinter.CTkFrame(self.tabview.tab("Investing"))
        self.plot_canvas.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 10), sticky="nsew")

        self.plot_canvas2 = customtkinter.CTkFrame(self.tabview.tab("Spending"))
        self.plot_canvas2.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 10), sticky="nsew")

        self.plot_canvas3 = customtkinter.CTkFrame(self.tabview.tab("Saving"))
        self.plot_canvas3.grid(row=4, column=0, columnspan=6, padx=20, pady=(10, 10), sticky="nsew")

        self.canvas_reference_investing = None
        self.canvas_reference_spending = None
        self.canvas_reference_saving = None

        self.investments_data = {}
        self.risk_scores = {}

        self.expenses_data = {}
        self.saving_data = {}
        #self.total_data = {}

        self.create_investing_tab()
        self.create_spending_tab()
        self.create_saving_tab()
        self.create_recommendations_tab()


    def create_spending_tab(self):
        label_expense_description = customtkinter.CTkLabel(self.tabview.tab("Spending"), text="Enter expense description:", anchor="w")
        label_expense_description.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.expense_description_entry = customtkinter.CTkEntry(self.tabview.tab("Spending"), width=70,
                                                                font=customtkinter.CTkFont(size=14))
        self.expense_description_entry.grid(row=0, column=1, padx=0, pady=(20, 10), sticky="w")

        label_expense_category = customtkinter.CTkLabel(self.tabview.tab("Spending"), text="Select expense category and amount:", anchor="w")
        label_expense_category.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        self.expense_category_var = tk.StringVar()
        self.expense_category_var.set("Food")
        expense_categories = ["Food", "Housing", "Utilities", "Entertainment", "Transportation", "Tuition", "Loan Payments", "Other"]
        self.expense_category_menu = customtkinter.CTkOptionMenu(self.tabview.tab("Spending"), values=expense_categories,
                                                                font=customtkinter.CTkFont(size=14), variable=self.expense_category_var)
        self.expense_category_menu.grid(row=1, column=1, padx=0, pady=(0, 10), sticky="w")

        self.expense_amount_entry = customtkinter.CTkEntry(self.tabview.tab("Spending"), width=70,
                                                            font=customtkinter.CTkFont(size=14))
        self.expense_amount_entry.grid(row=2, column=1, padx=0, pady=(0, 10), sticky="w")

        self.add_expense_button = customtkinter.CTkButton(self.tabview.tab("Spending"), text="Add Expense",
                                                        command=self.add_expense_and_plot,
                                                        font=customtkinter.CTkFont(size=14))
        self.add_expense_button.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")

        self.clear_spending_button = customtkinter.CTkButton(self.tabview.tab("Spending"), text="Clear Spending",
                                                              command=self.clear_spending,
                                                              font=customtkinter.CTkFont(size=14))
        self.clear_spending_button.grid(row=2, column=0, columnspan=1, padx=(20,800), pady=(10, 20), sticky="nsew")

    def clear_spending(self):
        # Reset the investments data
        self.expenses_data.clear()

        # Clear the plot
        self.plot_pie_chart("Spending", [], [])

    def create_investing_tab(self):
        label_stock_symbol = customtkinter.CTkLabel(self.tabview.tab("Investing"), text="Enter stock symbol:", anchor="w")
        label_stock_symbol.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.stock_symbol_entry = customtkinter.CTkEntry(self.tabview.tab("Investing"), width=70,
                                                        font=customtkinter.CTkFont(size=14))
        self.stock_symbol_entry.grid(row=0, column=1, padx=0, pady=(20, 10), sticky="w")

        label_investment_type = customtkinter.CTkLabel(self.tabview.tab("Investing"), text="Select investment type and amount:", anchor="w")
        label_investment_type.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        self.investment_type_var = tk.StringVar()
        self.investment_type_menu = customtkinter.CTkOptionMenu(self.tabview.tab("Investing"), values=["Shares", "Dollars"],
                                                            font=customtkinter.CTkFont(size=14), variable=self.investment_type_var)
        self.investment_type_menu.grid(row=1, column=1, padx=0, pady=(0, 10), sticky="w")
        self.investment_type_var.set("Shares")

        self.investment_entry = customtkinter.CTkEntry(self.tabview.tab("Investing"), width=70,
                                                        font=customtkinter.CTkFont(size=14))
        self.investment_entry.grid(row=2, column=1, padx=0, pady=(0, 10), sticky="w")

        self.fetch_data_button = customtkinter.CTkButton(self.tabview.tab("Investing"), text="Add Stock",
                                                        command=self.fetch_data_and_plot,
                                                        font=customtkinter.CTkFont(size=14))
        self.fetch_data_button.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")

        self.clear_portfolio_button = customtkinter.CTkButton(self.tabview.tab("Investing"), text="Clear Portfolio",
                                                              command=self.clear_portfolio,
                                                              font=customtkinter.CTkFont(size=14))
        self.clear_portfolio_button.grid(row=2, column=0, columnspan=1, padx=(20,800), pady=(10, 20), sticky="nsew")
    
    def clear_portfolio(self):
        # Reset the investments data
        self.investments_data.clear()

        # Clear the plot
        self.plot_pie_chart("Investing", [], [])

    def create_saving_tab(self):
        # Configure grid columns for equal width
        for i in range(6):  # Adjust the range based on the number of columns you are using
            self.tabview.tab("Saving").grid_columnconfigure(i, weight=1)

        # Total Dollar Savings
        savings_label = customtkinter.CTkLabel(self.tabview.tab("Saving"), text="Total Cash Savings:", anchor="w")
        savings_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="e")
        self.savings_entry = customtkinter.CTkEntry(self.tabview.tab("Saving"), font=customtkinter.CTkFont(size=14))
        self.savings_entry.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="w")

        # Total Traditional 401k
        traditional_401k_label = customtkinter.CTkLabel(self.tabview.tab("Saving"), text="Total Traditional 401k:", anchor="w")
        traditional_401k_label.grid(row=0, column=3, padx=20, pady=10, sticky="e")
        self.traditional_401k_entry = customtkinter.CTkEntry(self.tabview.tab("Saving"), font=customtkinter.CTkFont(size=14))
        self.traditional_401k_entry.grid(row=0, column=4, padx=20, pady=10, sticky="w")

        # Total Roth
        roth_label = customtkinter.CTkLabel(self.tabview.tab("Saving"), text="Total Roth:", anchor="w")
        roth_label.grid(row=1, column=3, padx=20, pady=10, sticky="e")
        self.roth_entry = customtkinter.CTkEntry(self.tabview.tab("Saving"), font=customtkinter.CTkFont(size=14))
        self.roth_entry.grid(row=1, column=4, padx=20, pady=10, sticky="w")

        # Total Other Investments
        other_investments_label = customtkinter.CTkLabel(self.tabview.tab("Saving"), text="Total Other Investments:", anchor="w")
        other_investments_label.grid(row=1, column=0, padx=20, pady=10, sticky="e")
        self.other_investments_entry = customtkinter.CTkEntry(self.tabview.tab("Saving"), font=customtkinter.CTkFont(size=14))
        self.other_investments_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        # Button to plot savings data
        self.plot_savings_button = customtkinter.CTkButton(self.tabview.tab("Saving"), text="Plot Savings",
                                                        command=self.add_saving_and_plot,
                                                        font=customtkinter.CTkFont(size=14))
        self.plot_savings_button.grid(row=3, column=0, columnspan=6, padx=20, pady=(10, 20), sticky="nsew")
    
    def create_recommendations_tab(self):
        # Configure grid columns and rows
        for i in range(3):  # Using 3 columns
            self.tabview.tab("Recommendations").grid_columnconfigure(i, weight=1)

        for i in range(6):  # Using 6 rows
            self.tabview.tab("Recommendations").grid_rowconfigure(i, weight=1)

        # FinScore Button
        self.recommendations_button = customtkinter.CTkButton(
            self.tabview.tab("Recommendations"),
            text="Get FinScore!",
            command=self.get_recommendations,
            font=customtkinter.CTkFont(size=16)
        )
        self.recommendations_button.grid(row=0, column=1, sticky="nsew", padx=30, pady=10)

        # Riskiness Index Label
        self.riskiness_label = customtkinter.CTkLabel(self.tabview.tab("Recommendations"),
                                                    text="Portfolio Risk Score: ",
                                                    font=customtkinter.CTkFont(size=30, weight="bold"),
                                                    text_color="black")
        self.riskiness_label.grid(row=1, column=1, sticky="nsew", padx=0, pady=5)

        # Riskiness Index Description
        risk_index_description = "This index represents the overall risk level of your investment portfolio, ranging from 0 (low risk) to 1 (extremely high risk)."
        self.riskiness_description_label = customtkinter.CTkLabel(self.tabview.tab("Recommendations"),
                                                                text=risk_index_description,
                                                                font=customtkinter.CTkFont(size=15),
                                                                wraplength=500,
                                                                fg_color=None,
                                                                justify=tk.LEFT)
        self.riskiness_description_label.grid(row=2, column=1, sticky="nsew", padx=20, pady=(0, 70))

        # FinScore Label
        self.finscore_label = customtkinter.CTkLabel(self.tabview.tab("Recommendations"),
                                                    text="FinScore: ",
                                                    font=customtkinter.CTkFont(size=40, weight="bold"),
                                                    text_color="black")
        self.finscore_label.grid(row=3, column=1, sticky="nsew", padx=20, pady=(0, 5))

        # FinScore Description
        self.finscore_description = "Enter all your financial data to find your FinScore!"
        self.finscore_description_label = customtkinter.CTkLabel(self.tabview.tab("Recommendations"),
                                                                text=self.finscore_description,
                                                                font=customtkinter.CTkFont(size=18),
                                                                wraplength=500,
                                                                fg_color=None,
                                                                justify=tk.LEFT)
        self.finscore_description_label.grid(row=4, column=1, sticky="nsew", padx=20, pady=(0, 100))

    

    def get_recommendations(self):
        age = int(self.age_entry.get())
        income = self.income_entry.get()
        risk_tolerance = self.slider_1.get()

        # Populate the risk scores dictionary by fetching data from the API
        for ticker in self.investments_data.keys():
            risk_score = self.get_stock_risk_scores(ticker)
            self.risk_scores[ticker] = risk_score

        max_risk_score = 0.4
        for ticker in self.risk_scores:
            self.risk_scores[ticker] /= max_risk_score

        # Calculate the total investment in the portfolio
        total_investment = sum(self.investments_data.values())

        # Calculate the weighted risk score for each stock
        weighted_risk_scores = {ticker: (investment / total_investment) * risk_score for ticker, investment, risk_score in zip(self.investments_data.keys(), self.investments_data.values(), self.risk_scores.values())}

        # Calculate the riskiness index of the portfolio by summing up the weighted risk scores
        self.riskiness_index = sum(weighted_risk_scores.values())

        self.riskiness_label.configure(text=f"Portfolio Risk Score: {self.riskiness_index:.2f}")
        if self.riskiness_index < 0.3:
            risk_color = "green"
        elif self.riskiness_index < 0.7:
            risk_color = "orange"
        else:
            risk_color = "red"
        self.riskiness_label.configure(text_color=risk_color)

        risk_index_description = "This index represents the overall risk level of your investment portfolio, ranging from 0 (low risk) to 1 (extremely high risk)."
        risk_ratio=(self.riskiness_index-risk_tolerance)/risk_tolerance
        if abs(risk_ratio)<.20:
            additional_message = " Your portfolio currently matches your risk tolerance. Keep investing in similar assets!"
            risk_index_description += additional_message
        elif risk_ratio > 0:
            additional_message = " Your portfolio is currently higher risk than your risk tolerance, so you may consider moving out of more aggressive investments to decrease risk."
            risk_index_description += additional_message
        elif risk_ratio < 0:
            additional_message = " Your portfolio is currently lower risk than your risk tolerance, so you may consider diversifying into more aggressive investments to potentially increase returns."
            risk_index_description += additional_message

        self.riskiness_description_label.configure(text=risk_index_description)


        #print("Age:", age)
        #print("Monthly Income:", income)
        #print("Risk Tolerance:", risk_tolerance)
        #print("Investing Data:", self.investments_data)
        #print("Spending Data:", self.expenses_data)
        #print("Saving Data:", self.saving_data)
        #print("Riskiness Index:", self.riskiness_index)

        expenses=float(sum(self.expenses_data.values()))
        saving=float(sum(self.saving_data.values()))
        self.finscore = kalman(income, expenses, saving, age, self.riskiness_index)
        self.finscore_description=""

        # Define parameters for each age group
        age_groups = {
            "16-22": {"income_mean": 1500, "income_std": 500, "savings_mean": 2500, "savings_std": 1000, "expenses_mean": 1000, "expenses_std": 500},
            "23-29": {"income_mean": 3500, "income_std": 1000, "savings_mean": 15000, "savings_std": 5000, "expenses_mean": 2000, "expenses_std": 1000},
            "30-40": {"income_mean": 6000, "income_std": 1500, "savings_mean": 50000, "savings_std": 10000, "expenses_mean": 4000, "expenses_std": 1500},
            "40-50": {"income_mean": 8000, "income_std": 2000, "savings_mean": 100000, "savings_std": 20000, "expenses_mean": 6000, "expenses_std": 2000},
            "50-65": {"income_mean": 10000, "income_std": 2500, "savings_mean": 250000, "savings_std": 50000, "expenses_mean": 8000, "expenses_std": 2500},
            "65+": {"income_mean": 5000, "income_std": 2000, "savings_mean": 100000, "savings_std": 50000, "expenses_mean": 5000, "expenses_std": 2000}
        }

        # Number of samples for each group
        num_samples = 1000

        age_group=""
        if 16 <= age <= 22:
            age_group = "16-22"
        elif 23 <= age <= 29:
            age_group ="23-29"
        elif 30 <= age <= 40:
            age_group ="30-40"
        elif 41 <= age <= 50:
            age_group ="40-50"
        elif 51 <= age <= 65:
            age_group ="50-65"
        else:
            age_group = "65+"

        group_params = age_groups[age_group]
        mean = group_params["income_mean"] - group_params["expenses_mean"] + group_params["savings_mean"]
        std_dev = np.sqrt(group_params["income_std"]**2 + group_params["expenses_std"]**2 + group_params["savings_std"]**2)

        z_score = (self.finscore - mean) / std_dev

        sigmoid = 1 / (1 + np.exp(-z_score))
        self.finscore = sigmoid * 100
        
        end=int(self.finscore%10)
        print("end: ",end)
        ending=""
        if end==2:
            ending="nd"
        elif end==3:
            ending="rd"
        else:
            ending="th"
        print("ending: ",ending)
        if z_score < -1:
            fin_color = "red"
            self.finscore_description += f"Keep going! You are currently in the {self.finscore:.0f}{ending} percentile of people in your age group. While this may be below the average, it's important to see this as an opportunity for growth and improvement in managing your finances. To improve your position, consider reviewing and adjusting your current financial strategies. This might involve more disciplined budgeting, exploring new savings methods, or seeking advice on effective investment strategies. Remember, everyone's financial journey is unique, and progress takes time. Staying informed, adapting to new financial insights, and being proactive are crucial steps towards improving your financial standing and achieving long-term financial success."
        elif -1 <= z_score <= 1:
            fin_color = "orange"
            self.finscore_description += f"You are in the {self.finscore:.0f}{ending} percentile of people in your age group! This is a great accomplishment as it means you are right in line with the average financial standing of your peers. Being at this percentile indicates that you have a stable and balanced approach to your financial health. To maintain or further improve your position, consider improving on your current financial strategies while remaining open to new ideas for optimizing your savings, investments, and expenditures. Remember, effective financial planning is a continual journey, and staying informed and proactive is essential for long-term financial success."
        else:
            fin_color = "green"
            self.finscore_description += f"Congrats! You are in the {self.finscore:.0f}{ending} percentile of people in your age group! Keep up the good work managing your finances. This high percentile indicates that your financial health is better than many of your peers. To maintain or even improve this standing, consider continuing your current financial strategies, and always be open to exploring new ways to optimize your savings, investments, and expenditures. Remember, financial planning is an ongoing process, and staying informed and proactive is key to long-term financial success."


        self.finscore_label.configure(text=f"FinScore: {self.finscore:.2f}")
        self.finscore_label.configure(text_color=fin_color)
        self.finscore_description_label.configure(text=self.finscore_description)

    # Function to get risk scores for stocks
    def get_stock_risk_scores(self, ticker):
        # Fetch historical data from Yahoo Finance
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y", interval="1mo")  # Adjust the period and interval as needed

        # Extract the adjusted close prices
        if "Close" in hist.columns:
            prices = hist["Close"].dropna().tolist()

            # Calculate the volatility of price changes
            if len(prices) > 1:
                returns = np.diff(prices) / prices[:-1]
                volatility = np.std(returns)
                risk_score = volatility
            else:
                # Default risk score if there's insufficient data
                risk_score = 0
        else:
            # Default to 0 if data is not available
            risk_score = 0

        return risk_score
    

    def fetch_data_and_plot(self):
        stock_symbol = self.stock_symbol_entry.get().upper()
        investment_type = self.investment_type_var.get()
        investment_value = float(self.investment_entry.get())

        try:
            stock_info = yf.Ticker(stock_symbol)
            stock_price = stock_info.history(period='1d')['Close'][0]

            if investment_type == "Shares":
                investment_value_in_dollars = investment_value * stock_price
            else:
                investment_value_in_dollars = investment_value

            if stock_symbol in self.investments_data:
                self.investments_data[str(stock_symbol)] += investment_value_in_dollars
            else:
                self.investments_data[str(stock_symbol)] = investment_value_in_dollars

            self.plot_pie_chart("Investing", list(self.investments_data.keys()), list(self.investments_data.values()))

        except Exception as e:
            print(f"Error fetching data for {stock_symbol}: {e}")
    
    def add_expense_and_plot(self):
        expense_description = self.expense_description_entry.get()
        expense_category = self.expense_category_var.get()
        expense_amount = float(self.expense_amount_entry.get())

        try:
            if expense_category in self.expenses_data:
                self.expenses_data[str(expense_category)] += expense_amount
            else:
                self.expenses_data[str(expense_category)] = expense_amount

            self.plot_pie_chart("Spending", list(self.expenses_data.keys()), list(self.expenses_data.values()))

        except Exception as e:
            print(f"Error adding expense: {e}")

    def add_saving_and_plot(self):
        # Gather data from entry fields
        total_savings = float(self.savings_entry.get()) if self.savings_entry.get() else 0
        total_traditional_401k = float(self.traditional_401k_entry.get()) if self.traditional_401k_entry.get() else 0
        total_roth = float(self.roth_entry.get()) if self.roth_entry.get() else 0
        total_other_investments = float(self.other_investments_entry.get()) if self.other_investments_entry.get() else 0

        # Update savings data
        self.saving_data = {
            "Total Savings": total_savings,
            "Traditional 401k": total_traditional_401k,
            "Roth": total_roth,
            "Other Investments": total_other_investments
        }

        for key in list(self.saving_data.keys()):
            if self.saving_data[key] == 0:
                del self.saving_data[key]

        # Plot the data
        self.plot_pie_chart("Saving", list(self.saving_data.keys()), list(self.saving_data.values()))

    def plot_pie_chart(self, tab_name, labels, values):
        try:
            plt.clf()
            fig, ax = plt.subplots()

            # Make values positive
            non_negative_values = [max(0, val) for val in values]

            ax.pie(non_negative_values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that the pie is drawn as a circle.
            plt.title(f"{tab_name}", fontsize=16)

            # Update the existing canvas or create a new one if it doesn't exist
            if tab_name == "Investing":
                if self.canvas_reference_investing:
                    self.canvas_reference_investing.get_tk_widget().destroy()

                self.canvas_reference_investing = FigureCanvasTkAgg(fig, master=self.plot_canvas)
                self.canvas_reference_investing.draw()
                self.canvas_reference_investing.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            elif tab_name == "Spending":
                if self.canvas_reference_spending:
                    self.canvas_reference_spending.get_tk_widget().destroy()

                self.canvas_reference_spending = FigureCanvasTkAgg(fig, master=self.plot_canvas2)
                self.canvas_reference_spending.draw()
                self.canvas_reference_spending.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            elif tab_name == "Saving":
                if self.canvas_reference_saving:
                    self.canvas_reference_saving.get_tk_widget().destroy()

                self.canvas_reference_saving = FigureCanvasTkAgg(fig, master=self.plot_canvas3)
                self.canvas_reference_saving.draw()
                self.canvas_reference_saving.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            print(f"Error plotting pie chart: {e}")


    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")


if __name__ == "__main__":
    app = App()
    app.mainloop()
