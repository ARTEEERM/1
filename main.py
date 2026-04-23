import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import requests

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("900x700")

        # Файлы для хранения данных
        self.favorites_file = "favorites.json"
        self.favorites = []
        self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Панель поиска
        search_frame = ttk.LabelFrame(self.root, text="Поиск пользователя GitHub")
        search_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(search_frame, text="Имя пользователя:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)

        search_btn = ttk.Button(search_frame, text="Найти", command=self.search_user)
        search_btn.pack(side="left", padx=5)

        # Кнопки управления избранным
        fav_frame = ttk.Frame(self.root)
        fav_frame.pack(pady=5, padx=10, fill="x")

        add_fav_btn = ttk.Button(fav_frame, text="Добавить в избранное", command=self.add_to_favorites)
        add_fav_btn.pack(side="left", padx=5)

        remove_fav_btn = ttk.Button(fav_frame, text="Удалить из избранного", command=self.remove_from_favorites)
        remove_fav_btn.pack(side="left", padx=5)

        refresh_fav_btn = ttk.Button(fav_frame, text="Обновить избранное", command=self.refresh_favorites)
        refresh_fav_btn.pack(side="left", padx=5)

        # Результаты поиска
        results_frame = ttk.LabelFrame(self.root, text="Результаты поиска")
        results_frame.pack(pady=10, padx=10, fill="both", expand=True)

        columns = ("login", "name", "public_repos", "followers", "location", "created_at")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=12)

        self.results_tree.heading("login", text="Логин")
        self.results_tree.heading("name", text="Имя")
        self.results_tree.heading("public_repos", text="Репозитории")
        self.results_tree.heading("followers", text="Подписчики")
        self.results_tree.heading("location", text="Локация")
        self.results_tree.heading("created_at", text="Дата создания")

        self.results_tree.column("login", width=120)
        self.results_tree.column("name", width=150)
        self.results_tree.column("public_repos", width=100)
        self.results_tree.column("followers", width=100)
        self.results_tree.column("location", width=150)
        self.results_tree.column("created_at", width=120)

        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        self.results_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Избранное
        favorites_frame = ttk.LabelFrame(self.root, text="Избранное")
        favorites_frame.pack(pady=10, padx=10, fill="both", expand=True)

        fav_columns = ("login", "name", "public_repos", "followers")
        self.favorites_tree = ttk.Treeview(favorites_frame, columns=fav_columns, show="headings", height=8)

        self.favorites_tree.heading("login", text="Логин")
        self.favorites_tree.heading("name", text="Имя")
        self.favorites_tree.heading("public_repos", text="Репозитории")
        self.favorites_tree.heading("followers", text="Подписчики")

        self.favorites_tree.column("login", width=150)
        self.favorites_tree.column("name", width=250)
        self.favorites_tree.column("public_repos", width=120)
        self.favorites_tree.column("followers", width=120)

        fav_scrollbar = ttk.Scrollbar(favorites_frame, orient="vertical", command=self.favorites_tree.yview)
        self.favorites_tree.configure(yscrollcommand=fav_scrollbar.set)

        self.favorites_tree.pack(side="left", fill="both", expand=True)
        fav_scrollbar.pack(side="right", fill="y")


        self.refresh_favorites()

    def validate_input(self):
        """Проверка корректности ввода"""
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не может быть пустым!")
            return False
        return True, username

    def search_user(self):
        """Поиск пользователя на GitHub"""
        validation_result = self.validate_input()
        if not validation_result:
            return

        username = validation_result[1]

        try:
            response = requests.get(f"https://api.github.com/users/{username}")
            if response.status_code == 200:
                user_data = response.json()
                self.display_search_result(user_data)
            elif response.status_code == 404:
                messagebox.showwarning("Предупреждение", f"Пользователь '{username}' не найден!")
            else:
                messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка сети", f"Не удалось подключиться к GitHub API: {e}")

    def display_search_result(self, user_data):
        """Отображение результатов поиска"""
        # Очищаем таблицу
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Добавляем найденного пользователя
        self.results_tree.insert("", "end", values=(
            user_data.get("login", "N/A"),
            user_data.get("name", "N/A"),
            user_data.get("public_repos", 0),
            user_data.get("followers", 0),
            user_data.get("location", "N/A"),
            user_data.get("created_at", "N/A")[:10]  # Только дата без времени
        ))

    def add_to_favorites(self):
        """Добавление пользователя в избранное"""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из результатов поиска!")
            return

        item = self.results_tree.item(selection[0])
        user_data = {
            "login": item["values"][0],
            "name": item["values"][1],
            "public
