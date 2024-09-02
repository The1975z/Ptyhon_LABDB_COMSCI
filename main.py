import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv
import os
from typing import List, Tuple
from dataclasses import dataclass
import threading
import urllib.request
import json
import requests

# Load environment variables
load_dotenv()

# Database connection pool
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

@dataclass
class Character:
    id: int
    fname: str
    lname: str
    popularity: int
    anime_title: str
    anime_volumes: int

class DatabaseManager:
    @staticmethod
    def execute_query(query: str, params: Tuple = None) -> List[Tuple]:
        with connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    @staticmethod
    def execute_action(query: str, params: Tuple = None) -> int:
        with connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount

class AnimeCharacterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Anime Character Database By 67050651")
        master.geometry("1200x768")

        icon_path = r"C:\Users\PC\Desktop\Programing\Python LAB\The1975.gif"  
        icon_image = tk.PhotoImage(file=icon_path)  
        master.iconphoto(False, icon_image)  
        
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Arial", 12, "bold"), padding=[10, 10])
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10), padding=[5, 5])
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        style.configure("Treeview", font=("Arial", 10), rowheight=25)

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both")

        self.frames = {}
        for frame_name in ["assignment_frame", "search_frame", "insert_frame", "update_frame", "delete_frame", "labapi_frame", "labapimovie_frame"]:
            self.frames[frame_name] = ttk.Frame(self.notebook)
            self.notebook.add(self.frames[frame_name], text=frame_name.replace("_", " ").title())

        self.create_tabs()

    def create_tabs(self):
        self.create_assignment_tab()
        self.create_search_tab()
        self.create_insert_tab()
        self.create_update_tab()
        self.create_delete_tab()
        self.create_labapi_tab()
        self.create_labapimovie_tab()
        self.create_footer()
        self.search_characters()

    def create_assignment_tab(self):
        frame = self.frames["assignment_frame"]
        ttk.Label(frame, text="1.1 INNER JOIN and 1.2 LIKE operator:").pack(pady=5)
        explanation = "1.1 INNER JOIN: \n\n1.2 LIKE operator: \n"
        self.add_scrolled_text(frame, explanation, width=70, height=8)

        ttk.Button(frame, text="1.3 Search karakai-jouzu-no-takagi-san characters", 
                   command=self.search_takagi_characters).pack(pady=5)
        self.new_char_id = self.add_entry(frame, default_text="550650 (Change last 5 digits)")
        ttk.Button(frame, text="Insert Character", 
                   command=self.insert_new_character).pack(pady=5)
        ttk.Button(frame, text="1.5 Show last inserted character", 
                   command=self.show_last_inserted_character).pack(pady=5)

        self.result_text = self.add_scrolled_text(frame, "", width=70, height=10)

    def create_search_tab(self):
        frame = self.frames["search_frame"]
        ttk.Label(frame, text="Search Anime:").pack(pady=5)
        self.search_entry = ttk.Entry(frame, width=50)
        self.search_entry.pack(pady=5)
        ttk.Button(frame, text="Search", command=self.search_characters).pack(pady=5)

        columns = ("ID", "First Name", "Last Name", "Popularity", "Anime", "Volumes")
        self.result_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.result_tree.heading(col, text=col, anchor="center")
            self.result_tree.column(col, anchor="center")
        self.result_tree.pack(pady=10, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.result_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_tree.configure(yscrollcommand=scrollbar.set)

    def create_insert_tab(self):
        frame = self.frames["insert_frame"]
        fields = [("First Name:", "fname"), ("Last Name:", "lname"), ("Popularity:", "popularity"), ("Anime ID:", "anime_id")]
        self.create_form(frame, fields, self.insert_character)

    def create_update_tab(self):
        frame = self.frames["update_frame"]
        fields = [("Character ID:", "update_id"), ("First Name:", "update_fname"), 
                  ("Last Name:", "update_lname"), ("Popularity:", "update_popularity"), 
                  ("Anime ID:", "update_anime_id")]
        self.create_form(frame, fields, self.update_character)

    def create_delete_tab(self):
        frame = self.frames["delete_frame"]
        ttk.Label(frame, text="Character ID:").pack(pady=5)
        self.delete_id_entry = ttk.Entry(frame)
        self.delete_id_entry.pack(pady=5)
        ttk.Button(frame, text="Delete Character", command=self.delete_character).pack(pady=10)

    def create_labapi_tab(self):
        frame = self.frames["labapi_frame"]
        ttk.Label(frame, text="LABAPI: Select Resource ID and Request Data").pack(pady=5)

        resource_ids = ["87abdf57-7edd-4864-9766-7bb0e87272f9"]
        self.resource_id_combobox = ttk.Combobox(frame, width=50, values=resource_ids, state='readonly')
        self.resource_id_combobox.pack(pady=5)
        self.resource_id_combobox.set(resource_ids[0])

        ttk.Button(frame, text="Request Data", command=self.request_data).pack(pady=10)
        ttk.Button(frame, text="Clear Data", command=self.clear_data).pack(pady=10)
        self.labapi_result_text = self.add_scrolled_text(frame, "", width=70, height=20)

    def create_labapimovie_tab(self):
        frame = self.frames["labapimovie_frame"]
        ttk.Label(frame, text="LABAPIMOVIE: Search Movies").pack(pady=5)
        self.movie_search_entry = ttk.Entry(frame, width=50)
        self.movie_search_entry.pack(pady=5)
        ttk.Button(frame, text="Search", command=self.search_movie).pack(pady=10)
        ttk.Button(frame, text="Clear Data", command=self.clear_data).pack(pady=5)
        self.movie_result_text = self.add_scrolled_text(frame, "", width=70, height=20)

    def create_footer(self):
        footer = tk.Frame(self.master, bg="#2c3e50")
        footer.pack(side="bottom", fill="x", pady=5)
        footer_label = tk.Label(
            footer, 
            text="© 2024 LABAPI • Made with passion by The1975 & Scottz", 
            font=("Arial", 10), 
            bg="#2c3e50",   
            fg="white",    
            anchor="center"
        )
        footer_label.pack(pady=10)

    def add_entry(self, parent, default_text=""):
        entry = ttk.Entry(parent, width=30)
        entry.pack()
        entry.insert(0, default_text)
        return entry

    def add_scrolled_text(self, parent, text, width=70, height=10):
        scrolled_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, width=width, height=height)
        scrolled_text.pack(pady=5)
        scrolled_text.insert(tk.END, text)
        scrolled_text.configure(state='disabled')
        return scrolled_text

    def create_form(self, parent, fields, command):
        for i, (label, attr) in enumerate(fields):
            ttk.Label(parent, text=label).grid(row=i, column=0, padx=5, pady=5)
            setattr(self, f"{attr}_entry", ttk.Entry(parent))
            getattr(self, f"{attr}_entry").grid(row=i, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Submit", command=command).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def request_data(self):
        resource_id = self.resource_id_combobox.get().strip()
        if not resource_id:
            messagebox.showwarning("Input Error", "Please select a Resource ID.")
            return

        api_url = f"https://opend.data.go.th/get-ckan/datastore_search?resource_id={resource_id}&limit=5"
        headers = {'api-key': 'eU2UNvnnHrteGgyW9WxR8UExq7As8qML'}

        def fetch_data():
            try:
                req = urllib.request.Request(api_url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    content = response.read()
                    encoding = response.info().get_content_charset('utf-8')
                    JSON_object = json.loads(content.decode(encoding))
                    formatted_json = json.dumps(JSON_object, indent=4, ensure_ascii=False)
                    self.update_scrolled_text(self.labapi_result_text, formatted_json)
            except Exception as e:
                self.master.after(0, lambda: messagebox.showerror("Request Error", f"An error occurred: {str(e)}"))

        threading.Thread(target=fetch_data, daemon=True).start()

    def search_movie(self):
        movie_name = self.movie_search_entry.get().strip()
        if not movie_name:
            messagebox.showwarning("Input Error", "Please enter a movie name.")
            return

        url = "https://online-movie-database.p.rapidapi.com/auto-complete"
        querystring = {"q": movie_name}
        headers = {
            "X-RapidAPI-Key": "66440edc5fmsh40a62f7c167eb63p16829bjsn9d75c87742ab",
            "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
        }

        def fetch_movie_data():
            try:
                response = requests.get(url, headers=headers, params=querystring)
                results = [movie["l"] for movie in response.json().get("d", [])]
                self.update_scrolled_text(self.movie_result_text, "\n".join(results) if results else "No results found.")
            except Exception as e:
                self.master.after(0, lambda: messagebox.showerror("Request Error", f"An error occurred: {str(e)}"))

        threading.Thread(target=fetch_movie_data, daemon=True).start()

    def search_characters(self):
        search_term = self.search_entry.get().strip()

        def search():
            query = """
            SELECT c.id, c.fName, c.lName, c.popularity, a.title, a.numOfVolume
            FROM characters c
            INNER JOIN anime a ON c.animeFK = a.id
            WHERE a.title LIKE %s
            """
            params = (f"%{search_term}%",) if search_term else ("%",)
            try:
                results = DatabaseManager.execute_query(query, params)
                self.update_tree(results)
            except mysql.connector.Error as err:
                self.master.after(0, lambda: messagebox.showerror("Database Error", f"An error occurred: {err}"))

        threading.Thread(target=search, daemon=True).start()

    def update_tree(self, results):
        self.result_tree.delete(*self.result_tree.get_children())
        for row in results:
            self.result_tree.insert("", "end", values=(f"{row[0]:08d}", *row[1:]))

    def insert_character(self):
        def insert():
            try:
                params = (
                    self.fname_entry.get().strip(),
                    self.lname_entry.get().strip(),
                    int(self.popularity_entry.get().strip()),
                    int(self.anime_id_entry.get().strip())
                )
                if not all(params[:2]):
                    raise ValueError("First Name and Last Name are required.")

                query = "INSERT INTO characters (fName, lName, popularity, animeFK) VALUES (%s, %s, %s, %s)"
                if DatabaseManager.execute_action(query, params):
                    self.master.after(0, lambda: messagebox.showinfo("Success", "Character inserted successfully!"))
                    self.clear_entries(["fname_entry", "lname_entry", "popularity_entry", "anime_id_entry"])
                    self.search_characters()
            except (ValueError, mysql.connector.Error) as err:
                self.master.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {err}"))

        threading.Thread(target=insert, daemon=True).start()

    def update_character(self):
        def update():
            try:
                params = (
                    self.update_fname_entry.get().strip(),
                    self.update_lname_entry.get().strip(),
                    int(self.update_popularity_entry.get().strip()) if self.update_popularity_entry.get().strip() else None,
                    int(self.update_anime_id_entry.get().strip()) if self.update_anime_id_entry.get().strip() else None,
                    int(self.update_id_entry.get().strip())
                )
                if not params[-1]:
                    raise ValueError("Character ID is required.")

                query = """
                UPDATE characters SET fName = %s, lName = %s, popularity = %s, animeFK = %s WHERE id = %s
                """
                if DatabaseManager.execute_action(query, params):
                    self.master.after(0, lambda: messagebox.showinfo("Success", "Character updated successfully!"))
                    self.clear_entries(["update_id_entry", "update_fname_entry", "update_lname_entry", "update_popularity_entry", "update_anime_id_entry"])
                    self.search_characters()
            except (ValueError, mysql.connector.Error) as err:
                self.master.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {err}"))

        threading.Thread(target=update, daemon=True).start()

    def delete_character(self):
        def delete():
            try:
                char_id = int(self.delete_id_entry.get().strip())
                if not char_id:
                    raise ValueError("Character ID is required.")

                query = "DELETE FROM characters WHERE id = %s"
                if DatabaseManager.execute_action(query, (char_id,)):
                    self.master.after(0, lambda: messagebox.showinfo("Success", "Character deleted successfully!"))
                    self.delete_id_entry.delete(0, 'end')
                    self.search_characters()
            except (ValueError, mysql.connector.Error) as err:
                self.master.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {err}"))

        threading.Thread(target=delete, daemon=True).start()

    def search_takagi_characters(self):
        def search():
            query = "SELECT c.fName, c.lName FROM characters c INNER JOIN anime a ON c.animeFK = a.id WHERE a.title = 'karakai-jouzu-no-takagi-san'"
            try:
                results = DatabaseManager.execute_query(query)
                self.update_scrolled_text(self.result_text, "Takagi-san characters:\n" + "\n".join(f"{fname} {lname}" for fname, lname in results))
            except mysql.connector.Error as err:
                self.master.after(0, lambda: messagebox.showerror("Database Error", f"An error occurred: {err}"))

        threading.Thread(target=search, daemon=True).start()

    def insert_new_character(self):
        def insert():
            try:
                char_id = int(self.new_char_id.get().strip())
                if not 550000 <= char_id <= 559999:
                    raise ValueError("ID must be between 550000 and 559999")
                
                query = "INSERT INTO characters (id, fName, lName, popularity, animeFK) VALUES (%s, %s, %s, %s, %s)"
                if DatabaseManager.execute_action(query, (char_id, 'New', 'Character', 50, 1)):
                    self.master.after(0, lambda: messagebox.showinfo("Success", f"Character with ID {char_id} inserted successfully!"))
                    self.show_last_inserted_character()
            except (ValueError, mysql.connector.Error) as err:
                self.master.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {err}"))

        threading.Thread(target=insert, daemon=True).start()

    def show_last_inserted_character(self):
        def fetch():
            query = "SELECT c.id, c.fName, c.lName, c.popularity, a.title FROM characters c INNER JOIN anime a ON c.animeFK = a.id ORDER BY c.id DESC LIMIT 1"
            try:
                results = DatabaseManager.execute_query(query)
                if results:
                    character = results[0]
                    self.update_scrolled_text(self.result_text, f"Last inserted character:\nID: {character[0]}\nName: {character[1]} {character[2]}\nPopularity: {character[3]}\nAnime: {character[4]}")
                else:
                    self.master.after(0, lambda: messagebox.showinfo("Info", "No characters found."))
            except mysql.connector.Error as err:
                self.master.after(0, lambda: messagebox.showerror("Database Error", f"An error occurred: {err}"))

        threading.Thread(target=fetch, daemon=True).start()

    def update_scrolled_text(self, scrolled_text, text):
        scrolled_text.configure(state='normal')
        scrolled_text.delete(1.0, tk.END)
        scrolled_text.insert(tk.END, text)
        scrolled_text.configure(state='disabled')

    def clear_entries(self, entry_names):
        for entry_name in entry_names:
            getattr(self, entry_name).delete(0, 'end')

    def clear_data(self):
        if hasattr(self, 'labapi_result_text'):
            self.labapi_result_text.configure(state='normal')
            self.labapi_result_text.delete(1.0, tk.END)
            self.labapi_result_text.configure(state='disabled')
        if hasattr(self, 'movie_result_text'):
            self.movie_result_text.configure(state='normal')
            self.movie_result_text.delete(1.0, tk.END)
            self.movie_result_text.configure(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimeCharacterGUI(root)
    root.mainloop()
