import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("1000x600")
        
        self.movies = []
        self.filename = "movies.json"
        
        # Загрузка данных из файла
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы и фильтров
        self.update_filters()
        self.display_movies()
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(main_frame, text="Добавление нового фильма", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Поля ввода
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(input_frame, text="Жанр:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.genre_entry = ttk.Entry(input_frame, width=20)
        self.genre_entry.grid(row=0, column=3, padx=(0, 20))
        
        ttk.Label(input_frame, text="Год выпуска:").grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        self.year_entry = ttk.Entry(input_frame, width=10)
        self.year_entry.grid(row=0, column=5, padx=(0, 20))
        
        ttk.Label(input_frame, text="Рейтинг (0-10):").grid(row=0, column=6, sticky=tk.W, padx=(0, 10))
        self.rating_entry = ttk.Entry(input_frame, width=10)
        self.rating_entry.grid(row=0, column=7, padx=(0, 10))
        
        # Кнопка добавления
        self.add_button = ttk.Button(input_frame, text="Добавить фильм", command=self.add_movie)
        self.add_button.grid(row=0, column=8, padx=(10, 0))
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=(0, 10))
        self.genre_filter = ttk.Combobox(filter_frame, values=["Все жанры"], state="readonly", width=20)
        self.genre_filter.set("Все жанры")
        self.genre_filter.grid(row=0, column=1, padx=(0, 20))
        self.genre_filter.bind('<<ComboboxSelected>>', lambda e: self.filter_movies())
        
        ttk.Label(filter_frame, text="Фильтр по году:").grid(row=0, column=2, padx=(0, 10))
        self.year_filter = ttk.Combobox(filter_frame, values=["Все годы"], state="readonly", width=15)
        self.year_filter.set("Все годы")
        self.year_filter.grid(row=0, column=3, padx=(0, 20))
        self.year_filter.bind('<<ComboboxSelected>>', lambda e: self.filter_movies())
        
        # Кнопка сброса фильтров
        self.reset_button = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters)
        self.reset_button.grid(row=0, column=4, padx=(10, 0))
        
        # Таблица для отображения фильмов
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Создание таблицы
        columns = ("Название", "Жанр", "Год", "Рейтинг")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        # Настройка заголовков
        self.tree.heading("Название", text="Название")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Год", text="Год")
        self.tree.heading("Рейтинг", text="Рейтинг")
        
        # Настройка ширины колонок
        self.tree.column("Название", width=300)
        self.tree.column("Жанр", width=150)
        self.tree.column("Год", width=100)
        self.tree.column("Рейтинг", width=100)
        
        # Добавление скроллбаров
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Размещение таблицы и скроллбаров
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Настройка веса для растягивания
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def validate_input(self, title, genre, year, rating):
        """Проверка корректности ввода"""
        if not title or not genre:
            messagebox.showerror("Ошибка", "Название и жанр не могут быть пустыми!")
            return False
        
        try:
            year_int = int(year)
            current_year = datetime.now().year
            if year_int < 1888 or year_int > current_year:
                messagebox.showerror("Ошибка", 
                                   f"Год должен быть от 1888 до {current_year}!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом!")
            return False
        
        try:
            rating_float = float(rating)
            if rating_float < 0 or rating_float > 10:
                messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом!")
            return False
        
        return True
    
    def add_movie(self):
        """Добавление нового фильма"""
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year = self.year_entry.get().strip()
        rating = self.rating_entry.get().strip()
        
        if self.validate_input(title, genre, year, rating):
            movie = {
                "title": title,
                "genre": genre,
                "year": int(year),
                "rating": float(rating)
            }
            self.movies.append(movie)
            self.save_data()
            self.update_filters()
            self.filter_movies()
            
            # Очистка полей ввода
            self.title_entry.delete(0, tk.END)
            self.genre_entry.delete(0, tk.END)
            self.year_entry.delete(0, tk.END)
            self.rating_entry.delete(0, tk.END)
            
            # Фокус на поле названия
            self.title_entry.focus()
    
    def update_filters(self):
        """Обновление списков фильтров"""
        # Сохранение текущих значений
        current_genre = self.genre_filter.get()
        current_year = self.year_filter.get()
        
        # Обновление фильтра жанров
        genres = sorted(set(movie["genre"] for movie in self.movies))
        self.genre_filter['values'] = ["Все жанры"] + genres
        
        # Восстановление выбранного жанра, если он все еще существует
        if current_genre in self.genre_filter['values']:
            self.genre_filter.set(current_genre)
        else:
            self.genre_filter.set("Все жанры")
        
        # Обновление фильтра годов
        years = sorted(set(movie["year"] for movie in self.movies), reverse=True)
        self.year_filter['values'] = ["Все годы"] + [str(year) for year in years]
        
        # Восстановление выбранного года, если он все еще существует
        if current_year in self.year_filter['values']:
            self.year_filter.set(current_year)
        else:
            self.year_filter.set("Все годы")
    
    def filter_movies(self):
        """Фильтрация фильмов по выбранным критериям"""
        selected_genre = self.genre_filter.get()
        selected_year = self.year_filter.get()
        
        filtered_movies = self.movies.copy()
        
        # Фильтрация по жанру
        if selected_genre != "Все жанры":
            filtered_movies = [m for m in filtered_movies if m["genre"] == selected_genre]
        
        # Фильтрация по году
        if selected_year != "Все годы":
            filtered_movies = [m for m in filtered_movies if str(m["year"]) == selected_year]
        
        self.display_movies(filtered_movies)
    
    def display_movies(self, movies_list=None):
        """Отображение фильмов в таблице"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if movies_list is None:
            movies_list = self.movies
        
        # Добавление фильмов в таблицу
        for movie in movies_list:
            self.tree.insert("", tk.END, values=(
                movie["title"],
                movie["genre"],
                movie["year"],
                f"{movie['rating']:.1f}"
            ))
        
        # Обновление статуса
        count = len(movies_list)
        self.root.title(f"Movie Library - Личная кинотека ({count} фильмов)")
    
    def reset_filters(self):
        """Сброс всех фильтров"""
        self.genre_filter.set("Все жанры")
        self.year_filter.set("Все годы")
        self.filter_movies()
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.movies = json.load(f)
            except Exception as e:
                messagebox.showwarning("Предупреждение", 
                                      f"Не удалось загрузить данные: {str(e)}\nНачинаем с пустой библиотекой.")
                self.movies = []

def main():
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()

if __name__ == "__main__":
    main()
