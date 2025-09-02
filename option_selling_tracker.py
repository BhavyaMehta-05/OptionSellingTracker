import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox

FILE_NAME = "option_selling_tracker.csv"

def initialize_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Strategy_Name", "Trade_Date", "Instrument", "Strike_Price", "Buy/Sell",
                "Expiry_Date", "Type", "Lots", "Entry_Price", "Exit_Price",
                "Hedged_Strike_Price", "Hedged_Buy/Sell", "Hedged_Entry_Price", "Hedged_Exit_Price",
                "Margin_Used", "Holding_Period", "P&L"])

class OptionSellingTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Option Selling Tracker")
        self.geometry("1150x680")
        self.minsize(1000, 600)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 11), background="#f5f7fa")
        style.configure("TButton", font=("Segoe UI", 11), padding=6)
        style.configure("Header.TLabel", font=("Segoe UI Semibold", 14))
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 12), background="#506482", foreground="white")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
        self.configure(bg="#f5f7fa")
        
        # Top frame for title and Clear All button
        top_frame = ttk.Frame(self, padding=(10, 12), style="TFrame")
        top_frame.pack(fill=tk.X)
        title_label = ttk.Label(top_frame, text="Option Selling Tracker", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        clear_btn = ttk.Button(top_frame, text="Clear All Trades", command=self.clear_all_records)
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_add_tab()
        self.create_display_tab()
        self.create_update_tab()
        self.create_search_tab()
        
        # Bottom status frame
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(bottom_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT)
        
        initialize_file()
        self.load_trades_into_table()

    def create_add_tab(self):
        self.add_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.add_tab, text="Add Trade")
        labels = [
            "Strategy Name", "Trade Date (YYYY-MM-DD)", "Instrument", "Strike Price", "Buy/Sell",
            "Expiry Date (YYYY-MM-DD)", "Type (CE/PE)", "Lots", "Entry Price", "Exit Price",
            "Have you hedged your position? (y/n)",
            "Hedged Strike Price", "Hedged Buy/Sell", "Hedged Entry Price", "Hedged Exit Price",
            "Margin Used", "Holding Period (Days)", "P&L"
        ]
        self.entries = {}
        for i, text in enumerate(labels):
            lbl = ttk.Label(self.add_tab, text=text + ":")
            lbl.grid(row=i, column=0, sticky=tk.W, pady=4, padx=5)
            entry = ttk.Entry(self.add_tab, width=32)
            entry.grid(row=i, column=1, sticky=tk.W, pady=4)
            self.entries[text] = entry
        
        hedged_fields = ["Hedged Strike Price", "Hedged Buy/Sell", "Hedged Entry Price", "Hedged Exit Price"]
        for field in hedged_fields:
            self.entries[field].config(state="disabled")

        def on_hedged_focusout(event):
            val = self.entries["Have you hedged your position? (y/n)"].get().strip().lower()
            state = "normal" if val == "y" else "disabled"
            for field in hedged_fields:
                self.entries[field].config(state=state)
                if state == "disabled":
                    self.entries[field].delete(0, tk.END)

        self.entries["Have you hedged your position? (y/n)"].bind("<FocusOut>", on_hedged_focusout)

        add_btn = ttk.Button(self.add_tab, text="Add Trade", command=self.add_trade)
        add_btn.grid(row=len(labels), column=0, columnspan=2, pady=12, sticky=tk.EW)

    def add_trade(self):
        vals = {k: v.get().strip() for k, v in self.entries.items()}
        required = [
            "Strategy Name", "Trade Date (YYYY-MM-DD)", "Instrument", "Strike Price",
            "Buy/Sell", "Expiry Date (YYYY-MM-DD)", "Type (CE/PE)",
            "Lots", "Entry Price", "Exit Price",
            "Margin Used", "Holding Period (Days)", "P&L"
        ]
        for field in required:
            if not vals[field]:
                messagebox.showwarning("Missing Input", f"'{field}' is required.")
                return
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r", newline='') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if row[0] == vals["Strategy Name"] and row[1] == vals["Trade Date (YYYY-MM-DD)"] and row[2] == vals["Instrument"]:
                        messagebox.showerror("Duplicate Trade", "Trade with same Strategy Name, Trade Date, and Instrument already exists.")
                        return
        hedged = vals["Have you hedged your position? (y/n)"].lower()
        if hedged == "y":
            hedged_fields = ["Hedged Strike Price", "Hedged Buy/Sell", "Hedged Entry Price", "Hedged Exit Price"]
            for field in hedged_fields:
                if not vals[field]:
                    messagebox.showwarning("Missing Input", f"Please fill all hedged details or answer 'n' to hedged question.")
                    return
            hedged_details = [vals[field] for field in hedged_fields]
        else:
            hedged_details = ["-", "-", "-", "-"]
        with open(FILE_NAME, "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                vals["Strategy Name"], vals["Trade Date (YYYY-MM-DD)"], vals["Instrument"],
                vals["Strike Price"], vals["Buy/Sell"], vals["Expiry Date (YYYY-MM-DD)"], vals["Type (CE/PE)"],
                vals["Lots"], vals["Entry Price"], vals["Exit Price"]] + hedged_details +
                [vals["Margin Used"], vals["Holding Period (Days)"], vals["P&L"]]
            )
        messagebox.showinfo("Success", "Trade added successfully!")
        self.status_var.set(f"Trade '{vals['Strategy Name']}' added.")
        self.clear_form()
        self.load_trades_into_table()
        self.notebook.select(self.display_tab)

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def create_display_tab(self):
        self.display_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.display_tab, text="Display Trades")
        tree_frame = ttk.Frame(self.display_tab)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.TOP, fill=tk.X)
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.trade_table = ttk.Treeview(
            tree_frame, show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set)
        self.trade_table.pack(fill=tk.BOTH, expand=True)
        tree_scroll_y.config(command=self.trade_table.yview)
        tree_scroll_x.config(command=self.trade_table.xview)
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r", newline='') as file:
                reader = csv.reader(file)
                headers = next(reader)
            self.trade_table["columns"] = headers
            for col in headers:
                self.trade_table.heading(col, text=col)
                self.trade_table.column(col, anchor=tk.CENTER, width=120)
        self.totals_frame = ttk.Frame(self.display_tab)
        self.totals_frame.pack(pady=(5, 10), padx=0, fill=tk.X)
        self.total_trades_label = tk.Label(self.totals_frame, font=("Segoe UI Semibold", 12),
                                           width=16, anchor="center", bg="#e3eaff", relief="solid")
        self.total_pl_label = tk.Label(self.totals_frame, font=("Segoe UI Semibold", 12),
                                       width=20, anchor="center", bg="#d6fde3", relief="solid")
        self.winning_label = tk.Label(self.totals_frame, font=("Segoe UI Semibold", 12),
                                      width=18, anchor="center", bg="#f7e3ff", relief="solid")
        self.losing_label = tk.Label(self.totals_frame, font=("Segoe UI Semibold", 12),
                                     width=18, anchor="center", bg="#ffe3e3", relief="solid")
        self.total_trades_label.pack(side=tk.LEFT, padx=6, pady=2, fill=tk.X, expand=True)
        self.total_pl_label.pack(side=tk.LEFT, padx=6, pady=2, fill=tk.X, expand=True)
        self.winning_label.pack(side=tk.LEFT, padx=6, pady=2, fill=tk.X, expand=True)
        self.losing_label.pack(side=tk.LEFT, padx=6, pady=2, fill=tk.X, expand=True)
        delete_btn = ttk.Button(self.display_tab, text="Delete Selected Trade", command=self.delete_selected_trade)
        delete_btn.pack(pady=8)

    def delete_selected_trade(self):
        selected = self.trade_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a trade to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected trade?")
        if not confirm:
            return
        item = selected[0]
        values = self.trade_table.item(item, "values")
        key = (values[0], values[1], values[2])
        with open(FILE_NAME, "r", newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)
            rows = list(reader)
        new_rows = [row for row in rows if not (row[0] == key[0] and row[1] == key[1] and row[2] == key[2])]
        if len(new_rows) == len(rows):
            messagebox.showerror("Error", "Trade not found in file.")
            return
        with open(FILE_NAME, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(new_rows)
        messagebox.showinfo("Deleted", f"Trade '{key[0]}' deleted successfully.")
        self.status_var.set(f"Trade '{key[0]}' deleted.")
        self.load_trades_into_table()

    def load_trades_into_table(self):
        for row in self.trade_table.get_children():
            self.trade_table.delete(row)
        if not os.path.exists(FILE_NAME):
            self.total_trades_label.config(text="Total Trades: 0")
            self.total_pl_label.config(text="Total P&L: 0.00", fg="green")
            self.winning_label.config(text="Winning Trades: 0")
            self.losing_label.config(text="Losing Trades: 0")
            return
        total_pl = 0.0
        total_trades = 0
        winning_trades = 0
        losing_trades = 0
        with open(FILE_NAME, "r", newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)
            pl_index = headers.index("P&L") if "P&L" in headers else -1
            for row in reader:
                if len(row) == len(headers):
                    self.trade_table.insert("", tk.END, values=row)
                    total_trades += 1
                    if pl_index != -1:
                        try:
                            pl_value = float(row[pl_index])
                            total_pl += pl_value
                            if pl_value > 0:
                                winning_trades += 1
                            elif pl_value < 0:
                                losing_trades += 1
                        except ValueError:
                            pass
        self.total_trades_label.config(text=f"Total Trades: {total_trades}")
        if total_pl < 0:
            self.total_pl_label.config(text=f"Total P&L: {total_pl:.2f}", fg="red")
        else:
            self.total_pl_label.config(text=f"Total P&L: {total_pl:.2f}", fg="green")
        self.winning_label.config(text=f"Winning Trades: {winning_trades}")
        self.losing_label.config(text=f"Losing Trades: {losing_trades}")

    def create_update_tab(self):
        self.update_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.update_tab, text="Update Trade")

        key_frame = ttk.LabelFrame(self.update_tab, text="Find Trade to Update", padding=(10, 10))
        key_frame.pack(fill=tk.X, pady=10)

        ttk.Label(key_frame, text="Strategy Name:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.upd_strategy = ttk.Entry(key_frame, width=25)
        self.upd_strategy.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(key_frame, text="Trade Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, sticky=tk.W)
        self.upd_date = ttk.Entry(key_frame, width=25)
        self.upd_date.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(key_frame, text="Instrument:").grid(row=2, column=0, padx=5, sticky=tk.W)
        self.upd_instrument = ttk.Entry(key_frame, width=25)
        self.upd_instrument.grid(row=2, column=1, padx=5, pady=4)

        find_btn = ttk.Button(key_frame, text="Find Trade", command=self.find_trade_for_update)
        find_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Scrollable canvas and frame for update form fields
        self.update_form_canvas = tk.Canvas(self.update_tab)
        self.update_form_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.update_tab, orient=tk.VERTICAL, command=self.update_form_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.update_form_canvas.configure(yscrollcommand=scrollbar.set)
        self.update_form_canvas.bind('<Configure>', lambda e: self.update_form_canvas.configure(scrollregion=self.update_form_canvas.bbox("all")))
        self.update_form_frame = ttk.Frame(self.update_form_canvas)
        self.update_form_canvas.create_window((0, 0), window=self.update_form_frame, anchor="nw")
        self.update_form_frame.pack_forget()

        # Fixed frame below the scrollable area for the Save button
        self.save_btn_frame = ttk.Frame(self.update_tab, padding=(10, 5))
        self.save_btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.save_btn = ttk.Button(self.save_btn_frame, text="Save Changes", command=self.save_updated_trade)
        self.save_btn.pack(anchor=tk.E)

        self.update_entries = {}

    def find_trade_for_update(self):
        strategy = self.upd_strategy.get().strip()
        date = self.upd_date.get().strip()
        instrument = self.upd_instrument.get().strip()
        if not (strategy and date and instrument):
            messagebox.showwarning("Missing Keys", "Please enter Strategy Name, Trade Date, and Instrument to find trade.")
            return
        if not os.path.exists(FILE_NAME):
            messagebox.showinfo("No Data", "No trade records found.")
            return

        with open(FILE_NAME, "r", newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)
            trades = list(reader)

        found = None
        for trade in trades:
            if trade[0] == strategy and trade[1] == date and trade[2] == instrument:
                found = trade
                break
        if not found:
            messagebox.showinfo("Not Found", "Specified trade does not exist.")
            self.update_form_frame.pack_forget()
            return

        for widget in self.update_form_frame.winfo_children():
            widget.destroy()
        self.update_entries.clear()
        self.update_form_frame.pack(fill=tk.BOTH, expand=True)

        lbl = ttk.Label(self.update_form_frame, text="Edit fields and click Save. Leave blank to keep current value.")
        lbl.pack(pady=5)

        # Create main frame for inputs, with horizontal layout
        main_frame = ttk.Frame(self.update_form_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Left scrollable frame for first 17 fields
        scroll_canvas = tk.Canvas(main_frame)
        scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=scroll_canvas.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scroll_canvas.bind('<Configure>', lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))

        scrollable_frame = ttk.Frame(scroll_canvas)
        scroll_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Add first 17 fields in scrollable_frame
        for idx, col in enumerate(headers[:17]):  # first 17 fields
            ttk.Label(scrollable_frame, text=col + ":").grid(row=idx, column=0, sticky=tk.W, padx=5, pady=3)
            entry = ttk.Entry(scrollable_frame, width=30)
            value = found[idx] if idx < len(found) else ""
            entry.insert(0, value)
            entry.grid(row=idx, column=1, sticky=tk.W, padx=5, pady=3)
            self.update_entries[col] = entry

        


    def save_updated_trade(self):
        updated_vals = {key: entry.get().strip() for key, entry in self.update_entries.items()}
        orig_key = (self.upd_strategy.get().strip(), self.upd_date.get().strip(), self.upd_instrument.get().strip())
        if not all(orig_key):
            messagebox.showerror("Error", "Original keys missing. Please re-search trade.")
            return
        with open(FILE_NAME, "r", newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)
            rows = list(reader)
        new_rows = []
        updated = False
        for row in rows:
            if row[0] == orig_key[0] and row[1] == orig_key[1] and row[2] == orig_key[2]:
                updated_row = [updated_vals.get(h, "") if updated_vals.get(h, "") != "" else row[i] for i, h in enumerate(headers)]
                new_rows.append(updated_row)
                updated = True
            else:
                new_rows.append(row)
        if updated:
            with open(FILE_NAME, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(new_rows)
            messagebox.showinfo("Success", "Trade updated successfully.")
            self.status_var.set(f"Trade '{orig_key[0]}' updated.")
            self.load_trades_into_table()
            self.update_form_frame.pack_forget()
            self.upd_strategy.delete(0, tk.END)
            self.upd_date.delete(0, tk.END)
            self.upd_instrument.delete(0, tk.END)
            self.notebook.select(self.display_tab)
        else:
            messagebox.showerror("Error", "Trade to update was not found.")

    def create_search_tab(self):
        self.search_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.search_tab, text="Search Trade")
        frame = ttk.LabelFrame(self.search_tab, text="Search Trade By", padding=10)
        frame.pack(fill=tk.X, pady=10)
        ttk.Label(frame, text="Strategy Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.search_strategy = ttk.Entry(frame, width=30)
        self.search_strategy.grid(row=0, column=1, padx=5)
        ttk.Label(frame, text="Trade Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.search_date = ttk.Entry(frame, width=30)
        self.search_date.grid(row=1, column=1, padx=5)
        ttk.Label(frame, text="Instrument:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.search_instrument = ttk.Entry(frame, width=30)
        self.search_instrument.grid(row=2, column=1, padx=5)
        search_btn = ttk.Button(frame, text="Search", command=self.search_trade)
        search_btn.grid(row=3, column=0, columnspan=2, pady=10)
        self.search_result = tk.Text(self.search_tab, height=13, font=("Segoe UI", 11))
        self.search_result.pack(fill=tk.BOTH, expand=True, pady=10)
        self.search_result.config(state=tk.DISABLED)

    def search_trade(self):
        strategy = self.search_strategy.get().strip()
        date = self.search_date.get().strip()
        instrument = self.search_instrument.get().strip()
        if not (strategy and date and instrument):
            messagebox.showwarning("Missing Input", "Please enter Strategy Name, Trade Date, and Instrument to search.")
            return
        if not os.path.exists(FILE_NAME):
            messagebox.showinfo("No Records", "No trade records found.")
            return
        with open(FILE_NAME, "r", newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)
            found = None
            for row in reader:
                if row[0] == strategy and row[1] == date and row[2] == instrument:
                    found = row
                    break
        self.search_result.config(state=tk.NORMAL)
        self.search_result.delete("1.0", tk.END)
        if found:
            for h, val in zip(headers, found):
                self.search_result.insert(tk.END, f"{h}: {val}\n")
            self.status_var.set(f"Trade '{strategy}' found.")
        else:
            self.search_result.insert(tk.END, "Trade record not found.")
            self.status_var.set("Trade not found.")
        self.search_result.config(state=tk.DISABLED)

    def clear_all_records(self):
        if messagebox.askyesno("Clear All Trades Confirmation",
                               "Are you sure you want to permanently clear ALL trade records?"):
            with open(FILE_NAME, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Strategy_Name", "Trade_Date", "Instrument", "Strike_Price", "Buy/Sell",
                    "Expiry_Date", "Type", "Lots", "Entry_Price", "Exit_Price",
                    "Hedged_Strike_Price", "Hedged_Buy/Sell", "Hedged_Entry_Price", "Hedged_Exit_Price",
                    "Margin_Used", "Holding_Period", "P&L"])
            self.load_trades_into_table()
            messagebox.showinfo("Records Cleared", "All trade records have been cleared.")
            self.status_var.set("All records cleared.")

if __name__ == "__main__":
    initialize_file()
    app = OptionSellingTracker()
    app.mainloop()
