"""
Flowallet - Personal Finance Manager

This module serves as the main entry point for the Flowallet application.
It provides functionality for managing transactions, generating charts,
and interacting with the database. The module also handles user interface
components and integrates themes for an enhanced user experience.

Main functionalities include:
- Adding, deleting, and searching transactions.
- Exporting data to CSV.
- Generating pie, bar and line charts for financial data.
- Tracking income, expenses and total balance.
"""

import os
import sys
import csv
import random
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FuncFormatter
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def setup_database():
    """Set up the SQLite database schema and tables"""

    conn = sqlite3.connect('flowallet.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            type TEXT,  -- "income" or "expense"
            category TEXT,
            amount REAL
        )
    ''')
    conn.commit()
    conn.close()

def validate_amount(amount):
    """Validate the format of the input amount"""

    try:
        amount = amount.replace(',', '')
        value = float(amount)
        return value if value > 0 else None
    except ValueError:
        return None

def format_amount_input(event):
    """Format the input amount into the correct currency format"""

    amount = amount_entry.get().replace(',', '')

    if amount.isdigit() and int(amount) > 0:
        formatted_amount = "{:,}".format(int(amount))
        amount_entry.delete(0, tk.END)
        amount_entry.insert(0, formatted_amount)
    elif any(not (c.isdigit() or c == ',' or c == '.') for c in amount):
        cleaned_amount = ''.join(c for c in amount if c.isdigit() or c == ',' or c == '.')
        amount_entry.delete(0, tk.END)
        amount_entry.insert(0, cleaned_amount)

def add_transaction():
    """Add a new transaction to the database and update totals"""

    amount = amount_entry.get()
    category = category_entry.get().capitalize()
    trans_type = type_var.get()

    amount_value = validate_amount(amount)

    if amount_value is None:
        result_label.config(text="Please enter a valid numeric amount.", fg="red")
        return

    if not category:
        result_label.config(text="Please enter a category.", fg="red")
        return

    try:
        conn = sqlite3.connect('flowallet.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT MIN(id) FROM transactions WHERE id NOT IN (SELECT id FROM transactions)')
        available_id = cursor.fetchone()[0]

        if available_id is None:
            cursor.execute('SELECT MAX(id) FROM transactions')
            max_id = cursor.fetchone()[0]
            new_id = 1 if max_id is None else max_id + 1
        else:
            new_id = available_id

        cursor.execute('''
            INSERT INTO transactions (id, date, type, category, amount)
            VALUES (?, CURRENT_DATE, ?, ?, ?)
        ''', (new_id, trans_type, category, amount_value))
        conn.commit()
        conn.close()

        result_label.config(text="Transaction Added!", fg="green")

        amount_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        amount_entry.focus()

        update_totals()

    except sqlite3.Error as e:
        result_label.config(text=f"Database error: {e}", fg="red")

def on_amount_entry(event):
    """Move to category field after entering an amount and pressing Enter"""

    amount = amount_entry.get()

    if validate_amount(amount) is not None:
        category_entry.focus()
    else:
        result_label.config(text="Please enter a valid numeric amount.", fg="red")
        amount_entry.focus()

def on_category_entry(event):
    """Trigger the Add Transaction button after entering a category and pressing Enter"""

    if category_entry.get():
        add_transaction()
    else:
        result_label.config(text="Please enter a category.", fg="red")

def view_transaction_history():
    """View transaction history table"""

    conn = sqlite3.connect('flowallet.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions')
    transactions = cursor.fetchall()
    conn.close()

    history_window = tk.Toplevel(root)
    history_window.title("Transaction History")
    history_window.geometry("500x500")
    logo_path = resource_path('assets/app_logo.ico')
    history_window.wm_iconbitmap(logo_path)
    history_window.focus_force()

    def search_transactions(event=None):
        """Search for transactions based on the input search criteria"""

        for item in tree.get_children():
            tree.delete(item)

        conn = sqlite3.connect('flowallet.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions')
        transactions = cursor.fetchall()
        conn.close()

        search_term = search_entry.get().lower()

        filtered_transactions = [
            trans for trans in transactions if search_term in str(trans).lower()]

        for index, transaction in enumerate(filtered_transactions):
            if index % 2 == 0:
                tree.insert("", "end",
                            values=(transaction[0], transaction[1], transaction[2],
                            transaction[3], f"${transaction[4]:,}"), tags=('evenrow',))
            else:
                tree.insert("", "end",
                            values=(transaction[0], transaction[1], transaction[2],
                            transaction[3], f"${transaction[4]:,}"), tags=('oddrow',))

    # Frame to hold search components (label, entry, button)
    search_frame = ttk.Frame(history_window)
    search_frame.pack(padx=10, pady=5, anchor='center')

    search_label = tk.Label(search_frame, text="Search:")
    search_label.pack(side="left", padx=5)

    search_entry = ttk.Entry(search_frame)
    search_entry.pack(side="left", padx=5)
    search_entry.bind("<KeyRelease>", search_transactions)

    search_button = ttk.Button(search_frame, text="Search", command=search_transactions)
    search_button.bind("<ButtonRelease>", lambda e: history_window.focus())
    search_button.pack(side="left", padx=5)

    # Frame to hold history window table and scrollbars
    table_frame = ttk.Frame(history_window)
    table_frame.pack(fill='both', expand=True)

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical")
    scrollbar_y.pack(side="right", fill="y")

    scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal")
    scrollbar_x.pack(side="bottom", fill="x")

    tree = ttk.Treeview(table_frame,
                        columns=("id", "date", "type", "category", "amount"), show="headings",
                        yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set,
                        selectmode="extended")

    tree.heading("id", text="ID", anchor=tk.W)
    tree.heading("date", text="Date", anchor=tk.W)
    tree.heading("type", text="Type", anchor=tk.W)
    tree.heading("category", text="Category", anchor=tk.W)
    tree.heading("amount", text="Amount", anchor=tk.W)

    tree.column("id", width=50, anchor=tk.W)
    tree.column("date", width=100, anchor=tk.W)
    tree.column("type", width=80, anchor=tk.W)
    tree.column("category", width=150, anchor=tk.W)
    tree.column("amount", width=100, anchor=tk.W)

    tree.pack(fill="both", expand=True)

    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)

    tree.tag_configure('evenrow', background='#0f172a')
    tree.tag_configure('oddrow', background='#1e293b')

    for index, transaction in enumerate(transactions):
        if index % 2 == 0:
            tree.insert("", "end", values=(transaction[0], transaction[1],
                        transaction[2], transaction[3], f"${transaction[4]:,}"), tags=('evenrow',))
        else:
            tree.insert("", "end", values=(transaction[0], transaction[1],
                        transaction[2], transaction[3], f"${transaction[4]:,}"), tags=('oddrow',))

    def on_mouse_drag(event):
        """Handle the selection of transactions in the treeview with mouse click + drag"""

        region = tree.identify_region(event.x, event.y)

        if region == 'cell':
            row_id = tree.identify_row(event.y)
            if row_id:
                tree.selection_add(row_id)

    tree.bind("<B1-Motion>", on_mouse_drag)

    # Button to delete selected transactions
    delete_button = ttk.Button(history_window, text="Delete",
                                command=lambda: delete_transaction(tree, history_window))
    delete_button.pack(padx=(5,10), pady=(5,5))

def delete_transaction(tree, history_window):
    """Delete the selected transactions from the database and totals"""

    selected_items = tree.selection()

    if selected_items:
        confirm = messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete selected transactions?",
            parent=history_window)
        if confirm:
            conn = sqlite3.connect('flowallet.db')
            cursor = conn.cursor()

            for selected_item in selected_items:
                item_id = tree.item(selected_item)['values'][0]
                tree.delete(selected_item)
                cursor.execute('DELETE FROM transactions WHERE id = ?', (item_id,))

            cursor.execute('SELECT id FROM transactions ORDER BY id')
            all_ids = cursor.fetchall()

            for new_id, (old_id,) in enumerate(all_ids, start=1):
                cursor.execute('UPDATE transactions SET id = ? WHERE id = ?', (new_id, old_id))

            conn.commit()

            tree.delete(*tree.get_children())  # Clear the treeview
            cursor.execute('SELECT * FROM transactions ORDER BY id')
            rows = cursor.fetchall()

            for index, row in enumerate(rows):
                if index % 2 == 0:
                    tree.insert('', 'end', values=row, tags=('evenrow',))
                else:
                    tree.insert('', 'end', values=row, tags=('oddrow',))

            conn.close()

            messagebox.showinfo("Deleted", "Transactions deleted successfully.",
                                parent=history_window)
            update_totals()
            history_window.focus_force()
    else:
        messagebox.showwarning("No Selection", "Please select a transaction to delete.",
                                parent=history_window)

def update_totals():
    """Update totals for income, expenses, and balance"""

    conn = sqlite3.connect('flowallet.db')
    cursor = conn.cursor()

    # Calculate total income
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "Income"')
    total_income = cursor.fetchone()[0]
    if total_income is None:
        total_income = 0.0

    # Calculate total expenses
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "Expense"')
    total_expenses = cursor.fetchone()[0]
    if total_expenses is None:
        total_expenses = 0.0

    # Calculate the current balance (income - expenses)
    balance = total_income - total_expenses

    # Update the labels to show totals
    income_label.config(text=f"Total Income: ${total_income:,}")
    expenses_label.config(text=f"Total Expenses: ${total_expenses:,}")
    balance_label.config(text=f"Balance: ${balance:,}")

    conn.close()

def export_data():
    """Export transaction data to a CSV file"""

    conn = sqlite3.connect('flowallet.db')
    cursor = conn.cursor()

    filter_type = filter_type_entry.get().capitalize().strip()
    filter_category = filter_category_entry.get().capitalize().strip()
    filter_date = filter_date_entry.get().strip()

    # Build dynamic query based on available filters
    query = 'SELECT * FROM transactions WHERE 1=1'
    params = []

    if filter_type and filter_type != "Income or Expense":
        query += ' AND type = ?'
        params.append(filter_type.capitalize())

    if filter_category and filter_category != "Category type":
        query += ' AND category = ?'
        params.append(filter_category.capitalize())

    if filter_date and filter_date != "(YYYY-MM-DD)":
        # Handle different date formats (YYYY, YYYY-MM, YYYY-MM-DD)
        if len(filter_date) == 4:  # Year only
            query += ' AND strftime("%Y", date) = ?'
            params.append(filter_date)
        elif len(filter_date) == 7:  # Year and month
            query += ' AND strftime("%Y-%m", date) = ?'
            params.append(filter_date)
        else: # Full date (YYYY-MM-DD)
            query += ' AND date = ?'
            params.append(filter_date)

    if not params:
        cursor.execute('SELECT * FROM transactions')
    else:
        cursor.execute(query, params)
    transactions = cursor.fetchall()

    if not transactions:
        messagebox.showinfo("No Data", "No transactions found for the given filters.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Transaction ID', 'Date', 'Type', 'Category', 'Amount'])
        for transaction in transactions:
            formatted_amount = "${:,}".format(transaction[4])
            writer.writerow([transaction[0], transaction[1],
                                transaction[2], transaction[3], formatted_amount])


    filter_type_entry.delete(0, tk.END)
    filter_category_entry.delete(0, tk.END)
    filter_date_entry.delete(0, tk.END)

    messagebox.showinfo("Export", "Transactions exported successfully!")

    filter_type_entry.focus_set()

    conn.close()

def generate_medium_colors(n):
    """Generates n medium brightness colors randomly selected from a large pool"""

    colors = list(mcolors.CSS4_COLORS.values())
    medium_colors = []

    for color in colors:
        r, g, b = mcolors.to_rgb(color)
        brightness = (r + g + b) / 3
        if 0.4 < brightness < 0.7:
            medium_colors.append(color)

    return random.sample(medium_colors, min(n, len(medium_colors)))

def format_currency(x, _):
    """Format the amount of money in chaers into the correct currency format"""

    return '${:,.0f}'.format(x)

def show_income_by_category_bar_chart():
    """Generate and display a bar chart showing income by category"""

    conn = sqlite3.connect('flowallet.db')
    cursor = conn.cursor()

    cursor.execute(
        'SELECT category, SUM(amount) FROM transactions WHERE type = "Income" GROUP BY category')
    categories = cursor.fetchall()
    conn.close()

    if not categories:
        messagebox.showinfo("No Data", "No income to show.")
        return

    labels = [category[0] for category in categories]
    values = [category[1] for category in categories]

    medium_colors = generate_medium_colors(len(labels))

    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, values)

    plt.xlabel('Category', labelpad=20, fontweight='bold')
    plt.ylabel('Amount Earned', labelpad=20, fontweight='bold')
    plt.title('Income by Category', fontweight='bold')

    ax = plt.gca()
    ax.xaxis.label.set_y(-0.15)

    for i, measure_bar in enumerate(bars):
        measure_bar.set_color(medium_colors[i])
        plt.text(i + 0.07, -max(values) * 0.01, '${:,.0f}'.format(values[i]),
                    ha='center', va='top', rotation=45, fontweight='bold')

    ax = plt.gca()
    for xtick, color in zip(ax.get_xticklabels(), medium_colors):
        xtick.set_color(color)
        xtick.set_fontweight('bold')

    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_currency))

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def show_expenses_by_category_bar_chart():
    """Generate and display a bar chart showing expenses by category"""

    conn = sqlite3.connect('flowallet.db')
    cursor = conn.cursor()

    cursor.execute(
        'SELECT category, SUM(amount) FROM transactions WHERE type = "Expense" GROUP BY category')
    categories = cursor.fetchall()
    conn.close()

    if not categories:
        messagebox.showinfo("No Data", "No expenses to show.")
        return

    labels = [category[0] for category in categories]
    values = [category[1] for category in categories]

    medium_colors = generate_medium_colors(len(labels))

    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, values)
    plt.xlabel('Category', labelpad=20, fontweight='bold')
    plt.ylabel('Amount Spent', labelpad=10, fontweight='bold')
    plt.title('Expenses by Category', fontweight='bold')

    ax = plt.gca()
    ax.xaxis.label.set_y(-0.15)

    for i, measure_bar in enumerate(bars):
        measure_bar.set_color(medium_colors[i])
        plt.text(i + 0.07, -max(values) * 0.01, '${:,.0f}'.format(values[i]),
                    ha='center', va='top', rotation=45, fontweight='bold')

    ax = plt.gca()
    for xtick, color in zip(ax.get_xticklabels(), medium_colors):
        xtick.set_color(color)
        xtick.set_fontweight('bold')

    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_currency))

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def show_income_vs_expenses_bar_chart():
    """Generate and display a bar chart showing income vs expenses"""

    conn = sqlite3.connect('flowallet.db')
    cursor = conn.cursor()

    cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "Income"')
    total_income = cursor.fetchone()[0]
    if total_income is None:
        messagebox.showinfo("No Data", "No transactions for income to show.")
        return

    cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "Expense"')
    total_expenses = cursor.fetchone()[0]
    if total_expenses is None:
        messagebox.showinfo("No Data", "No transactions for expenses to show.")
        return

    conn.close()

    labels = ['Income', 'Expenses']
    values = [total_income, total_expenses]
    medium_colors = ['green', 'red']

    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, values, color=medium_colors)

    for measure_bar, value in zip(bars, values):
        plt.text(measure_bar.get_x() + measure_bar.get_width()/2,
                    measure_bar.get_height(), f'${value:,.0f}',
                    ha='center', va='bottom', fontweight='bold')

    plt.title('Income vs. Expenses', fontweight='bold')

    ax = plt.gca()
    xticks = ax.get_xticklabels()
    xticks[0].set_color('green')
    xticks[0].set_fontweight('bold')
    xticks[1].set_color('red')
    xticks[1].set_fontweight('bold')

    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_currency))

    plt.tight_layout()
    plt.show()

def show_income_by_category_pie_chart():
    """Generate and display a pie chart showing income by category"""

    conn = sqlite3.connect('flowallet.db')
    cursor = conn.cursor()

    cursor.execute(
        'SELECT category, SUM(amount) FROM transactions WHERE type = "Income" GROUP BY category')
    categories = cursor.fetchall()
    conn.close()

    if not categories:
        messagebox.showinfo("No Data", "No income to show.")
        return

    labels = [category[0] for category in categories]
    values = [category[1] for category in categories]
    colors = generate_medium_colors(len(labels))

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        autopct=lambda p: '' if p < 5 else f'{p:.1f}%',
        colors=colors,
        startangle=90
    )

    small_categories = []

    for i, (wedge, value) in enumerate(zip(wedges, values)):
        percentage = (value / sum(values)) * 100

        if percentage >= 5:
            angle = (wedge.theta2 + wedge.theta1) / 2.0
            x = 1.4 * np.cos(np.radians(angle))
            y = 1.2 * np.sin(np.radians(angle))

            label_text = labels[i]

            ax.text(x, y, label_text,
                    ha='center', va='center', fontweight='bold', color=colors[i])
            ax.text(x, y - 0.1, f'(${value:,})',
                    ha='center', va='center', fontweight='bold', color='black')
        else:
            small_categories.append((labels[i], percentage, value, colors[i]))

    if small_categories:
        box_ax = fig.add_axes([0.05, 0.70, 0.2, 0.2])
        box_ax.set_axis_off()

        small_categories.sort(key=lambda x: x[1])

        start_y = 0.8 if len(small_categories) <= 5 else 0.9
        box_ax.text(0.0, 1.0, 'Categories < 5%', ha='left', va='top', fontweight='bold')

        for label, percentage, amount, color in small_categories:
            box_ax.add_patch(plt.Rectangle((0, start_y - 0.1), 0.05, 0.05, color=color))
            box_ax.text(0.1, start_y - 0.1, f'{label}',
                        ha='left', va='center', color=color, fontweight='bold')
            box_ax.text(0.7, start_y - 0.1, f'({percentage:.1f}%) (${amount:,})',
                        ha='left', va='center', color='black', fontweight='bold')
            start_y -= 0.15

    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_color('black')

    ax.set_title('Income by Category', fontweight='bold', fontsize=16, pad=30)

    plt.show()

def show_expenses_by_category_pie_chart():
    """Generate and display a pie chart showing expenses by category"""

    conn = sqlite3.connect('flowallet.db')
    cursor = conn.cursor()

    cursor.execute(
        'SELECT category, SUM(amount) FROM transactions WHERE type = "Expense" GROUP BY category')
    categories = cursor.fetchall()
    conn.close()

    if not categories:
        messagebox.showinfo("No Data", "No expenses to show.")
        return

    labels = [category[0] for category in categories]
    values = [category[1] for category in categories]
    colors = generate_medium_colors(len(labels))

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        autopct=lambda p: '' if p < 5 else f'{p:.1f}%',
        colors=colors,
        startangle=90
    )

    small_categories = []

    for i, (wedge, value) in enumerate(zip(wedges, values)):
        percentage = (value / sum(values)) * 100

        if percentage >= 5:
            angle = (wedge.theta2 + wedge.theta1) / 2.0
            x = 1.4 * np.cos(np.radians(angle))
            y = 1.2 * np.sin(np.radians(angle))

            label_text = labels[i]

            ax.text(x, y, label_text,
                    ha='center', va='center', fontweight='bold', color=colors[i])
            ax.text(x, y - 0.1, f'(${value:,})',
                    ha='center', va='center', fontweight='bold', color='black')
        else:
            small_categories.append((labels[i], percentage, value, colors[i]))

    if small_categories:
        box_ax = fig.add_axes([0.05, 0.70, 0.2, 0.2])
        box_ax.set_axis_off()

        small_categories.sort(key=lambda x: x[1])

        start_y = 0.8 if len(small_categories) <= 5 else 0.9
        box_ax.text(0.0, 1.0, 'Categories < 5%', ha='left', va='top', fontweight='bold')

        for label, percentage, amount, color in small_categories:
            box_ax.add_patch(plt.Rectangle((0, start_y - 0.1), 0.05, 0.05, color=color))
            box_ax.text(0.1, start_y - 0.1, f'{label}',
                        ha='left', va='center', color=color, fontweight='bold')
            box_ax.text(0.7, start_y - 0.1, f'({percentage:.1f}%) (${amount:,})',
                        ha='left', va='center', color='black', fontweight='bold')
            start_y -= 0.15

    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_color('black')

    ax.set_title('Expenses by Category', fontweight='bold', fontsize=16, pad=30)

    plt.show()

def show_income_vs_expenses_pie_chart():
    """Generate and display a pie chart showing income vs expenses"""

    conn = sqlite3.connect('flowallet.db')
    cursor = conn.cursor()

    cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "Income"')
    total_income = cursor.fetchone()[0]
    if total_income is None:
        messagebox.showinfo("No Data", "No transactions for income to show.")
        return

    cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "Expense"')
    total_expenses = cursor.fetchone()[0]
    if total_expenses is None:
        messagebox.showinfo("No Data", "No transactions for expenses to show.")
        return

    conn.close()

    labels = [f'Income (${total_income:,})', f'Expenses (${total_expenses:,})']
    values = [total_income, total_expenses]
    colors = ['green', 'red']

    plt.figure(figsize=(6, 6))
    wedges, texts, autotexts = plt.pie(
        values,
        labels=None,
        autopct=lambda p: '' if p < 5 else f'{p:.1f}%',
        colors=colors,
        startangle=90,
    )

    for i, (wedge, value) in enumerate(zip(wedges, values)):
        angle = (wedge.theta2 + wedge.theta1) / 2.0
        x = 1.4 * np.cos(np.radians(angle))
        y = 1.4 * np.sin(np.radians(angle))

        label_text = 'Income' if i == 0 else 'Expenses'
        label_color = 'green' if i == 0 else 'red'
        amount_text = f' (${value:,})'

        plt.text(x, y, label_text,
                ha='center', va='center', fontweight='bold', color=label_color)
        plt.text(x, y - 0.15, amount_text,
                ha='center', va='center', fontweight='bold', color='black')

    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_color('black')

    plt.title('Income vs. Expenses', fontweight='bold', pad=40)

    plt.tight_layout()

    plt.show()

def show_monthly_trends_for_income():
    """Generate and display a line chart showing monthly trends for income"""

    conn = sqlite3.connect('flowallet.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT strftime('%Y-%m', date) AS month, SUM(amount)
        FROM transactions
        WHERE type = "Income"
        GROUP BY month
    ''')
    trends = cursor.fetchall()
    conn.close()

    if not trends:
        messagebox.showinfo("No Data", "No monthly trends to show.")
        return

    months = [trend[0] for trend in trends]
    amounts = [trend[1] for trend in trends]

    plt.figure(figsize=(10, 6))
    plt.plot(months, amounts, marker='o')
    plt.title('Monthly Income Trends', fontweight='bold')
    plt.xlabel('Month', fontweight='bold')
    plt.ylabel('Amount Spent', labelpad=20, fontweight='bold')
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_currency))
    plt.tight_layout()
    plt.show()

