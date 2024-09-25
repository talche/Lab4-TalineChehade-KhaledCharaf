import sys
import json
import re
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QGridLayout, QMenuBar,
    QMenu, QAction, QMessageBox, QStackedWidget, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from SchoolStructs import *  # Assuming this is a custom module containing validation functions

# Database initialization and operations
class Database:
    """
    Handles the database operations for the School Management System.
    """
    def __init__(self, db_name='school.db'):
        """
        Initializes the Database object and creates tables if they don't exist.

        Args:
            db_name (str): The name of the database file.
        """
        # Connect to the SQLite database (or create it if it doesn't exist)
        self.connection = sqlite3.connect(db_name)
        # Create the necessary tables
        self.create_tables()

    def create_tables(self):
        """
        Creates the necessary tables in the database if they do not already exist.
        """
        # Create a cursor object to execute SQL commands
        cursor = self.connection.cursor()

        # Create Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT UNIQUE NOT NULL,
                student_id TEXT UNIQUE NOT NULL
            )
        ''')

        # Create Instructors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Instructors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT UNIQUE NOT NULL,
                instructor_id TEXT UNIQUE NOT NULL
            )
        ''')

        # Create Courses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id TEXT UNIQUE NOT NULL,
                course_name TEXT NOT NULL,
                instructor_id INTEGER,
                FOREIGN KEY (instructor_id) REFERENCES Instructors(id)
            )
        ''')

        # Create Registrations table (for many-to-many relationship between Students and Courses)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY (student_id) REFERENCES Students(id),
                FOREIGN KEY (course_id) REFERENCES Courses(id),
                UNIQUE(student_id, course_id)
            )
        ''')

        # Commit the changes to the database
        self.connection.commit()

    def close(self):
        """
        Closes the database connection.
        """
        self.connection.close()

# Validation functions (assumed to be in SchoolStructs.py)
# You might have functions like validate_email, validate_age, etc.

# Data models
class Person:
    """
    Base class for Student and Instructor, representing a person.
    """
    def __init__(self, name: str, age: int, email: str):
        """
        Initializes a Person object with validation.

        Args:
            name (str): The name of the person.
            age (int): The age of the person.
            email (str): The email address of the person.
        """
        # Validate email format
        if not validate_email(email):
            raise ValueError("Invalid email format.")
        # Validate age (must be non-negative integer)
        if not validate_age(age):
            raise ValueError("Age must be a non-negative integer.")
        # Assign attributes
        self.name = name
        self.age = age
        self.email = email

class Student(Person):
    """
    Represents a student, inheriting from Person.
    """
    def __init__(self, name: str, age: int, email: str, student_id: str):
        """
        Initializes a Student object.

        Args:
            name (str): The name of the student.
            age (int): The age of the student.
            email (str): The email address of the student.
            student_id (str): The unique student ID.
        """
        # Initialize the base class
        super().__init__(name, age, email)
        # Assign the student ID
        self.student_id = student_id

class Instructor(Person):
    """
    Represents an instructor, inheriting from Person.
    """
    def __init__(self, name: str, age: int, email: str, instructor_id: str):
        """
        Initializes an Instructor object.

        Args:
            name (str): The name of the instructor.
            age (int): The age of the instructor.
            email (str): The email address of the instructor.
            instructor_id (str): The unique instructor ID.
        """
        # Initialize the base class
        super().__init__(name, age, email)
        # Assign the instructor ID
        self.instructor_id = instructor_id

class Course:
    """
    Represents a course.
    """
    def __init__(self, course_id: str, course_name: str, instructor_id=None):
        """
        Initializes a Course object.

        Args:
            course_id (str): The unique course ID.
            course_name (str): The name of the course.
            instructor_id (int, optional): The ID of the instructor teaching the course.
        """
        self.course_id = course_id
        self.course_name = course_name
        self.instructor_id = instructor_id

