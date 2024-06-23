import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

def init_db():
    conn = sqlite3.connect('todo_list.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority INTEGER,
            due_date DATE,
            category TEXT,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Application")
        self.root.geometry("700x500")

        self.task_frame = tk.Frame(root, bd=2, relief="solid")
        self.task_frame.pack(pady=10, padx=10, fill='both', expand=True)

        self.add_button = tk.Button(root, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.update_button = tk.Button(root, text="Update Task", command=self.update_task)
        self.update_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.delete_button = tk.Button(root, text="Delete Task", command=self.delete_task)
        self.delete_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.filter_button = tk.Button(root, text="Filter Tasks", command=self.filter_tasks)
        self.filter_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.category_filter = tk.StringVar()
        self.category_filter.set("All")

        self.category_dropdown = tk.OptionMenu(root, self.category_filter, "All", "Work", "Personal", "Home", "Others")
        self.category_dropdown.pack(side=tk.LEFT, padx=10, pady=10)

        self.tasks = {}  # Dictionary to store tasks and their checkbutton variables
        self.load_tasks()

    def get_db_connection(self):
        return sqlite3.connect('todo_list.db')

    def load_tasks(self):
        for widget in self.task_frame.winfo_children():
            widget.destroy()

        self.tasks.clear()  # Clear the task dictionary

        conn = self.get_db_connection()
        cursor = conn.cursor()

        category_filter = self.category_filter.get()

        if category_filter == "All":
            cursor.execute("SELECT id, title, description, priority, due_date, category, completed FROM tasks")
        else:
            cursor.execute("SELECT id, title, description, priority, due_date, category, completed FROM tasks WHERE category = ?", (category_filter,))

        for row in cursor.fetchall():
            self.create_task_widget(row)
        conn.close()

    def create_task_widget(self, task):
        task_id, title, description, priority, due_date, category, completed = task
        task_frame = tk.Frame(self.task_frame)
        task_frame.pack(fill='x', pady=2, padx=2, anchor='w')

        var = tk.BooleanVar(value=completed)
        checkbox = tk.Checkbutton(task_frame, variable=var, command=lambda t=task_id, v=var: self.toggle_completion(t, v))
        checkbox.pack(side=tk.LEFT)

        task_label = tk.Label(task_frame, text=f"{title} - {description} (Priority: {priority}, Due: {due_date}, Category: {category})", anchor='w')
        task_label.pack(side=tk.LEFT, padx=5)

        self.tasks[task_id] = var  # Store the variable in the dictionary

    def add_task(self):
        title = simpledialog.askstring("Input", "Task Title:")
        if title:
            description = simpledialog.askstring("Input", "Task Description:")
            priority = simpledialog.askinteger("Input", "Task Priority (1-5):", minvalue=1, maxvalue=5)
            due_date = simpledialog.askstring("Input", "Due Date (YYYY-MM-DD):")
            category = simpledialog.askstring("Input", "Task Category:")
            completed = False

            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (title, description, priority, due_date, category, completed)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, description, priority, due_date, category, completed))
            conn.commit()
            conn.close()
            self.load_tasks()

    def update_task(self):
        selected_task_id = self.get_selected_task_id()
        if selected_task_id is None:
            messagebox.showwarning("Warning", "No task selected!")
            return

        title = simpledialog.askstring("Input", "New Task Title:")
        if title:
            description = simpledialog.askstring("Input", "New Task Description:")
            priority = simpledialog.askinteger("Input", "New Task Priority (1-5):", minvalue=1, maxvalue=5)
            due_date = simpledialog.askstring("Input", "New Due Date (YYYY-MM-DD):")
            category = simpledialog.askstring("Input", "New Task Category:")

            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tasks
                SET title = ?, description = ?, priority = ?, due_date = ?, category = ?
                WHERE id = ?
            ''', (title, description, priority, due_date, category, selected_task_id))
            conn.commit()
            conn.close()
            self.load_tasks()

    def delete_task(self):
        selected_task_id = self.get_selected_task_id()
        if selected_task_id is None:
            messagebox.showwarning("Warning", "No task selected!")
            return

        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (selected_task_id,))
        conn.commit()
        conn.close()
        self.load_tasks()

    def toggle_completion(self, task_id, var):
        completed = var.get()
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (completed, task_id))
        conn.commit()
        conn.close()

    def filter_tasks(self):
        self.load_tasks()

    def get_selected_task_id(self):
        for task_id, var in self.tasks.items():
            if var.get():
                return task_id
        return None

root = tk.Tk()
app = ToDoApp(root)
root.mainloop()
