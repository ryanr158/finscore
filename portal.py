import tkinter as tk
from tkinter import ttk 
import tkinter.messagebox
import customtkinter
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Finance Portal")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Finance Portal", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Investing", command=self.sidebar_button_event)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Spending", command=self.sidebar_button_event)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.risk_slider_label = customtkinter.CTkLabel(self.sidebar_frame, text="Set Risk Tolerance:", anchor="w")
        self.risk_slider_label.grid(row=4, column=0, padx=20, pady=(10, 50))
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        # create main entry and button
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Ask me anything finance related!")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        self.main_button_1 = customtkinter.CTkButton(master=self, text="Search", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=825, height=700)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Investing")
        self.tabview.add("Spending")
        self.tabview.add("Saving")
        self.tabview.add("Recommendations")
        self.tabview.tab("Investing").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabview.tab("Spending").grid_columnconfigure(0, weight=1)

        # create slider and progressbar frame
        self.slider_1 = customtkinter.CTkSlider(self.sidebar_frame, from_=0, to=1, number_of_steps=4)
        self.slider_1.grid(row=4, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")

        # set default values
        self.appearance_mode_optionemenu.set("Light")


        self.plot_canvas = customtkinter.CTkFrame(self.tabview.tab("Investing"))
        self.plot_canvas.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 10), sticky="nsew")

        self.plot_canvas2 = customtkinter.CTkFrame(self.tabview.tab("Spending"))
        self.plot_canvas2.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 10), sticky="nsew")

        self.canvas_reference_investing = None
        self.canvas_reference_spending = None

        self.investments_data = {}
        self.expenses_data = {}

        self.create_investing_tab()
        self.create_spending_tab()

    def show_investing_tab(self):
        self.tabview.tab("Investing").tkraise()

    def show_spending_tab(self):
        self.tabview.tab("Spending").tkraise()

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
        expense_categories = ["Food", "Housing", "Utilities", "Entertainment", "Transportation", "Tuition", "Other"]
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

        self.fetch_data_button = customtkinter.CTkButton(self.tabview.tab("Investing"), text="Fetch Data",
                                                        command=self.fetch_data_and_plot,
                                                        font=customtkinter.CTkFont(size=14))
        self.fetch_data_button.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")


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

    def plot_pie_chart(self, tab_name, labels, values):
        try:
            plt.clf()  # Clear existing plot
            fig, ax = plt.subplots()

            # Ensure all values are non-negative
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
