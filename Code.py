import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")

        # Данные
        self.expenses = []
        self.load_data()

        # Виджеты
        self.create_input_frame()
        self.create_filter_frame()
        self.create_table()
        self.create_summary_frame()

        # Обновить таблицу
        self.refresh_table()

    # ------------------- Ввод данных -------------------
    def create_input_frame(self):
        frame = tk.LabelFrame(self.root, text="Добавить расход", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Сумма:").grid(row=0, column=0, sticky="w")
        self.amount_entry = tk.Entry(frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Категория:").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.category_combo = ttk.Combobox(frame, values=["Еда", "Транспорт", "Развлечения", "Здоровье", "Другое"], width=12)
        self.category_combo.grid(row=0, column=3, padx=5)
        self.category_combo.set("Еда")

        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, sticky="w", padx=(10, 0))
        self.date_entry = tk.Entry(frame, width=12)
        self.date_entry.grid(row=0, column=5, padx=5)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        self.add_btn = tk.Button(frame, text="Добавить расход", command=self.add_expense)
        self.add_btn.grid(row=0, column=6, padx=10)

    # ------------------- Фильтры -------------------
    def create_filter_frame(self):
        frame = tk.LabelFrame(self.root, text="Фильтр", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Категория:").grid(row=0, column=0, sticky="w")
        self.filter_category = ttk.Combobox(frame, values=["Все"] + ["Еда", "Транспорт", "Развлечения", "Здоровье", "Другое"], width=12)
        self.filter_category.grid(row=0, column=1, padx=5)
        self.filter_category.set("Все")

        tk.Label(frame, text="Дата от (ГГГГ-ММ-ДД):").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.date_from = tk.Entry(frame, width=12)
        self.date_from.grid(row=0, column=3, padx=5)

        tk.Label(frame, text="Дата до (ГГГГ-ММ-ДД):").grid(row=0, column=4, sticky="w", padx=(10, 0))
        self.date_to = tk.Entry(frame, width=12)
        self.date_to.grid(row=0, column=5, padx=5)

        self.filter_btn = tk.Button(frame, text="Применить фильтр", command=self.refresh_table)
        self.filter_btn.grid(row=0, column=6, padx=10)

    # ------------------- Таблица расходов -------------------
    def create_table(self):
        columns = ("ID", "Дата", "Категория", "Сумма")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

    # ------------------- Сводка -------------------
    def create_summary_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=5)

        self.summary_label = tk.Label(frame, text="Сумма за период: 0.00", font=("Arial", 12, "bold"))
        self.summary_label.pack(side="left")

        self.clear_filter_btn = tk.Button(frame, text="Сбросить фильтр", command=self.reset_filter)
        self.clear_filter_btn.pack(side="right")

    # ------------------- Логика -------------------
    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Сумма должна быть > 0")
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
            return

        category = self.category_combo.get()
        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию")
            return

        date_str = self.date_entry.get()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        new_id = max([e["id"] for e in self.expenses], default=0) + 1
        self.expenses.append({
            "id": new_id,
            "amount": amount,
            "category": category,
            "date": date_str
        })
        self.save_data()
        self.refresh_table()
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

    def get_filtered_expenses(self):
        cat_filter = self.filter_category.get()
        date_from = self.date_from.get()
        date_to = self.date_to.get()

        filtered = self.expenses[:]

        if cat_filter != "Все":
            filtered = [e for e in filtered if e["category"] == cat_filter]

        if date_from:
            try:
                d_from = datetime.strptime(date_from, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") >= d_from]
            except:
                pass
        if date_to:
            try:
                d_to = datetime.strptime(date_to, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") <= d_to]
            except:
                pass

        return filtered

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered = self.get_filtered_expenses()
        total = 0
        for exp in filtered:
            self.tree.insert("", "end", values=(exp["id"], exp["date"], exp["category"], f"{exp['amount']:.2f}"))
            total += exp["amount"]

        self.summary_label.config(text=f"Сумма за период: {total:.2f}")

    def reset_filter(self):
        self.filter_category.set("Все")
        self.date_from.delete(0, tk.END)
        self.date_to.delete(0, tk.END)
        self.refresh_table()

    # ------------------- Работа с JSON -------------------
    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, indent=4, ensure_ascii=False)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.expenses = json.load(f)
        else:
            self.expenses = []

# ------------------- Запуск -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