def show_monthly_trends_for_expenses():
    """Generate and display a line chart showing monthly trends for expenses"""

    conn = sqlite3.connect('flowallet.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT strftime('%Y-%m', date) AS month, SUM(amount)
        FROM transactions
        WHERE type = "Expense"
        GROUP BY month
    ''')
    trends = cursor.fetchall()
    conn.close()

    if not trends:
        messagebox.showinfo("No Data", "No monthly trends to show.")
        return

    months = [trend[0] for trend in trends]
    amounts = [trend[1] for trend in trends]

    plt.figure(figsize=(10, 6))
    plt.plot(months, amounts, marker='o')
    plt.title('Monthly Expenses Trends', fontweight='bold')
    plt.xlabel('Month', fontweight='bold')
    plt.ylabel('Amount Spent', labelpad=20, fontweight='bold')
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_currency))
    plt.tight_layout()
    plt.show()

def center_root_window(window):
    """Start the main window of the application at the center of the screen"""

    width = 800
    height = 650
    window.geometry(f'{width}x{height}')

    window.update()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    taskbar_height = 45

    position_x = int((screen_width / 2) - (width / 2))
    position_y = int((screen_height / 2) - (height / 2) - (taskbar_height / 2))

    window.geometry(f'{width}x{height}+{position_x}+{position_y}')

class PlaceholderEntry(ttk.Entry):
    """Create a placeholder for entry fields"""

    def __init__(self, master=None, placeholder="", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.default_fg_color = 'white'
        self.placeholder_fg_color = '#9E9E9E'
        self.is_placeholder = True
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.on_focus_out(None)

    def on_focus_in(self, event):
        """On entry field focus, remove placeholder text and set text color to foreground color"""
        if self.is_placeholder:
            self.delete(0, tk.END)
            self.config(foreground=self.default_fg_color)
            self.is_placeholder = False
    def on_focus_out(self, event):
        """If entry field is empty and focused out, replace text with placeholder text and color"""
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(foreground=self.placeholder_fg_color)
            self.is_placeholder = True
    def get(self):
        current_text = super().get()
        if self.is_placeholder:
            return ""
        return current_text

def clear_focus(event):
    """Clear focus from buttons and entry fields when clicking on root"""

    widget = event.widget
    if isinstance(widget, (PlaceholderEntry, ttk.Entry)):
        return
    root.focus_set()

def initialize_app():
    """Initialize and configure the main window of the application."""

    result_label.config(text="Please enter a numeric amount and a category to add a transaction.",
                         fg="#4CAF50")

def resource_path(relative_path):
    """ Get absolute path to resource, works for PyInstaller bundling """

    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Setup database
setup_database()

# Main application window
root = tk.Tk()
root.withdraw()
root.title("Flowallet")
root.geometry("800x650")
icon_path = resource_path('assets/app_logo.ico')
root.wm_iconbitmap(icon_path)
root.resizable(False, False)
center_root_window(root)
root.deiconify()

header_frame = ttk.Frame(root, padding=10)
header_frame.pack(pady=10)

# App Name (Header)
app_name_label = ttk.Label(header_frame, text="Flowallet",
                            font=('Helvetica', 24, 'bold'), foreground='#4CAF50')
app_name_label.pack()

# Slogan (Subtitle)
slogan_label = ttk.Label(header_frame, text="Your Efortless Personal Finance Manager",
                        font=('Helvetica', 14, 'italic'), foreground='#999999')
slogan_label.pack()

# Frame to hold input fields of adding transactions (amount, category)
input_frame = ttk.Frame(root)
input_frame.pack()

# Amount field
amount_label = ttk.Label(input_frame, text="Amount:")
amount_label.pack(side=tk.LEFT, padx=(5,5), pady=(15,5))
amount_entry = PlaceholderEntry(input_frame, placeholder="Transaction amount")
root.bind("<Button-1>", lambda event: root.focus_set())
amount_entry.pack(side=tk.LEFT, padx=(5,5), pady=(15,5))

# Category field
category_label = ttk.Label(input_frame, text="Category:")
category_label.pack(side=tk.LEFT, padx=(5,5), pady=(15,5))
category_entry = PlaceholderEntry(input_frame, placeholder="Category type")
root.bind("<Button-1>", lambda event: clear_focus(event))
category_entry.pack(side=tk.LEFT, padx=(5,5), pady=(15,5))

# Bindings to auto-move focus and trigger actions
amount_entry.bind('<KeyRelease>', format_amount_input)
amount_entry.bind('<Return>', on_amount_entry)
category_entry.bind('<Return>', on_category_entry)

# Frame to hold radio buttons of transaction type (income, expense)
type_frame = ttk.Frame(root)
type_frame.pack()

# Variable for transaction type
type_var = tk.StringVar(value="Income")

# Income radio button
income_radio = ttk.Radiobutton(type_frame, text="Income", variable=type_var, value="Income")
income_radio.bind("<ButtonRelease>", lambda e: root.focus())
income_radio.pack(side=tk.LEFT, padx=(20,5), pady=(5,5))

# Expense radio button
expense_radio = ttk.Radiobutton(type_frame, text="Expense", variable=type_var, value="Expense")
expense_radio.bind("<ButtonRelease>", lambda e: root.focus())
expense_radio.pack(side=tk.LEFT, padx=(20,5), pady=(5,5))

# Set income radio button as default
income_radio.invoke()

# Button to add transaction
add_button = ttk.Button(root, text="Add Transaction", command=add_transaction)
add_button.bind("<ButtonRelease>", lambda e: root.focus())
add_button.pack(padx=(25,5), pady=(5,5))

# Label to show results
result_label = tk.Label(root, text="")
result_label.pack(padx=(25,5), pady=(5,5))

# Button to view transaction history
history_button = ttk.Button(root, text="View Transaction History", command=view_transaction_history)
history_button.pack(padx=(25,5), pady=(5,5))

# Frame to hold filters of exporting data to CSV (type, category, date)
export_frame = ttk.Frame(root)
export_frame.pack()

# Filters for exporting data to CSV
filter_type_label = ttk.Label(export_frame, text="Filter by Type:")
filter_type_label.pack(side=tk.LEFT, padx=(5,5), pady=(5,5))
filter_type_entry = PlaceholderEntry(export_frame, placeholder="Income or Expense")
filter_type_entry.bind("<Return>", lambda e: filter_category_entry.focus_set())
filter_type_entry.pack(side=tk.LEFT, padx=(5,5), pady=(5,5))

filter_category_label = ttk.Label(export_frame, text="Filter by Category:")
filter_category_label.pack(side=tk.LEFT, padx=(5,5), pady=(5,5))
filter_category_entry = PlaceholderEntry(export_frame, placeholder="Category type")
filter_category_entry.bind("<Return>", lambda e: filter_date_entry.focus_set())
filter_category_entry.pack(side=tk.LEFT, padx=(5,5), pady=(5,5))

filter_date_label = ttk.Label(export_frame, text="Filter by Date:")
filter_date_label.pack(side=tk.LEFT, padx=(5,5), pady=(5,5))
filter_date_entry = PlaceholderEntry(export_frame, placeholder="(YYYY-MM-DD)")
filter_date_entry.bind("<Return>", lambda e: export_button.invoke())
filter_date_entry.pack(side=tk.LEFT, padx=(5,5), pady=(5,5))

# Button to export data
export_button = ttk.Button(root, text="Export Data to CSV", command=export_data)
export_button.bind("<ButtonRelease>", lambda e: root.focus())
export_button.pack(padx= (30,5), pady=(5,15))

# Frame to hold income and expenses bar charts buttons
bar_frame = ttk.Frame(root)
bar_frame.pack()

# Button to show income by category bar chart
income_by_category_button = ttk.Button(bar_frame,
                                        text="Show Income by Category - Bar Chart",
                                        command=show_income_by_category_bar_chart)
income_by_category_button.bind("<ButtonRelease>", lambda e: root.focus())
income_by_category_button.pack(side=tk.LEFT, padx=(45,5), pady=(5,5))

# Button to show expenses by category bar chart
expenses_by_category_button = ttk.Button(bar_frame,
                                            text="Show Expenses by Category - Bar Chart",
                                            command=show_expenses_by_category_bar_chart)
expenses_by_category_button.bind("<ButtonRelease>", lambda e: root.focus())
expenses_by_category_button.pack(side=tk.RIGHT, padx=(5,5), pady=(5,5))

# Button to show income vs expenses bar chart
bar_chart_button = ttk.Button(root,
                                text="Show Income vs Expenses - Bar Chart",
                                command=show_income_vs_expenses_bar_chart)
bar_chart_button.bind("<ButtonRelease>", lambda e: root.focus())
bar_chart_button.pack(padx=(45,5), pady=(5,5))

# Frame to hold income and expenses pie charts buttons
pie_frame = ttk.Frame(root)
pie_frame.pack()

# Button to show income by category pie chart
income_by_category_pie_button = ttk.Button(pie_frame,
                                            text="Show Income by Category - Pie Chart",
                                            command=show_income_by_category_pie_chart)
income_by_category_pie_button.bind("<ButtonRelease>", lambda e: root.focus())
income_by_category_pie_button.pack(side=tk.LEFT, padx=(45,5), pady=(5,5))

# Button to show expenses by category pie chart
expenses_by_category_pie_button = ttk.Button(pie_frame,
                                                text="Show Expenses by Category - Pie Chart",
                                                command=show_expenses_by_category_pie_chart)
expenses_by_category_pie_button.bind("<ButtonRelease>", lambda e: root.focus())
expenses_by_category_pie_button.pack(side=tk.RIGHT, padx=(5,5), pady=(5,5))

# Button to show income vs expenses pie chart
pie_chart_button = ttk.Button(root, text="Show Income vs Expenses - Pie Chart",
                                command=show_income_vs_expenses_pie_chart)
pie_chart_button.bind("<ButtonRelease>", lambda e: root.focus())
pie_chart_button.pack(padx=(45,5), pady=(5,5))

# Frame to hold income and expenses line charts buttons
trends_frame = ttk.Frame(root)
trends_frame.pack()

# Button to show monthly trends for income
income_monthly_trends_button = ttk.Button(trends_frame,
                                            text="Show Monthly Trends For Income - Line Chart",
                                            command=show_monthly_trends_for_income)
income_monthly_trends_button.bind("<ButtonRelease>", lambda e: root.focus())
income_monthly_trends_button.pack(side=tk.LEFT, padx=(45,5), pady=(5,5))

# Button to show monthly trends for expenses
expense_monthly_trends_button = ttk.Button(trends_frame,
                                            text="Show Monthly Trends For Expenses - Line Chart",
                                            command=show_monthly_trends_for_expenses)
expense_monthly_trends_button.bind("<ButtonRelease>", lambda e: root.focus())
expense_monthly_trends_button.pack(side=tk.RIGHT, padx=(5,5), pady=(5,5))

# Labels to display totals
income_label = ttk.Label(root, text="Total Income: $0.00")
income_label.pack(padx=(20,5), pady=(10,1))
income_label.configure(foreground="green")
expenses_label = ttk.Label(root, text="Total Expenses: $0.00")
expenses_label.pack(padx=(20,5), pady=(1,1))
expenses_label.configure(foreground="red")
balance_label = ttk.Label(root, text="Balance: $0.00")
balance_label.pack(padx=(20,5), pady=(1,1))

# Footer section
footer_frame = ttk.Frame(root, style="TFrame")
footer_frame.pack(fill="x", padx=(700,0), pady=(0,1))

footer_label = ttk.Label(footer_frame, text="©2024 Flowallet", font=("Arial", 8, "bold"))
footer_label.pack()

# Apply a custom style to buttons
style = ttk.Style(theme='darkly')

# Buttons style
style.configure('TButton',
                background='#333333',
                foreground='white',
                font=('Arial', 8, 'bold'),
                padding=4,
                highlightthickness=0,
                focuscolor='#343a40'
                )
style.map('TButton',
          background=[('active', '#444444'), ('pressed', '#555555')],
          relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
          )

# Entry fields style
style.configure('TEntry',
                fieldbackground='#222222',
                foreground='white',
                font=('Arial', 8),
                padding=4,
                relief='solid',
                bordercolor='#555555',
                borderwidth=2,
                )

# Radiobuttons style
style.configure('TRadiobutton',
                background='#222222',
                foreground='white',
                font=('Arial', 8),
                padding=4,
                indicatorrelief='flat',
                relief='solid',
                borderwidth=2,
                highlightthickness=0,
                focuscolor='#343a40'
                )
style.map('TRadiobutton',
          background=[('active', '#333333')],
          indicatorcolor=[('selected', '#343a40')]
          )

style.configure('TLabel',
                font=('Arial', 10, 'bold')
                )

update_totals()

initialize_app()

root.mainloop()
