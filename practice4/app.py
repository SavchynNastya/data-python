import tkinter as tk
from tkinter import messagebox
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt


class DetailView:
    def __init__(self, master, item):
        self.master = master
        self.item = item
        self.create_widgets()

    def create_widgets(self):
        detail_label = tk.Label(self.master, text=f"Selected Item Details:\n{self.item}")
        detail_label.pack()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Data Management Application")
        self.geometry("500x500")
        self.full_data = {}
        self.displayed_data = {}
        
        # Підключення до бази даних PostgreSQL
        self.conn = psycopg2.connect(
            host="localhost",
            database="advertisement_agency",
            user="postgres",
            password="root",
        )
        self.cur = self.conn.cursor()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Форма для додавання даних
        self.lbl_product_name = tk.Label(self, text="Product Name:")
        self.lbl_product_name.grid(row=0, column=0, sticky="w")
        self.entry_product_name = tk.Entry(self)
        self.entry_product_name.grid(row=0, column=1)
        
        self.lbl_description = tk.Label(self, text="Description:")
        self.lbl_description.grid(row=1, column=0, sticky="w")
        self.entry_description = tk.Entry(self)
        self.entry_description.grid(row=1, column=1)
        
        self.lbl_price = tk.Label(self, text="Price:")
        self.lbl_price.grid(row=2, column=0, sticky="w")
        self.entry_price = tk.Entry(self)
        self.entry_price.grid(row=2, column=1)
        
        self.btn_add = tk.Button(self, text="Add", command=self.add_data)
        self.btn_add.grid(row=3, columnspan=2, pady=5)
        
        # Пошук
        self.lbl_search = tk.Label(self, text="Search:")
        self.lbl_search.grid(row=4, column=0, sticky="w")
        self.entry_search = tk.Entry(self)
        self.entry_search.grid(row=4, column=1)
        
        self.btn_search = tk.Button(self, text="Search", command=self.search_data)
        self.btn_search.grid(row=5, columnspan=2, pady=5)
        
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        scrollbar.grid(row=6, column=2, sticky=tk.NS)

        self.display_area = tk.Listbox(self, height=10, width=40, yscrollcommand=scrollbar.set)
        self.display_area.grid(row=6, columnspan=2)
        scrollbar.config(command=self.display_area.yview)

        self.display_area.bind("<Double-Button-1>", self.open_detail_window)

        # Кнопка для візуалізації даних продуктів
        self.btn_visualize_products = tk.Button(self, text="Visualize Products Data", command=self.visualize_products_data)
        self.btn_visualize_products.grid(row=7, column=0, pady=5)

        # Кнопка для візуалізації даних продажів
        self.btn_visualize_sales = tk.Button(self, text="Visualize Sales Data", command=self.visualize_sales_data)
        self.btn_visualize_sales.grid(row=8, column=0, pady=5)
    
    def add_data(self):
        self.display_area.delete(0, tk.END)
        product_name = self.entry_product_name.get()
        description = self.entry_description.get()
        price = self.entry_price.get()
        
        if product_name and price:
            try:
                self.cur.execute("INSERT INTO products (product_name, description, price) VALUES (%s, %s, %s)", (product_name, description, price))
                self.conn.commit()
                self.display_data("Data added successfully!", "Products")
            except psycopg2.Error as e:
                messagebox.showerror("Error", f"Error adding data: {e}")
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def search_data(self):
        print(self.display_area)
        self.display_area.delete(0, tk.END)
        keyword = self.entry_search.get().lower()
        
        # Пошук в таблиці користувачів
        self.cur.execute("SELECT * FROM users WHERE LOWER(username) LIKE %s", ('%' + keyword + '%',))
        user_results = self.cur.fetchall()
        self.display_data(user_results, "Users")
        
        # Пошук в таблиці продуктів
        self.cur.execute("SELECT * FROM products WHERE LOWER(product_name) LIKE %s", ('%' + keyword + '%',))
        product_results = self.cur.fetchall()
        self.display_data(product_results, "Products")
        
        # Пошук в таблиці реклам
        self.cur.execute("SELECT * FROM advertisements WHERE LOWER(ad_name) LIKE %s", ('%' + keyword + '%',))
        ad_results = self.cur.fetchall()
        self.display_data(ad_results, "Advertisements")

        self.display_area.update_idletasks()

    def display_data(self, data, section):
        if data:
            self.display_area.insert(tk.END, f"{section}:")
            
            for item in data:
                text = ""
                if section == "Users":
                    text = f"{item[1]} ({item[3]})"
                elif section == "Products":
                    text = f"{item[1]}, {float(item[3])}"
                elif section == "Advertisements":
                    text = f"{item[1]}"
                self.display_area.insert(tk.END, text)
                self.display_area.bind("<Double-Button-1>", lambda event, x=item, y=section: self.open_detail_window(x, y))
        else:
            self.display_area.insert(tk.END, f"No matching data found in {section}.")
        self.display_area.see(tk.END)
        
    def update_user(self, user_data):
        sql = """
        UPDATE users
        SET username = %s,
            email = %s,
            role = %s
        WHERE user_id = %s;
        """
        self.cur.execute(sql, (user_data['username'], user_data['email'], user_data['role'], user_data['user_id']))
        self.conn.commit()

    def update_product(self, product_data):
        sql = """
        UPDATE products
        SET product_name = %s,
            description = %s,
            price = %s
        WHERE product_id = %s;
        """
        self.cur.execute(sql, (product_data['product_name'], product_data['description'], product_data['price'], product_data['product_id']))
        self.conn.commit()

    def update_advertisement(self, ad_data):
        sql = """
        UPDATE advertisements
        SET ad_name = %s,
            ad_description = %s
        WHERE ad_id = %s;
        """
        self.cur.execute(sql, (ad_data['ad_name'], ad_data['ad_description'], ad_data['ad_id']))
        self.conn.commit()

    def update_item(self, dict_item, section):
        dict_item = {key: entry.get() for key, entry in dict_item.items()}
        if section == "Products":
            self.update_product(product_data=dict_item)
        if section == "Users":
            self.update_user(user_data=dict_item)
        if section == "Advertisements":
            self.update_advertisement(ad_data=dict_item)
    
    def open_detail_window(self, item, section):
        dict_item = None
        if section == "Products":
            dict_item = {
                'product_id': item[0],
                'product_name': item[1],
                'description': item[2],
                'price': item[3]
            }
        if section == "Users":
            dict_item = {
                'user_id': item[0],
                'username': item[1],
                'email': item[3],
                'role': item[4]
            }
        if section == "Advertisements":
            dict_item = {
                'ad_id': item[0],
                'ad_name': item[1],
                'ad_description': item[2],
                'product_id': item[5]
            }
        
        detail_window = tk.Toplevel(self)
        detail_window.title("Detail Information")
        detail_label = tk.Label(detail_window, text="\n".join([f"{key}: {value}" for key, value in dict_item.items()]))
        detail_label.pack()

        entry_fields = {}
        for i, (key, value) in enumerate(dict_item.items()):
            label = tk.Label(detail_window, text=f"{key}:")
            label.pack(anchor='w', padx=10, pady=5)
            entry = tk.Entry(detail_window)
            entry.pack(anchor='w', padx=10, pady=5)
            entry.insert(0, str(value)) 
            entry_fields[key] = entry

        update_button = tk.Button(detail_window, text="Update", command=lambda: self.update_item(entry_fields, section))
        update_button.pack(pady=10)

    def visualize_products_data(self):
        self.cur.execute("SELECT * FROM products")
        data = self.cur.fetchall()
        df = pd.DataFrame(data, columns=['Product ID', 'Product Name', 'Description', 'Price'])
        
        plt.bar(df['Product Name'], df['Price'])
        plt.xlabel('Product Name')
        plt.ylabel('Price')
        plt.title('Product Prices')
        plt.xticks(rotation=45, ha='right')
        plt.show()

    def visualize_sales_data(self):
        self.cur.execute("SELECT * FROM sales")
        data = self.cur.fetchall()
        df = pd.DataFrame(data, columns=['Sale ID', 'Product ID', 'Quantity', 'Revenue', 'Advertisement ID'])
        
        plt.bar(df['Sale ID'], df['Revenue'])
        plt.xlabel('Sale ID')
        plt.ylabel('Revenue')
        plt.title('Sales Revenue')
        plt.show()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