# Main application window
class MainWindow(QMainWindow):
    """
    The main window of the School Management System application.
    """
    def __init__(self):
        """
        Initializes the main window and sets up the UI components.
        """
        super().__init__()
        # Set window title and geometry
        self.setWindowTitle("School Management System")
        self.setGeometry(100, 100, 1000, 800)

        # Initialize the database
        self.db = Database()

        # Create a central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout for the central widget
        self.layout = QVBoxLayout(self.central_widget)

        # Create a stacked widget to switch between different pages
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Create instances of each page
        self.home_page = HomePage(self)
        self.student_page = StudentPage(self)
        self.instructor_page = InstructorPage(self)
        self.course_page = CoursePage(self)

        # Add pages to the stacked widget
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.student_page)
        self.stacked_widget.addWidget(self.instructor_page)
        self.stacked_widget.addWidget(self.course_page)

        # Set up the menu bar
        self.setup_menu_bar()

        # Start by showing the home page
        self.stacked_widget.setCurrentWidget(self.home_page)

    def setup_menu_bar(self):
        """
        Sets up the menu bar with navigation options.
        """
        # Create the menu bar
        menu_bar = self.menuBar()

        # Home menu
        home_menu = menu_bar.addMenu("Home")
        home_action = QAction("Home", self)
        # Connect the action to show the home page
        home_action.triggered.connect(lambda: self.show_page(self.home_page))
        home_menu.addAction(home_action)

        # Students menu
        student_menu = menu_bar.addMenu("Students")
        student_action = QAction("Students", self)
        # Connect the action to show the student page
        student_action.triggered.connect(lambda: self.show_page(self.student_page))
        student_menu.addAction(student_action)

        # Instructors menu
        instructor_menu = menu_bar.addMenu("Instructors")
        instructor_action = QAction("Instructors", self)
        # Connect the action to show the instructor page
        instructor_action.triggered.connect(lambda: self.show_page(self.instructor_page))
        instructor_menu.addAction(instructor_action)

        # Courses menu
        course_menu = menu_bar.addMenu("Courses")
        course_action = QAction("Courses", self)
        # Connect the action to show the course page
        course_action.triggered.connect(lambda: self.show_page(self.course_page))
        course_menu.addAction(course_action)

        # Backup menu
        backup_menu = menu_bar.addMenu("Backup")
        backup_action = QAction("Backup Database", self)
        # Connect the action to backup the database
        backup_action.triggered.connect(self.backup_database)
        backup_menu.addAction(backup_action)

    def show_page(self, page):
        """
        Switches the displayed page in the stacked widget.

        Args:
            page (QWidget): The page to display.
        """
        self.stacked_widget.setCurrentWidget(page)

    def backup_database(self):
        """
        Backs up the database to a file chosen by the user.
        """
        # Open a file dialog for the user to choose the backup file location
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Backup Database", "",
            "SQLite Database Files (*.db);;All Files (*)", options=options
        )
        if fileName:
            try:
                # Copy the database file to the chosen location
                source_db = self.db.connection
                dest_db = sqlite3.connect(fileName)
                with dest_db:
                    source_db.backup(dest_db)
                dest_db.close()
                QMessageBox.information(self, "Backup Successful", "Database backup completed successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Backup Failed", f"An error occurred: {str(e)}")

    def closeEvent(self, event):
        """
        Handles the window close event to ensure the database connection is closed.

        Args:
            event (QCloseEvent): The close event.
        """
        # Close the database connection before exiting
        self.db.close()
        event.accept()

# Home Page
class HomePage(QWidget):
    """
    Represents the home page of the application.
    """
    def __init__(self, parent):
        """
        Initializes the home page.

        Args:
            parent (QMainWindow): Reference to the main window.
        """
        super().__init__()
        self.parent = parent  # Reference to the main window
        self.init_ui()

    def init_ui(self):
        """
        Sets up the UI components for the home page.
        """
        # Create a vertical layout
        layout = QVBoxLayout(self)

        # Create and set the main label
        home_label = QLabel("School Management System", self)
        home_label.setFont(QtGui.QFont("Arial", 20))
        layout.addWidget(home_label)

