import os
import mysql.connector
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *

load_dotenv()
PASSKEY = os.getenv('PASSKEY')

class StockManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Stocks - Tableau de Bord")
        self.root.geometry("1200x700")

        self.connect_to_db()
        
        self.create_dashboard()

        self.load_products()
    
    def connect_to_db(self):
        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password=PASSKEY,
                database="store_SQL"
            )
            if self.mydb.is_connected():
                db_info = self.mydb.get_server_info()
                print(f"Connected to MySQL version {db_info}")
                self.cursor = self.mydb.cursor(buffered=True)
        except mysql.connector.Error as e:
            messagebox.showerror("Erreur de connexion", f"Impossible de se connecter à la base de données: {e}")
            self.root.destroy()
    
    def create_dashboard(self):
        self.sidebar = tb.Frame(self.root, bootstyle="dark")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        logo_frame = tb.Frame(self.sidebar, bootstyle="dark")
        logo_frame.pack(pady=20, padx=10)
        tb.Label(logo_frame, text="STORE", font=("Arial", 24, "bold"), 
                bootstyle="inverse-dark").pack()
        tb.Label(logo_frame, text="Gestion des stocks", 
                bootstyle="inverse-dark").pack()
        
        btn_frame = tb.Frame(self.sidebar, bootstyle="dark")
        btn_frame.pack(fill=tk.X, pady=20)
        
        tb.Button(btn_frame, text="Tableau de bord", width=20, 
                 bootstyle="outline-light", command=self.show_dashboard).pack(pady=5)
        tb.Button(btn_frame, text="Ajouter un produit", width=20, 
                 bootstyle="outline-success", command=self.add_product).pack(pady=5)
        tb.Button(btn_frame, text="Actualiser", width=20, 
                 bootstyle="outline-info", command=self.load_products).pack(pady=5)
        
        self.main_frame = tb.Frame(self.root)
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        header_frame = tb.Frame(self.main_frame, bootstyle="light")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tb.Label(header_frame, text="Tableau de Bord", 
                font=("Arial", 18, "bold")).pack(side=tk.LEFT)
        
        search_frame = tb.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_products)
        search_entry = tb.Entry(search_frame, width=30, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5)
        tb.Label(search_frame, text="🔍").pack(side=tk.LEFT)
        
        stats_frame = tb.Frame(self.main_frame)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.total_products_var = tk.StringVar(value="0")
        self.total_value_var = tk.StringVar(value="0 €")
        self.low_stock_var = tk.StringVar(value="0")
        
        self.create_stat_card(stats_frame, "Total Produits", self.total_products_var, "info")
        self.create_stat_card(stats_frame, "Valeur Totale", self.total_value_var, "success")
        self.create_stat_card(stats_frame, "Stock Faible (<10)", self.low_stock_var, "danger")
        
        table_frame = tb.Frame(self.main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        scrollbar = tb.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("id", "name", "description", "price", "quantity", "category")
        self.product_table = tb.Treeview(table_frame, columns=columns, show="headings", 
                                        yscrollcommand=scrollbar.set, bootstyle="info")
        scrollbar.config(command=self.product_table.yview)
        
        self.product_table.heading("id", text="ID")
        self.product_table.heading("name", text="Nom")
        self.product_table.heading("description", text="Description")
        self.product_table.heading("price", text="Prix (€)")
        self.product_table.heading("quantity", text="Quantité")
        self.product_table.heading("category", text="Catégorie")
        
        self.product_table.column("id", width=50, anchor=tk.CENTER)
        self.product_table.column("name", width=150)
        self.product_table.column("description", width=300)
        self.product_table.column("price", width=100, anchor=tk.E)
        self.product_table.column("quantity", width=100, anchor=tk.CENTER)
        self.product_table.column("category", width=150)
        
        self.product_table.pack(fill=tk.BOTH, expand=True)
        
        self.product_table.bind("<Button-3>", self.show_context_menu)
        self.product_table.bind("<Double-1>", self.edit_product)
        
        status_frame = tb.Frame(self.main_frame, bootstyle="light")
        status_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.status_var = tk.StringVar(value="Prêt")
        tb.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
    
    def create_stat_card(self, parent, title, value_var, style):
        card = tb.Frame(parent, bootstyle=style)
        card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        
        tb.Label(card, text=title, font=("Arial", 12), bootstyle=f"inverse-{style}").pack(pady=5)
        tb.Label(card, textvariable=value_var, font=("Arial", 20, "bold"), bootstyle=f"inverse-{style}").pack(pady=10)

    def show_dashboard(self):
        self.load_products()

    def load_products(self):
        for item in self.product_table.get_children():
            self.product_table.delete(item)
        
        try:
            query = """
            SELECT p.id, p.name, p.description, p.price, p.quantity, c.name
            FROM product p
            LEFT JOIN category c ON p.id_category = c.id
            ORDER BY p.id
            """
            self.cursor.execute(query)
            products = self.cursor.fetchall()
            
            total_products = len(products)
            total_value = sum(p[3] * p[4] for p in products) / 100  
            low_stock = sum(1 for p in products if p[4] < 10)
            
            self.total_products_var.set(str(total_products))
            self.total_value_var.set(f"{total_value:.2f} €")
            self.low_stock_var.set(str(low_stock))
            
            for product in products:
                price_display = f"{product[3]/100:.2f}"
                
                if product[4] < 5:
                    tag = "low"
                elif product[4] < 10:
                    tag = "medium"
                else:
                    tag = "normal"
                
                self.product_table.insert("", tk.END, values=(
                    product[0], product[1], product[2], price_display, product[4], product[5]
                ), tags=(tag,))
            
            self.product_table.tag_configure("low", background="#ffcccc")
            self.product_table.tag_configure("medium", background="#ffffcc")
            self.product_table.tag_configure("normal", background="white")
            
            self.status_var.set(f"Chargé {total_products} produits")
        except mysql.connector.Error as e:
            messagebox.showerror("Erreur", f"Impossible de charger les produits: {e}")

    def search_products(self, *args):
        search_term = self.search_var.get().lower()
        
        for item in self.product_table.get_children():
            self.product_table.delete(item)
        
        try:
            query = """
            SELECT p.id, p.name, p.description, p.price, p.quantity, c.name
            FROM product p
            LEFT JOIN category c ON p.id_category = c.id
            WHERE LOWER(p.name) LIKE %s OR LOWER(p.description) LIKE %s OR LOWER(c.name) LIKE %s
            ORDER BY p.id
            """
            search_param = f"%{search_term}%"
            self.cursor.execute(query, (search_param, search_param, search_param))
            products = self.cursor.fetchall()
            
            for product in products:
                price_display = f"{product[3]/100:.2f}"
                
                if product[4] < 5:
                    tag = "low"
                elif product[4] < 10:
                    tag = "medium"
                else:
                    tag = "normal"
                
                self.product_table.insert("", tk.END, values=(
                    product[0], product[1], product[2], price_display, product[4], product[5]
                ), tags=(tag,))
            
            self.status_var.set(f"Trouvé {len(products)} produits")
        except mysql.connector.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche: {e}")

    def show_context_menu(self, event):
        iid = self.product_table.identify_row(event.y)
        if iid:
            self.product_table.selection_set(iid)
            
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Modifier", command=lambda: self.edit_product(None))
            context_menu.add_command(label="Supprimer", command=self.delete_product)
            
            context_menu.post(event.x_root, event.y_root)

    def get_categories(self):
        self.cursor.execute("SELECT id, name FROM category ORDER BY name")
        return self.cursor.fetchall()

    def add_product(self):
        add_window = tb.Toplevel(self.root)
        add_window.title("Ajouter un produit")
        add_window.geometry("500x500")
        add_window.grab_set()  
        
        form_frame = tb.Frame(add_window, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        tb.Label(form_frame, text="Ajouter un nouveau produit", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=15)
        
        tb.Label(form_frame, text="Nom:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = tb.Entry(form_frame, width=40, bootstyle="default")
        name_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tb.Label(form_frame, text="Description:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        desc_text = tk.Text(form_frame, width=30, height=5)
        desc_text.grid(row=2, column=1, padx=10, pady=10)
        
        tb.Label(form_frame, text="Prix (€):").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        price_entry = tb.Entry(form_frame, width=40, bootstyle="default")
        price_entry.grid(row=3, column=1, padx=10, pady=10)
        
        tb.Label(form_frame, text="Quantité:").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        quantity_entry = tb.Entry(form_frame, width=40, bootstyle="default")
        quantity_entry.grid(row=4, column=1, padx=10, pady=10)
        tb.Label(form_frame, text="Catégorie:").grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
    
        categories = self.get_categories()
        category_names = [cat[1] for cat in categories]
        category_ids = [cat[0] for cat in categories]
        
        category_var = tk.StringVar()
        category_combo = tb.Combobox(form_frame, textvariable=category_var, values=category_names, width=38, bootstyle="default")
        category_combo.grid(row=5, column=1, padx=10, pady=10)
        
        if categories:
            category_combo.current(0)
        
        btn_frame = tb.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        tb.Button(btn_frame, text="Annuler", bootstyle="secondary", 
                command=add_window.destroy, width=15).pack(side=tk.LEFT, padx=5)
        
        def save_product():
            try:
                name = name_entry.get().strip()
                description = desc_text.get("1.0", tk.END).strip()
                
                if not name:
                    messagebox.showerror("Erreur", "Le nom du produit est obligatoire")
                    return
                
                try:
                    price = int(float(price_entry.get()) * 100)
                    quantity = int(quantity_entry.get())
                except ValueError:
                    messagebox.showerror("Erreur", "Le prix et la quantité doivent être des nombres valides")
                    return
                
                category_index = category_names.index(category_var.get())
                category_id = category_ids[category_index]
                
                query = """
                INSERT INTO product (name, description, price, quantity, id_category)
                VALUES (%s, %s, %s, %s, %s)
                """
                self.cursor.execute(query, (name, description, price, quantity, category_id))
                self.mydb.commit()
                
                messagebox.showinfo("Succès", "Produit ajouté avec succès!")
                add_window.destroy()
                self.load_products()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'ajout du produit: {e}")
        
        tb.Button(btn_frame, text="Enregistrer", bootstyle="success", 
                command=save_product, width=15).pack(side=tk.LEFT, padx=5)

    def edit_product(self, event=None):
        selected_item = self.product_table.selection()
        if not selected_item:
            messagebox.showinfo("Information", "Veuillez sélectionner un produit à modifier")
            return
        
        product_id = self.product_table.item(selected_item[0], "values")[0]
        
        self.cursor.execute("SELECT * FROM product WHERE id = %s", (product_id,))
        product = self.cursor.fetchone()
        
        edit_window = tb.Toplevel(self.root)
        edit_window.title("Modifier un produit")
        edit_window.geometry("500x500")
        edit_window.grab_set()  
        
        form_frame = tb.Frame(edit_window, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        tb.Label(form_frame, text=f"Modifier le produit #{product_id}", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=15)
        
        tb.Label(form_frame, text="Nom:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = tb.Entry(form_frame, width=40, bootstyle="default")
        name_entry.insert(0, product[1])
        name_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tb.Label(form_frame, text="Description:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        desc_text = tk.Text(form_frame, width=30, height=5)
        desc_text.insert("1.0", product[2])
        desc_text.grid(row=2, column=1, padx=10, pady=10)
        
        tb.Label(form_frame, text="Prix (€):").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        price_entry = tb.Entry(form_frame, width=40, bootstyle="default")
        price_entry.insert(0, f"{product[3]/100:.2f}")
        price_entry.grid(row=3, column=1, padx=10, pady=10)
        
        tb.Label(form_frame, text="Quantité:").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        quantity_entry = tb.Entry(form_frame, width=40, bootstyle="default")
        quantity_entry.insert(0, product[4])
        quantity_entry.grid(row=4, column=1, padx=10, pady=10)
        
        tb.Label(form_frame, text="Catégorie:").grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        
        categories = self.get_categories()
        category_names = [cat[1] for cat in categories]
        category_ids = [cat[0] for cat in categories]
        
        category_var = tk.StringVar()
        category_combo = tb.Combobox(form_frame, textvariable=category_var, values=category_names, width=38, bootstyle="default")
        category_combo.grid(row=5, column=1, padx=10, pady=10)
        
        try:
            current_category_index = category_ids.index(product[5])
            category_combo.current(current_category_index)
        except (ValueError, IndexError):
            if categories:
                category_combo.current(0)
        
        btn_frame = tb.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        tb.Button(btn_frame, text="Annuler", bootstyle="secondary", 
                command=edit_window.destroy, width=15).pack(side=tk.LEFT, padx=5)
        
        def update_product():
            try:
                name = name_entry.get().strip()
                description = desc_text.get("1.0", tk.END).strip()
                
                if not name:
                    messagebox.showerror("Erreur", "Le nom du produit est obligatoire")
                    return
                
                try:
                    price = int(float(price_entry.get()) * 100)
                    quantity = int(quantity_entry.get())
                except ValueError:
                    messagebox.showerror("Erreur", "Le prix et la quantité doivent être des nombres valides")
                    return
                
                category_index = category_names.index(category_var.get())
                category_id = category_ids[category_index]
                
                query = """
                UPDATE product 
                SET name = %s, description = %s, price = %s, quantity = %s, id_category = %s
                WHERE id = %s
                """
                self.cursor.execute(query, (name, description, price, quantity, category_id, product_id))
                self.mydb.commit()
                
                messagebox.showinfo("Succès", "Produit mis à jour avec succès!")
                edit_window.destroy()
                self.load_products()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la mise à jour du produit: {e}")
        
        tb.Button(btn_frame, text="Enregistrer", bootstyle="success", 
                 command=update_product, width=15).pack(side=tk.LEFT, padx=5)
    
    def delete_product(self):
        selected_item = self.product_table.selection()
        if not selected_item:
            messagebox.showinfo("Information", "Veuillez sélectionner un produit à supprimer")
            return
        
        product_id = self.product_table.item(selected_item[0], "values")[0]
        product_name = self.product_table.item(selected_item[0], "values")[1]
        
        confirm = messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer le produit '{product_name}' ?")
        if not confirm:
            return
        
        try:
            self.cursor.execute("DELETE FROM product WHERE id = %s", (product_id,))
            self.mydb.commit()
            
            messagebox.showinfo("Succès", "Produit supprimé avec succès!")
            self.load_products()
        except mysql.connector.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression du produit: {e}")
    
    def __del__(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'mydb') and self.mydb.is_connected():
            self.mydb.close()
            print("Connexion à la base de données fermée")


if __name__ == "__main__":
    root = tb.Window(themename="litera")  # << THEMES : cosmo, flatly, journal, litera, lumen, minty, pulse, sandstone, united, yeti
    app = StockManagerApp(root)
    root.mainloop()