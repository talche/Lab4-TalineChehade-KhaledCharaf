#FYI the edit and delete buttons appear after selecting a student/instructor/course
#display all button can act as refresh too

import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox, filedialog
import csv

"""[Summary]
:param [ParamName]: [ParamDescription], defaults to [DefaultParamVal]
:type [ParamName]: [ParamType](, optional)
...
:raises [ErrorType]: [ErrorDescription]
...
:return: [ReturnDescription]
:rty
"""

class App(tk.Tk):
    """ This is a Tkinter application for a school management system.
    It uses an SQLite database to store data about the students, courses and instructors.
    It offers a graphical user interface to create, remove, edit the data of this school, and allows to register students to the active courses. 
    """
    def __init__(self):
        """Constructor of the application. This sets the application running."""
        super().__init__()
        self.title("School Management System")
        self.geometry("800x600")
        
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6)
        self.style.configure("TLabel", padding=5)
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        
        self.connection = None
        self.cursor = None
        self.make_database()

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=1, fill="both")

        self.student_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.student_tab, text="Students")
        self.create_student()

        self.instructor_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.instructor_tab, text="Instructors")
        self.create_instructor()

        self.course_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.course_tab, text="Courses")
        self.create_course()

        self.registration_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.registration_tab, text="Registrations")
        self.create_registration()

        self.display_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.display_tab, text="View All")
        self.create_display_all()

        clear_button = ttk.Button(self, text="Clear Database", command=self.clear_database)
        clear_button.pack(pady=10)

        self.update_button = None

    def make_database(self):
        """This method constructs the database that this application uses. It simply initializes each table for students, instructors, courses, registrations.
        """
        self.connection = sqlite3.connect("school_management.db")
        self.cursor = self.connection.cursor()

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER CHECK(age >= 0),
            email TEXT NOT NULL
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS instructors (
            instructor_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER CHECK(age >= 0),
            email TEXT NOT NULL
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            instructor_id TEXT,
            FOREIGN KEY (instructor_id) REFERENCES instructors (instructor_id)
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            student_id TEXT,
            course_id TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(course_id) REFERENCES courses(course_id)
        )
        ''')

        self.connection.commit()

    def input_student(self):
        """This method implements the ability of inputting the filled out data of a student in the text boxes into the database as long as they are correct. If the inputs are not valid, an error messagebox appears."""
        name = self.student_name.get()
        age = self.student_age.get()
        email = self.student_email.get()
        student_id = self.student_id.get()

        if not name or not age.isdigit() or not email or not student_id:
            messagebox.showerror("Error", "Please fill in all fields correctly.")
            return

        try:
            self.cursor.execute('''
                INSERT INTO students (student_id, name, age, email)
                VALUES (?, ?, ?, ?)
            ''', (student_id, name, int(age), email))
            self.connection.commit()
            messagebox.showinfo("Success", "Student added successfully!")
            self.clear_student_inputs()
            self.refresh_student_display()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Student ID already exists!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_student(self):
        """
        This method forms the structure of the student tab of the application, including the input textboxes, add button, search feature, table, edit/delete buttons
        """
        student_frame = ttk.Frame(self.student_tab)
        student_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(student_frame, text="Name").pack()
        self.student_name = tk.Entry(student_frame)
        self.student_name.pack(fill='x')

        tk.Label(student_frame, text="Age").pack()
        self.student_age = tk.Entry(student_frame)
        self.student_age.pack(fill='x')

        tk.Label(student_frame, text="Email").pack()
        self.student_email = tk.Entry(student_frame)
        self.student_email.pack(fill='x')

        tk.Label(student_frame, text="Student ID").pack()
        self.student_id = tk.Entry(student_frame)
        self.student_id.pack(fill='x')

        add_button = ttk.Button(student_frame, text="Add Student", command=self.input_student)
        add_button.pack(pady=5)

        search_button = ttk.Button(student_frame, text="Search", command=self.search_student)
        search_button.pack(pady=5)

        self.student_tree = ttk.Treeview(student_frame, columns=("ID", "Name", "Age", "Email"), show='headings')
        self.student_tree.pack(expand=True, fill='both')
        self.student_tree.heading("ID", text="Student ID")
        self.student_tree.heading("Name", text="Name")
        self.student_tree.heading("Age", text="Age")
        self.student_tree.heading("Email", text="Email")
        self.student_tree.bind("<Double-1>", self.on_student_double_click)
        self.refresh_student_display()

    def refresh_student_display(self):
        """
        This method makes sure that the table of students is refreshed and shows its current contents
        """
        for i in self.student_tree.get_children():
            self.student_tree.delete(i)

        self.cursor.execute("SELECT * FROM students")
        for row in self.cursor.fetchall():
            self.student_tree.insert("", "end", values=row)

    def on_student_double_click(self, event):
        """
        This method handles double-click events on student entries and loads the selected student's data into the input fields for editing.

        :param event: The event object containing information about the double-click.
        :type event: tk.Event
        """
        selected_item = self.student_tree.selection()[0]
        student_id = self.student_tree.item(selected_item, 'values')[0]
        self.edit_student(selected_item, student_id)

    def edit_student(self, selected_item, student_id):
        """
        This method loads student data into input fields for editing.

        :param selected_item: The selected item in the tree view.
        :type selected_item: str
        :param student_id: The ID of the student to edit.
        :type student_id: str
        """
        self.cursor.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
        student = self.cursor.fetchone()

        if student:
            self.student_id.delete(0, tk.END)
            self.student_name.delete(0, tk.END)
            self.student_age.delete(0, tk.END)
            self.student_email.delete(0, tk.END)

            self.student_id.insert(0, student[0])
            self.student_name.insert(0, student[1])
            self.student_age.insert(0, student[2])
            self.student_email.insert(0, student[3])

            if self.update_button:
                self.update_button.destroy()

            self.update_button = ttk.Button(self.student_tab, text="Update Student", command=lambda: self.update_student(student_id))
            self.update_button.pack(pady=5)

            delete_button = ttk.Button(self.student_tab, text="Delete Student", command=lambda: self.delete_student(self.student_id.get()))
            delete_button.pack(pady=5)

    def update_student(self, student_id):
        """This method takes the new inputs from the textboxes and edits the student record in the database.

        :param student_id: the ID of the student to update.
        :type student_id: str
        """
        name = self.student_name.get()
        age = self.student_age.get()
        email = self.student_email.get()

        if not name or not age.isdigit() or not email:
            messagebox.showerror("Error", "Please fill in all fields correctly.")
            return

        try:
            self.cursor.execute('''
                UPDATE students
                SET name=?, age=?, email=?
                WHERE student_id=?
            ''', (name, int(age), email, student_id))
            self.connection.commit()
            messagebox.showinfo("Success", "Student updated successfully!")
            self.clear_student_inputs()
            self.refresh_student_display()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_student(self):
        """This method allows for the search of the student from the database using the chosen inputs in the textboxes"""
        student_id_query = self.student_id.get()
        name_query = self.student_name.get()
        age_query = self.student_age.get()

        for i in self.student_tree.get_children():
            self.student_tree.delete(i)  

        query = "SELECT * FROM students WHERE 1=1"  
        params = []

        if student_id_query:
            query += " AND student_id LIKE ?"
            params.append(f"%{student_id_query}%")

        if name_query:
            query += " AND name LIKE ?"
            params.append(f"%{name_query}%")

        if age_query:
            query += " AND age LIKE ?"
            params.append(age_query)


        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            self.student_tree.insert("", "end", values=row)

    def clear_student_inputs(self):
        """This method erases the inputs in the textboxes of the student fields"""
        self.student_name.delete(0, tk.END)
        self.student_age.delete(0, tk.END)
        self.student_email.delete(0, tk.END)
        self.student_id.delete(0, tk.END)

    def delete_student(self, student_id):
        """This method deletes the student chosen using the student_id from the database. Shows a success or error message accordingly.
        
        :param student_id: the ID of the student to delete
        :type student_id: str
        """
        try:
            self.cursor.execute("DELETE FROM students WHERE student_id=?", (student_id,))
            self.connection.commit()
            messagebox.showinfo("Success", "Student deleted successfully!")
            self.refresh_student_display()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def input_instructor(self):
        """This method implements the ability of inputting the filled out data of an instructor in the text boxes into the database as long as they are correct. 
        If the inputs are not valid, an error messagebox appears. 
        """
        name = self.instructor_name.get()
        age = self.instructor_age.get()
        email = self.instructor_email.get()
        instructor_id = self.instructor_id.get()

        if not name or not age.isdigit() or not email or not instructor_id:
            messagebox.showerror("Error", "Please fill in all fields correctly.")
            return

        try:
            self.cursor.execute('''
                INSERT INTO instructors (instructor_id, name, age, email)
                VALUES (?, ?, ?, ?)
            ''', (instructor_id, name, int(age), email))
            self.connection.commit()
            messagebox.showinfo("Success", "Instructor added successfully!")
            self.clear_instructor_inputs()
            self.refresh_instructor_display()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Instructor ID already exists!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_instructor(self):
        """
        This method forms the structure UI of the instructor tab of the application, including the input textboxes, add button, search feature, table (treeview), double click feature
        """
        instructor_frame = ttk.Frame(self.instructor_tab)
        instructor_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(instructor_frame, text="Name").pack()
        self.instructor_name = tk.Entry(instructor_frame)
        self.instructor_name.pack(fill='x')

        tk.Label(instructor_frame, text="Age").pack()
        self.instructor_age = tk.Entry(instructor_frame)
        self.instructor_age.pack(fill='x')

        tk.Label(instructor_frame, text="Email").pack()
        self.instructor_email = tk.Entry(instructor_frame)
        self.instructor_email.pack(fill='x')

        tk.Label(instructor_frame, text="Instructor ID").pack()
        self.instructor_id = tk.Entry(instructor_frame)
        self.instructor_id.pack(fill='x')

        add_button = ttk.Button(instructor_frame, text="Add Instructor", command=self.input_instructor)
        add_button.pack(pady=5)

        search_button = ttk.Button(instructor_frame, text="Search", command=self.search_instructor)
        search_button.pack(pady=5)

        self.instructor_tree = ttk.Treeview(instructor_frame, columns=("ID", "Name", "Age", "Email"), show='headings')
        self.instructor_tree.pack(expand=True, fill='both')
        self.instructor_tree.heading("ID", text="Instructor ID")
        self.instructor_tree.heading("Name", text="Name")
        self.instructor_tree.heading("Age", text="Age")
        self.instructor_tree.heading("Email", text="Email")
        self.instructor_tree.bind("<Double-1>", self.on_instructor_double_click)
        self.refresh_instructor_display()

    def refresh_instructor_display(self):
        """
        This method makes sure that the table of instructors is refreshed and shows its current contents
        """
        for i in self.instructor_tree.get_children():
            self.instructor_tree.delete(i)

        self.cursor.execute("SELECT * FROM instructors")
        for row in self.cursor.fetchall():
            self.instructor_tree.insert("", "end", values=row)

    def delete_instructor(self, instructor_id):
        """This method deletes the instructor chosen using the instructor_id from the database. Shows a success or error message accordingly.
        
        :param instructor_id: the ID of the student to delete
        :type instructor_id: str
        """
        try:
            self.cursor.execute("DELETE FROM instructors WHERE instructor_id=?", (instructor_id,))
            self.connection.commit()
            messagebox.showinfo("Success", "Instructor deleted successfully!")
            self.refresh_instructor_display()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_instructor_double_click(self, event):
        """
        This method handles double-click events on instructor entries and loads the selected instructor's data into the input fields for editing.

        :param event: The event object containing information about the double-click.
        :type event: tk.Event
        """
        selected_item = self.instructor_tree.selection()[0]
        instructor_id = self.instructor_tree.item(selected_item, 'values')[0]
        self.edit_instructor(selected_item, instructor_id)


    def edit_instructor(self, selected_item, instructor_id):
        """
        This method loads instructor data into input fields for editing.

        :param selected_item: The selected item in the tree view.
        :type selected_item: str
        :param instructor_id: The ID of the instructor to edit.
        :type instructor_id: str
        """
        self.cursor.execute("SELECT * FROM instructors WHERE instructor_id=?", (instructor_id,))
        instructor = self.cursor.fetchone()

        if instructor:
            self.instructor_id.delete(0, tk.END)
            self.instructor_name.delete(0, tk.END)
            self.instructor_age.delete(0, tk.END)
            self.instructor_email.delete(0, tk.END)

            self.instructor_id.insert(0, instructor[0])
            self.instructor_name.insert(0, instructor[1])
            self.instructor_age.insert(0, instructor[2])
            self.instructor_email.insert(0, instructor[3])

            if self.update_button:
                self.update_button.destroy()

            self.update_button = ttk.Button(self.instructor_tab, text="Update Instructor", command=lambda: self.update_instructor(instructor_id))
            self.update_button.pack(pady=5)

            delete_button = ttk.Button(self.instructor_tab, text="Delete Instructor", command=lambda: self.delete_instructor(self.instructor_id.get()))
            delete_button.pack(pady=5)


    def update_instructor(self, instructor_id):
        """This method takes the new inputs from the textboxes and edits the instructor record in the database.

        :param instructor_id: the ID of the instructor to update.
        :type instructor_id: str
        """
        name = self.instructor_name.get()
        age = self.instructor_age.get()
        email = self.instructor_email.get()

        if not name or not age.isdigit() or not email:
            messagebox.showerror("Error", "Please fill in all fields correctly.")
            return

        try:
            self.cursor.execute('''
                UPDATE instructors
                SET name=?, age=?, email=?
                WHERE instructor_id=?
            ''', (name, int(age), email, instructor_id))
            self.connection.commit()
            messagebox.showinfo("Success", "Instructor updated successfully!")
            self.clear_instructor_inputs()
            self.refresh_instructor_display()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_instructor(self):
        """This method allows for the selection of the instructor from the database using the chosen inputs in the textboxes."""
        instructor_id_query = self.instructor_id.get()
        name_query = self.instructor_name.get()
        age_query = self.instructor_age.get()

        for i in self.instructor_tree.get_children():
            self.instructor_tree.delete(i) 


        query = "SELECT * FROM instructors WHERE 1=1"  
        params = []

        if instructor_id_query:
            query += " AND instructor_id LIKE ?"
            params.append(f"%{instructor_id_query}%")

        if name_query:
            query += " AND name LIKE ?"
            params.append(f"%{name_query}%")

        if age_query:
            query += " AND age LIKE ?"
            params.append(age_query)
        self.cursor.execute(query, params)
        

        for row in self.cursor.fetchall():
            self.instructor_tree.insert("", "end", values=row)

    def clear_instructor_inputs(self):
        """This method erases the inputs in the textboxes of the instructor fields"""
        self.instructor_name.delete(0, tk.END)
        self.instructor_age.delete(0, tk.END)
        self.instructor_email.delete(0, tk.END)
        self.instructor_id.delete(0, tk.END)


    def input_course(self):
        """This method implements the ability of inputting the filled out data of a course in the text boxes into the database as long as they are correct. 
        If the inputs are not valid, an error messagebox appears. 
        """
        course_name = self.course_name.get()
        course_id = self.course_id.get()
        instructor_id = self.course_instructor_id.get()

        if not course_name or not course_id or not instructor_id:
            messagebox.showerror("Error", "Please fill in all fields correctly.")
            return

        try:
            self.cursor.execute('''
                INSERT INTO courses (course_id, course_name, instructor_id)
                VALUES (?, ?, ?)
            ''', (course_id, course_name, instructor_id))
            self.connection.commit()
            messagebox.showinfo("Success", "Course added successfully!")
            self.clear_course_inputs()
            self.refresh_course_display()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Course ID already exists!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_course(self):
        """
        This method forms the structure UI of the course tab of the application, including the input textboxes, add button, search feature, table, double click feature
        """
        course_frame = ttk.Frame(self.course_tab)
        course_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(course_frame, text="Course Name").pack()
        self.course_name = tk.Entry(course_frame)
        self.course_name.pack(fill='x')

        tk.Label(course_frame, text="Course ID").pack()
        self.course_id = tk.Entry(course_frame)
        self.course_id.pack(fill='x')

        tk.Label(course_frame, text="Instructor ID").pack()
        self.course_instructor_id = tk.Entry(course_frame)
        self.course_instructor_id.pack(fill='x')

        add_button = ttk.Button(course_frame, text="Add Course", command=self.input_course)
        add_button.pack(pady=5)

        search_button = ttk.Button(course_frame, text="Search", command=self.search_course)
        search_button.pack(pady=5)

        self.course_tree = ttk.Treeview(course_frame, columns=("ID", "Course Name", "Instructor ID"), show='headings')
        self.course_tree.pack(expand=True, fill='both')
        self.course_tree.heading("ID", text="Course ID")
        self.course_tree.heading("Course Name", text="Course Name")
        self.course_tree.heading("Instructor ID", text="Instructor ID")
        self.course_tree.bind("<Double-1>", self.on_course_double_click)
        self.refresh_course_display()

    def refresh_course_display(self):
        """
        This method makes sure that the table of courses is refreshed and shows its current contents
        """
        for i in self.course_tree.get_children():
            self.course_tree.delete(i)

        self.cursor.execute("SELECT * FROM courses")
        for row in self.cursor.fetchall():
            self.course_tree.insert("", "end", values=row)

    def delete_course(self, course_id):
        """This method deletes the course chosen using the course_id from the database. Shows a success or error message accordingly.
        
        :param course_id: the ID of the student to delete
        :type course_id: str
        """
        try:
            self.cursor.execute("DELETE FROM courses WHERE course_id=?", (course_id,))
            self.connection.commit()
            messagebox.showinfo("Success", "Course deleted successfully!")
            self.refresh_course_display()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_course_double_click(self, event):
        """
        This method handles double-click events on course entries and loads the selected course's data into the input fields for editing.

        :param event: The event object containing information about the double-click.
        :type event: tk.Event
        """
        selected_item = self.course_tree.selection()[0]
        course_id = self.course_tree.item(selected_item, 'values')[0]
        self.edit_course(selected_item, course_id)

    def edit_course(self, selected_item, course_id):
        """
        This method loads course data into input fields for editing.

        :param selected_item: The selected item in the tree view.
        :type selected_item: str
        :param course_id: The ID of the course to edit.
        :type course_id: str
        """
        self.cursor.execute("SELECT * FROM courses WHERE course_id=?", (course_id,))
        course = self.cursor.fetchone()

        if course:
            self.course_id.delete(0, tk.END)
            self.course_name.delete(0, tk.END)
            self.course_instructor_id.delete(0, tk.END)

            self.course_id.insert(0, course[0])
            self.course_name.insert(0, course[1])
            self.course_instructor_id.insert(0, course[2])

            if self.update_button:
                self.update_button.destroy()

            self.update_button = ttk.Button(self.course_tab, text="Update Course", command=lambda: self.update_course(course_id))
            self.update_button.pack(pady=5)

            delete_button = ttk.Button(self.course_tab, text="Delete Course", command=lambda: self.delete_course(self.course_id.get()))
            delete_button.pack(pady=5)

    def update_course(self, course_id):
        """This method takes the new inputs from the textboxes and edits the course record in the database.

        :param course_id: the ID of the course to update.
        :type course_id: str
        """
        course_name = self.course_name.get()
        instructor_id = self.course_instructor_id.get()

        if not course_name or not instructor_id:
            messagebox.showerror("Error", "Please fill in all fields correctly.")
            return

        try:
            self.cursor.execute('''
                UPDATE courses
                SET course_name=?, instructor_id=?
                WHERE course_id=?
            ''', (course_name, instructor_id, course_id))
            self.connection.commit()
            messagebox.showinfo("Success", "Course updated successfully!")
            self.clear_course_inputs()
            self.refresh_course_display()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_course(self):
        """This method allows for the selection of the course from the database using the chosen inputs in the textboxes"""
        course_id_query = self.course_id.get()
        course_name_query = self.course_name.get()

        for i in self.course_tree.get_children():
            self.course_tree.delete(i)  

        query = "SELECT * FROM courses WHERE 1=1"  
        params = []

        if course_id_query:
            query += " AND course_id LIKE ?"
            params.append(f"%{course_id_query}%")

        if course_name_query:
            query += " AND course_name LIKE ?"
            params.append(f"%{course_name_query}%")

        self.cursor.execute(query, params)
        
        for row in self.cursor.fetchall():
            self.course_tree.insert("", "end", values=row)

    def clear_course_inputs(self):
        """This method erases the inputs in the textboxes of the course fields"""
        self.course_name.delete(0, tk.END)
        self.course_id.delete(0, tk.END)
        self.course_instructor_id.delete(0, tk.END)

    def create_registration(self):
        """This method creates the registration interface for students to register a course using dropdowns of student_id and course_id"""
        tk.Label(self.registration_tab, text="Student ID").pack(pady=5)
        self.registration_student_id = ttk.Combobox(self.registration_tab)
        self.registration_student_id.pack(pady=5)

        tk.Label(self.registration_tab, text="Course ID").pack(pady=5)
        self.registration_course_id = ttk.Combobox(self.registration_tab)
        self.registration_course_id.pack(pady=5)

        register_button = tk.Button(self.registration_tab, text="Register", command=self.register_student)
        register_button.pack(pady=10)

        self.populate_comboboxes()  

    def populate_comboboxes(self):
        """
        This method populates the comboboxes for selecting student ID and course ID from the database.
        """
        self.registration_student_id['values'] = [student[0] for student in self.cursor.execute("SELECT student_id FROM students").fetchall()]
        self.registration_course_id['values'] = [course[0] for course in self.cursor.execute("SELECT course_id FROM courses").fetchall()]

    def register_student(self):
        """This method lets student register to a course according to the dropdown inputs. A messagebox shows whether the registration worked or an error occured."""
        student_id = self.registration_student_id.get()
        course_id = self.registration_course_id.get()

        if not student_id or not course_id:
            messagebox.showerror("Error", "Please select both Student ID and Course ID.")
            return

        try:
            self.cursor.execute('''INSERT INTO registrations (student_id, course_id) VALUES (?, ?)''', (student_id, course_id))
            self.connection.commit()
            messagebox.showinfo("Success", "Course registered successfully!")
            self.clear_registration_inputs()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_registration_inputs(self):
        """This method clears the dropdown inputs for the course registration."""
        self.registration_student_id.set('')
        self.registration_course_id.set('')

    def create_display_all(self):
        """
        This method creates a display interface to show all records from students, instructors, and courses.
        """
        display_frame = ttk.Frame(self.display_tab)
        display_frame.pack(pady=10, padx=10, fill='both', expand=True)

        control_frame = ttk.Frame(display_frame)
        control_frame.pack(fill='x', padx=5, pady=5)

        self.clear_button = ttk.Button(control_frame, text="Clear Database", command=self.clear_database)
        self.clear_button.pack(side='right', padx=5)

        self.display_tree = ttk.Treeview(display_frame, columns=("Type", "ID", "Name", "Age", "Email"), show='headings')
        self.display_tree.pack(expand=True, fill='both', padx=5, pady=5)
        self.display_tree.heading("Type", text="Type")
        self.display_tree.heading("ID", text="ID")
        self.display_tree.heading("Name", text="Name")
        self.display_tree.heading("Age", text="Age")
        self.display_tree.heading("Email", text="Email")


        self.display_button = ttk.Button(display_frame, text="Display All", command=self.display_all)
        self.display_button.pack(pady=5)
        self.display_button = ttk.Button(display_frame, text="Export to CSV", command=self.export)
        self.display_button.pack(pady=5)

    def display_all(self):
        """This method displays all the records in the database tree view"""
        for i in self.display_tree.get_children():
            self.display_tree.delete(i) 

        self.cursor.execute("SELECT 'Student' AS Type, student_id, name, age, email FROM students")
        students = self.cursor.fetchall()

        for row in students:
            self.display_tree.insert("", "end", values=row)

        self.cursor.execute("SELECT 'Instructor' AS Type, instructor_id, name, age, email FROM instructors")
        instructors = self.cursor.fetchall()

        for row in instructors:
            self.display_tree.insert("", "end", values=row)

        self.cursor.execute("SELECT 'Course' AS Type, course_id, course_name, NULL AS age, NULL AS email FROM courses")
        courses = self.cursor.fetchall()

        for row in courses:
            self.display_tree.insert("", "end", values=row)

    def export(self):
        """This method allows for the export of the database to a .csv file. A messagebox shows whether this was successful or not"""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not file_path:
            return  

        try:
            with open(file_path, mode='w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["Type", "ID", "Name", "Age", "Email"])
                self.cursor.execute("SELECT 'Student', student_id, name, age, email FROM students")
                csv_writer.writerows(self.cursor.fetchall())
                self.cursor.execute("SELECT 'Instructor', instructor_id, name, age, email FROM instructors")
                csv_writer.writerows(self.cursor.fetchall())
                self.cursor.execute("SELECT 'Course', course_id, course_name, NULL AS age, NULL AS email FROM courses")
                csv_writer.writerows(self.cursor.fetchall())

            messagebox.showinfo("Success", "Data exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_database(self):
        """
        This method clears all tables from the database after user confirmation.
        """
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the database?"):
            self.cursor.execute("DROP TABLE IF EXISTS registrations")
            self.cursor.execute("DROP TABLE IF EXISTS courses")
            self.cursor.execute("DROP TABLE IF EXISTS instructors")
            self.cursor.execute("DROP TABLE IF EXISTS students")
            self.connection.commit()
            messagebox.showinfo("Success", "Database cleared!")

    def on_closing(self):
        """
        This handles the cleanup when the application is closed, including closing the database connection.
        """
        self.connection.close()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()