# Student Page
class StudentPage(QWidget):
    """
    Represents the student management page.
    """
    def __init__(self, parent):
        """
        Initializes the student page.

        Args:
            parent (QMainWindow): Reference to the main window.
        """
        super().__init__()
        self.parent = parent  # Reference to the main window
        self.init_ui()

    def init_ui(self):
        """
        Sets up the UI components for the student page.
        """
        # Create a vertical layout
        layout = QVBoxLayout(self)

        # Create and add the title label
        student_label = QLabel("Add a Student", self)
        student_label.setFont(QtGui.QFont("Arial", 20))
        layout.addWidget(student_label)

        # Create a grid layout for the input fields
        form_layout = QGridLayout()

        # Student Name
        student_name_label = QLabel("Student Name:")
        self.student_name_entry = QLineEdit()
        form_layout.addWidget(student_name_label, 0, 0)
        form_layout.addWidget(self.student_name_entry, 0, 1)

        # Student Age
        student_age_label = QLabel("Student Age:")
        self.student_age_entry = QLineEdit()
        form_layout.addWidget(student_age_label, 1, 0)
        form_layout.addWidget(self.student_age_entry, 1, 1)

        # Student Email
        student_email_label = QLabel("Student Email:")
        self.student_email_entry = QLineEdit()
        form_layout.addWidget(student_email_label, 2, 0)
        form_layout.addWidget(self.student_email_entry, 2, 1)

        # Student ID
        student_id_label = QLabel("Student ID:")
        self.student_id_entry = QLineEdit()
        form_layout.addWidget(student_id_label, 3, 0)
        form_layout.addWidget(self.student_id_entry, 3, 1)

        # Add the form layout to the main layout
        layout.addLayout(form_layout)

        # Add Student Button
        self.add_student_button = QPushButton("Add Student")
        self.add_student_button.clicked.connect(self.add_student)
        layout.addWidget(self.add_student_button)

        # Student Table
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(4)
        self.student_table.setHorizontalHeaderLabels(["Name", "Age", "Email", "ID"])
        layout.addWidget(self.student_table)

        # Search bar and buttons
        search_layout = QHBoxLayout()
        student_search_label = QLabel("Search Students by Name or ID:")
        self.student_search_entry = QLineEdit()
        self.search_student_button = QPushButton("Search")
        self.search_student_button.clicked.connect(self.search_student_table)
        self.delete_student_button = QPushButton("Delete")
        self.delete_student_button.clicked.connect(self.delete_student_record)
        search_layout.addWidget(student_search_label)
        search_layout.addWidget(self.student_search_entry)
        search_layout.addWidget(self.search_student_button)
        search_layout.addWidget(self.delete_student_button)
        layout.addLayout(search_layout)

        # Load initial data into the table
        self.load_students()

    def add_student(self):
        """
        Adds a new student to the database and updates the table.
        """
        # Get input values
        student_name = self.student_name_entry.text()
        try:
            student_age = int(self.student_age_entry.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Age must be an integer.")
            return
        student_email = self.student_email_entry.text()
        student_id = self.student_id_entry.text()

        # Validation
        if not student_name or not student_email or not student_id:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields.")
            return

        try:
            # Create a Student object
            student = Student(student_name, student_age, student_email, student_id)
            # Insert into the database
            cursor = self.parent.db.connection.cursor()
            cursor.execute('''
                INSERT INTO Students (name, age, email, student_id)
                VALUES (?, ?, ?, ?)
            ''', (student.name, student.age, student.email, student.student_id))
            self.parent.db.connection.commit()
            QMessageBox.information(self, "Success", f"Student {student.name} added.")
            # Refresh the student table
            self.load_students()
            # Clear input fields
            self.student_name_entry.clear()
            self.student_age_entry.clear()
            self.student_email_entry.clear()
            self.student_id_entry.clear()
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def load_students(self):
        """
        Loads student data from the database into the table.
        """
        cursor = self.parent.db.connection.cursor()
        cursor.execute('SELECT name, age, email, student_id FROM Students')
        students = cursor.fetchall()
        self.student_table.setRowCount(0)
        for row_data in students:
            row_number = self.student_table.rowCount()
            self.student_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.student_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def search_student_table(self):
        """
        Searches for students based on the query and updates the table.
        """
        query = self.student_search_entry.text().lower()
        cursor = self.parent.db.connection.cursor()
        cursor.execute('''
            SELECT name, age, email, student_id FROM Students
            WHERE LOWER(name) LIKE ? OR LOWER(student_id) LIKE ?
        ''', ('%' + query + '%', '%' + query + '%'))
        students = cursor.fetchall()
        self.student_table.setRowCount(0)
        for row_data in students:
            row_number = self.student_table.rowCount()
            self.student_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.student_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def delete_student_record(self):
        """
        Deletes the selected student record from the database.
        """
        selected_items = self.student_table.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            email_item = self.student_table.item(selected_row, 2)
            email = email_item.text()
            cursor = self.parent.db.connection.cursor()
            try:
                cursor.execute('DELETE FROM Students WHERE email = ?', (email,))
                self.parent.db.connection.commit()
                QMessageBox.information(self, "Success", "Student record deleted.")
                self.load_students()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

# Instructor Page
class InstructorPage(QWidget):
    """
    Represents the instructor management page.
    """
    def __init__(self, parent):
        """
        Initializes the instructor page.

        Args:
            parent (QMainWindow): Reference to the main window.
        """
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        """
        Sets up the UI components for the instructor page.
        """
        # Create a vertical layout
        layout = QVBoxLayout(self)

        # Title label
        instructor_label = QLabel("Add an Instructor", self)
        instructor_label.setFont(QtGui.QFont("Arial", 20))
        layout.addWidget(instructor_label)

        # Form layout for input fields
        form_layout = QGridLayout()

        # Instructor Name
        instructor_name_label = QLabel("Instructor Name:")
        self.instructor_name_entry = QLineEdit()
        form_layout.addWidget(instructor_name_label, 0, 0)
        form_layout.addWidget(self.instructor_name_entry, 0, 1)

        # Instructor Age
        instructor_age_label = QLabel("Instructor Age:")
        self.instructor_age_entry = QLineEdit()
        form_layout.addWidget(instructor_age_label, 1, 0)
        form_layout.addWidget(self.instructor_age_entry, 1, 1)

        # Instructor Email
        instructor_email_label = QLabel("Instructor Email:")
        self.instructor_email_entry = QLineEdit()
        form_layout.addWidget(instructor_email_label, 2, 0)
        form_layout.addWidget(self.instructor_email_entry, 2, 1)

        # Instructor ID
        instructor_id_label = QLabel("Instructor ID:")
        self.instructor_id_entry = QLineEdit()
        form_layout.addWidget(instructor_id_label, 3, 0)
        form_layout.addWidget(self.instructor_id_entry, 3, 1)

        # Add form layout to main layout
        layout.addLayout(form_layout)

        # Add Instructor Button
        self.add_instructor_button = QPushButton("Add Instructor")
        self.add_instructor_button.clicked.connect(self.add_instructor)
        layout.addWidget(self.add_instructor_button)

        # Instructor Table
        self.instructor_table = QTableWidget()
        self.instructor_table.setColumnCount(4)
        self.instructor_table.setHorizontalHeaderLabels(["Name", "Age", "Email", "ID"])
        layout.addWidget(self.instructor_table)

        # Assign Instructor to Course section
        assign_layout = QGridLayout()
        assign_label = QLabel("Assign Instructor to Course", self)
        assign_label.setFont(QtGui.QFont("Arial", 16))
        layout.addWidget(assign_label)

        # Course Dropdown
        course_dropdown_label = QLabel("Select Course:")
        self.course_dropdown = QComboBox()
        self.update_course_dropdown()
        assign_layout.addWidget(course_dropdown_label, 0, 0)
        assign_layout.addWidget(self.course_dropdown, 0, 1)

        # Instructor Email for Assignment
        instructor_email_label2 = QLabel("Instructor Email:")
        self.instructor_email_entry2 = QLineEdit()
        assign_layout.addWidget(instructor_email_label2, 1, 0)
        assign_layout.addWidget(self.instructor_email_entry2, 1, 1)

        # Assign Instructor Button
        self.assign_instructor_button = QPushButton("Assign Instructor to Course")
        self.assign_instructor_button.clicked.connect(self.assign_instructor_to_course)
        assign_layout.addWidget(self.assign_instructor_button, 2, 0, 1, 2)

        # Add assignment layout to main layout
        layout.addLayout(assign_layout)

        # Search bar and buttons
        search_layout = QHBoxLayout()
        instructor_search_label = QLabel("Search Instructors by Name or ID:")
        self.instructor_search_entry = QLineEdit()
        self.search_instructor_button = QPushButton("Search")
        self.search_instructor_button.clicked.connect(self.search_instructor_table)
        self.delete_instructor_button = QPushButton("Delete")
        self.delete_instructor_button.clicked.connect(self.delete_instructor_record)
        search_layout.addWidget(instructor_search_label)
        search_layout.addWidget(self.instructor_search_entry)
        search_layout.addWidget(self.search_instructor_button)
        search_layout.addWidget(self.delete_instructor_button)
        layout.addLayout(search_layout)

        # Load initial data into the table
        self.load_instructors()

    def add_instructor(self):
        """
        Adds a new instructor to the database and updates the table.
        """
        # Get input values
        instructor_name = self.instructor_name_entry.text()
        try:
            instructor_age = int(self.instructor_age_entry.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Age must be an integer.")
            return
        instructor_email = self.instructor_email_entry.text()
        instructor_id = self.instructor_id_entry.text()

        # Validation
        if not instructor_name or not instructor_email or not instructor_id:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields.")
            return

        try:
            # Create an Instructor object
            instructor = Instructor(instructor_name, instructor_age, instructor_email, instructor_id)
            # Insert into the database
            cursor = self.parent.db.connection.cursor()
            cursor.execute('''
                INSERT INTO Instructors (name, age, email, instructor_id)
                VALUES (?, ?, ?, ?)
            ''', (instructor.name, instructor.age, instructor.email, instructor.instructor_id))
            self.parent.db.connection.commit()
            QMessageBox.information(self, "Success", f"Instructor {instructor.name} added.")
            # Refresh the instructor table
            self.load_instructors()
            # Clear input fields
            self.instructor_name_entry.clear()
            self.instructor_age_entry.clear()
            self.instructor_email_entry.clear()
            self.instructor_id_entry.clear()
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def load_instructors(self):
        """
        Loads instructor data from the database into the table.
        """
        cursor = self.parent.db.connection.cursor()
        cursor.execute('SELECT name, age, email, instructor_id FROM Instructors')
        instructors = cursor.fetchall()
        self.instructor_table.setRowCount(0)
        for row_data in instructors:
            row_number = self.instructor_table.rowCount()
            self.instructor_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.instructor_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def update_course_dropdown(self):
        """
        Updates the course dropdown with the latest courses.
        """
        cursor = self.parent.db.connection.cursor()
        cursor.execute('SELECT course_name FROM Courses')
        courses = cursor.fetchall()
        course_names = [course[0] for course in courses]
        self.course_dropdown.clear()
        self.course_dropdown.addItems(course_names)

    def assign_instructor_to_course(self):
        """
        Assigns an instructor to a selected course.
        """
        # Get input values
        instructor_email = self.instructor_email_entry2.text()
        course_name = self.course_dropdown.currentText()

        cursor = self.parent.db.connection.cursor()
        # Get instructor ID based on email
        cursor.execute('SELECT id FROM Instructors WHERE email = ?', (instructor_email,))
        instructor = cursor.fetchone()

        if instructor is None:
            QMessageBox.warning(self, "Error", "Instructor not found.")
            return

        instructor_id = instructor[0]

        # Get course ID based on course name
        cursor.execute('SELECT id FROM Courses WHERE course_name = ?', (course_name,))
        course = cursor.fetchone()

        if course is None:
            QMessageBox.warning(self, "Error", "Course not found.")
            return

        course_id = course[0]

        try:
            # Update the course to set the instructor ID
            cursor.execute('UPDATE Courses SET instructor_id = ? WHERE id = ?', (instructor_id, course_id))
            self.parent.db.connection.commit()
            QMessageBox.information(self, "Success", "Instructor assigned to course.")
            self.instructor_email_entry2.clear()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def search_instructor_table(self):
        """
        Searches for instructors based on the query and updates the table.
        """
        query = self.instructor_search_entry.text().lower()
        cursor = self.parent.db.connection.cursor()
        cursor.execute('''
            SELECT name, age, email, instructor_id FROM Instructors
            WHERE LOWER(name) LIKE ? OR LOWER(instructor_id) LIKE ?
        ''', ('%' + query + '%', '%' + query + '%'))
        instructors = cursor.fetchall()
        self.instructor_table.setRowCount(0)
        for row_data in instructors:
            row_number = self.instructor_table.rowCount()
            self.instructor_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.instructor_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def delete_instructor_record(self):
        """
        Deletes the selected instructor record from the database.
        """
        selected_items = self.instructor_table.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            email_item = self.instructor_table.item(selected_row, 2)
            email = email_item.text()
            cursor = self.parent.db.connection.cursor()
            try:
                cursor.execute('DELETE FROM Instructors WHERE email = ?', (email,))
                self.parent.db.connection.commit()
                QMessageBox.information(self, "Success", "Instructor record deleted.")
                self.load_instructors()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

# Course Page
class CoursePage(QWidget):
    """
    Represents the course management page.
    """
    def __init__(self, parent):
        """
        Initializes the course page.

        Args:
            parent (QMainWindow): Reference to the main window.
        """
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        """
        Sets up the UI components for the course page.
        """
        # Create a vertical layout
        layout = QVBoxLayout(self)

        # Title label
        course_label = QLabel("Add a Course", self)
        course_label.setFont(QtGui.QFont("Arial", 20))
        layout.addWidget(course_label)

        # Form layout for input fields
        form_layout = QGridLayout()

        # Course ID
        course_id_label = QLabel("Course ID:")
        self.course_id_entry = QLineEdit()
        form_layout.addWidget(course_id_label, 0, 0)
        form_layout.addWidget(self.course_id_entry, 0, 1)

        # Course Name
        course_name_label = QLabel("Course Name:")
        self.course_name_entry = QLineEdit()
        form_layout.addWidget(course_name_label, 1, 0)
        form_layout.addWidget(self.course_name_entry, 1, 1)

        # Add form layout to main layout
        layout.addLayout(form_layout)

        # Add Course Button
        self.add_course_button = QPushButton("Add Course")
        self.add_course_button.clicked.connect(self.add_course)
        layout.addWidget(self.add_course_button)

        # Register Student to Course section
        register_layout = QGridLayout()
        register_label = QLabel("Register Student for a Course", self)
        register_label.setFont(QtGui.QFont("Arial", 20))
        layout.addWidget(register_label)

        # Student Email
        student_email_label = QLabel("Student Email:")
        self.student_email_entry = QLineEdit()
        register_layout.addWidget(student_email_label, 0, 0)
        register_layout.addWidget(self.student_email_entry, 0, 1)

        # Course Dropdown
        course_dropdown_label = QLabel("Select Course:")
        self.course_dropdown = QComboBox()
        self.update_course_dropdown()
        register_layout.addWidget(course_dropdown_label, 1, 0)
        register_layout.addWidget(self.course_dropdown, 1, 1)

        # Register Student Button
        self.register_student_button = QPushButton("Register Student to Course")
        self.register_student_button.clicked.connect(self.register_course)
        register_layout.addWidget(self.register_student_button, 2, 0, 1, 2)

        # Add registration layout to main layout
        layout.addLayout(register_layout)

        # Course Table
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(3)
        self.course_table.setHorizontalHeaderLabels(["Course Name", "Course ID", "Instructor"])
        layout.addWidget(self.course_table)

        # Search bar and buttons
        search_layout = QHBoxLayout()
        course_search_label = QLabel("Search Courses by Name, ID, or Instructor:")
        self.course_search_entry = QLineEdit()
        self.search_course_button = QPushButton("Search")
        self.search_course_button.clicked.connect(self.search_course_table)
        self.delete_course_button = QPushButton("Delete")
        self.delete_course_button.clicked.connect(self.delete_course_record)
        search_layout.addWidget(course_search_label)
        search_layout.addWidget(self.course_search_entry)
        search_layout.addWidget(self.search_course_button)
        search_layout.addWidget(self.delete_course_button)
        layout.addLayout(search_layout)

        # Load initial data into the table
        self.load_courses()

    def add_course(self):
        """
        Adds a new course to the database and updates the table.
        """
        # Get input values
        course_id = self.course_id_entry.text()
        course_name = self.course_name_entry.text()

        # Validation
        if not course_id or not course_name:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields.")
            return

        try:
            # Create a Course object
            course = Course(course_id, course_name)
            # Insert into the database
            cursor = self.parent.db.connection.cursor()
            cursor.execute('''
                INSERT INTO Courses (course_id, course_name)
                VALUES (?, ?)
            ''', (course.course_id, course.course_name))
            self.parent.db.connection.commit()
            QMessageBox.information(self, "Success", f"Course {course.course_name} added.")
            # Refresh the course table
            self.load_courses()
            # Clear input fields
            self.course_id_entry.clear()
            self.course_name_entry.clear()
            # Update course dropdowns in other pages
            self.parent.instructor_page.update_course_dropdown()
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def load_courses(self):
        """
        Loads course data from the database into the table.
        """
        cursor = self.parent.db.connection.cursor()
        cursor.execute('''
            SELECT c.course_name, c.course_id, i.name FROM Courses c
            LEFT JOIN Instructors i ON c.instructor_id = i.id
        ''')
        courses = cursor.fetchall()
        self.course_table.setRowCount(0)
        for row_data in courses:
            row_number = self.course_table.rowCount()
            self.course_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.course_table.setItem(row_number, column_number, QTableWidgetItem(str(data) if data else ''))

        # Update course dropdowns
        self.update_course_dropdown()

    def update_course_dropdown(self):
        """
        Updates the course dropdown with the latest courses.
        """
        cursor = self.parent.db.connection.cursor()
        cursor.execute('SELECT course_name FROM Courses')
        courses = cursor.fetchall()
        course_names = [course[0] for course in courses]
        self.course_dropdown.clear()
        self.course_dropdown.addItems(course_names)

    def register_course(self):
        """
        Registers a student to a selected course.
        """
        # Get input values
        student_email = self.student_email_entry.text()
        course_name = self.course_dropdown.currentText()

        cursor = self.parent.db.connection.cursor()
        # Get student ID based on email
        cursor.execute('SELECT id FROM Students WHERE email = ?', (student_email,))
        student = cursor.fetchone()

        if student is None:
            QMessageBox.warning(self, "Error", "Student not found.")
            return

        student_id = student[0]

        # Get course ID based on course name
        cursor.execute('SELECT id FROM Courses WHERE course_name = ?', (course_name,))
        course = cursor.fetchone()

        if course is None:
            QMessageBox.warning(self, "Error", "Course not found.")
            return

        course_id = course[0]

        try:
            # Insert into the Registrations table
            cursor.execute('''
                INSERT INTO Registrations (student_id, course_id)
                VALUES (?, ?)
            ''', (student_id, course_id))
            self.parent.db.connection.commit()
            QMessageBox.information(self, "Success", "Student registered to course.")
            self.student_email_entry.clear()
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Error", "Student is already registered to this course.")

    def search_course_table(self):
        """
        Searches for courses based on the query and updates the table.
        """
        query = self.course_search_entry.text().lower()
        cursor = self.parent.db.connection.cursor()
        cursor.execute('''
            SELECT c.course_name, c.course_id, i.name FROM Courses c
            LEFT JOIN Instructors i ON c.instructor_id = i.id
            WHERE LOWER(c.course_name) LIKE ? OR LOWER(c.course_id) LIKE ? OR LOWER(i.name) LIKE ?
        ''', ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
        courses = cursor.fetchall()
        self.course_table.setRowCount(0)
        for row_data in courses:
            row_number = self.course_table.rowCount()
            self.course_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.course_table.setItem(row_number, column_number, QTableWidgetItem(str(data) if data else ''))

    def delete_course_record(self):
        """
        Deletes the selected course record from the database.
        """
        selected_items = self.course_table.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            course_id_item = self.course_table.item(selected_row, 1)
            course_id = course_id_item.text()
            cursor = self.parent.db.connection.cursor()
            try:
                cursor.execute('DELETE FROM Courses WHERE course_id = ?', (course_id,))
                self.parent.db.connection.commit()
                QMessageBox.information(self, "Success", "Course record deleted.")
                self.load_courses()
                # Update course dropdowns in other pages
                self.parent.instructor_page.update_course_dropdown()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

# Main entry point
if __name__ == '__main__':
    # Create the application
    app = QApplication(sys.argv)
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    # Start the event loop
    sys.exit(app.exec_())
