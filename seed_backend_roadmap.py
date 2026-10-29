"""
Seed Script: Backend Developer Roadmap
========================================
Creates a full career roadmap with milestones, topics, YouTube videos,
quizzes (with MCQ questions), and coding challenges.

Run: py seed_backend_roadmap.py
"""

import json
import datetime
from sqlalchemy.orm import Session
from app.database.connection import engine, SessionLocal
from app.models.models import (
    Career, Roadmap, Topic, Video, Quiz, Question,
    CodingChallenge, Resource
)


def seed():
    db: Session = SessionLocal()

    try:
        # ===================================================
        # 1. CREATE OR FETCH CAREER
        # ===================================================
        career = db.query(Career).filter(Career.name == "Backend Developer").first()
        if not career:
            career = Career(
                name="Backend Developer",
                slug="backend-developer",
                icon="bi-server",
                badge="⚙️",
                description="Master Python, databases, REST APIs, FastAPI/Django, authentication, deployment, and scalable server-side architecture.",
                total_topics=18,
                is_active=True,
                is_deleted=False
            )
            db.add(career)
            db.commit()
            db.refresh(career)
            print(f"✅ Created Career: Backend Developer (ID: {career.id})")
        else:
            print(f"ℹ️  Career 'Backend Developer' already exists (ID: {career.id}). Checking for missing data...")

        # ===================================================
        # 2. ROADMAP MILESTONES + TOPICS + VIDEOS + QUIZZES + CHALLENGES
        # ===================================================
        roadmap_data = [
            # =============================================
            # MILESTONE 1: Python Core
            # =============================================
            {
                "title": "Milestone 1: Python Programming Fundamentals",
                "description": "Master Python syntax, data types, control flow, functions, OOP, and file handling — the foundation for all backend development.",
                "order": 1,
                "topics": [
                    {
                        "title": "Python Variables, Data Types & Operators",
                        "description": "Learn Python variables, primitive data types (int, float, str, bool), type casting, and arithmetic/comparison/logical operators.",
                        "learning_objectives": "Declare and use variables in Python\nUnderstand primitive and compound data types\nPerform type casting and conversion\nUse arithmetic, comparison, and logical operators",
                        "difficulty": "easy",
                        "estimated_time": 2.0,
                        "order": 1,
                        "notes": "Python is dynamically typed — no need to declare variable types.\n\nData Types:\n- int: 42\n- float: 3.14\n- str: 'hello'\n- bool: True/False\n- list: [1, 2, 3]\n- tuple: (1, 2, 3)\n- dict: {'key': 'value'}\n- set: {1, 2, 3}\n- NoneType: None\n\nOperators:\nArithmetic: + - * / // % **\nComparison: == != < > <= >=\nLogical: and or not\nAssignment: = += -= *= /=",
                        "cheat_sheet": "VARIABLES:\nname = 'Python'\nage = 25\npi = 3.14\nis_active = True\n\nTYPE CHECKING:\ntype(variable)\nisinstance(x, int)\n\nCASTING:\nint('42'), float('3.14'), str(100), bool(0)\n\nSTRING METHODS:\n.upper(), .lower(), .strip(), .split(), .join(), .replace(), .find(), f-strings: f'{var}'",
                        "videos": [
                            {"title": "Python Tutorial for Beginners - Full Course", "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc"},
                            {"title": "Python Crash Course For Beginners", "url": "https://www.youtube.com/watch?v=JJmcL1N2KQs"}
                        ],
                        "docs": [
                            {"title": "Python Official Documentation", "url": "https://docs.python.org/3/tutorial/"},
                            {"title": "W3Schools Python Tutorial", "url": "https://www.w3schools.com/python/"}
                        ],
                        "quiz_questions": [
                            {"text": "What is the output of type(3.14) in Python?", "a": "<class 'int'>", "b": "<class 'float'>", "c": "<class 'str'>", "d": "<class 'double'>", "correct": "B", "exp": "3.14 is a floating-point number, so type() returns <class 'float'>."},
                            {"text": "Which operator performs floor division in Python?", "a": "/", "b": "//", "c": "%", "d": "**", "correct": "B", "exp": "// divides and truncates the result to the nearest integer (floor division)."},
                            {"text": "What is the result of bool(0) in Python?", "a": "True", "b": "False", "c": "0", "d": "None", "correct": "B", "exp": "In Python, 0, empty strings, empty lists, and None evaluate to False."},
                            {"text": "Which keyword is used to check variable type in Python?", "a": "typeof", "b": "instanceof", "c": "type()", "d": "check()", "correct": "C", "exp": "The type() function returns the data type of a variable."},
                        ],
                        "challenges": [
                            {
                                "title": "Temperature Converter",
                                "description": "Write a function that converts Celsius to Fahrenheit using the formula: F = (C × 9/5) + 32",
                                "difficulty": "easy",
                                "template_code": "def celsius_to_fahrenheit(celsius):\n    # Convert celsius to fahrenheit\n    # Formula: F = (C * 9/5) + 32\n    pass",
                                "test_cases": json.dumps([
                                    {"function_name": "celsius_to_fahrenheit", "args": [0], "expected": 32.0},
                                    {"function_name": "celsius_to_fahrenheit", "args": [100], "expected": 212.0},
                                    {"function_name": "celsius_to_fahrenheit", "args": [37], "expected": 98.6},
                                ]),
                                "score_points": 10
                            }
                        ]
                    },
                    {
                        "title": "Python Control Flow & Loops",
                        "description": "Master if/elif/else conditions, for loops, while loops, break/continue, list comprehensions, and nested control flow.",
                        "learning_objectives": "Write conditional statements with if/elif/else\nIterate with for and while loops\nUse break, continue, and pass\nWrite list comprehensions for concise data transformation",
                        "difficulty": "easy",
                        "estimated_time": 2.5,
                        "order": 2,
                        "notes": "Control Flow:\nif condition:\n    ...\nelif condition:\n    ...\nelse:\n    ...\n\nLoops:\nfor item in iterable:\n    ...\n\nwhile condition:\n    ...\n\nList Comprehension:\n[expression for item in iterable if condition]\n\nUseful:\nrange(start, stop, step)\nenumerate(iterable)\nzip(list1, list2)",
                        "cheat_sheet": "IF/ELSE:\nif x > 0:\n    print('positive')\nelif x == 0:\n    print('zero')\nelse:\n    print('negative')\n\nFOR LOOP:\nfor i in range(10):\n    print(i)\n\nLIST COMP:\nsquares = [x**2 for x in range(10)]\nevens = [x for x in nums if x % 2 == 0]\n\nTERNARY:\nresult = 'yes' if condition else 'no'",
                        "videos": [
                            {"title": "Python If Else & Loops Tutorial", "url": "https://www.youtube.com/watch?v=PqFKRqpHrjw"},
                            {"title": "Python Loops Full Tutorial", "url": "https://www.youtube.com/watch?v=94UHCEmprCY"}
                        ],
                        "docs": [
                            {"title": "Python Control Flow", "url": "https://docs.python.org/3/tutorial/controlflow.html"},
                        ],
                        "quiz_questions": [
                            {"text": "What is the output of: [x**2 for x in range(4)]?", "a": "[1, 4, 9, 16]", "b": "[0, 1, 4, 9]", "c": "[0, 2, 4, 6]", "d": "[1, 2, 3, 4]", "correct": "B", "exp": "range(4) produces 0,1,2,3 and x**2 gives 0,1,4,9."},
                            {"text": "Which keyword skips the current iteration and continues with the next?", "a": "break", "b": "pass", "c": "continue", "d": "skip", "correct": "C", "exp": "'continue' skips the rest of the current iteration and moves to the next loop cycle."},
                            {"text": "What does 'pass' do in Python?", "a": "Exits the loop", "b": "Does nothing (placeholder)", "c": "Returns None", "d": "Raises an error", "correct": "B", "exp": "'pass' is a null operation — it does nothing and serves as a placeholder in code blocks."},
                        ],
                        "challenges": [
                            {
                                "title": "FizzBuzz Challenge",
                                "description": "Write a function that returns a list of strings from 1 to n. For multiples of 3, use 'Fizz'; for 5, use 'Buzz'; for both, use 'FizzBuzz'.",
                                "difficulty": "easy",
                                "template_code": "def fizzbuzz(n):\n    # Return a list of strings from 1 to n\n    # Replace multiples of 3 with 'Fizz'\n    # Replace multiples of 5 with 'Buzz'\n    # Replace multiples of both 3 and 5 with 'FizzBuzz'\n    # Otherwise, use the number as a string\n    pass",
                                "test_cases": json.dumps([
                                    {"function_name": "fizzbuzz", "args": [5], "expected": ["1", "2", "Fizz", "4", "Buzz"]},
                                    {"function_name": "fizzbuzz", "args": [15], "expected": ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]},
                                ]),
                                "score_points": 15
                            }
                        ]
                    },
                    {
                        "title": "Python Functions & Modules",
                        "description": "Master function definitions, parameters, return values, *args/**kwargs, lambda functions, decorators, and module imports.",
                        "learning_objectives": "Define functions with parameters and return values\nUse *args and **kwargs for flexible arguments\nWrite lambda functions and closures\nImport and create Python modules",
                        "difficulty": "medium",
                        "estimated_time": 3.0,
                        "order": 3,
                        "notes": "Functions:\ndef function_name(param1, param2='default'):\n    '''docstring'''\n    return result\n\nAdvanced:\n*args = variable positional arguments\n**kwargs = variable keyword arguments\nlambda x: x * 2\n\nDecorators:\ndef decorator(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n    return wrapper\n\nModules:\nimport math\nfrom os import path\nimport json as j",
                        "cheat_sheet": "FUNCTIONS:\ndef greet(name, greeting='Hello'):\n    return f'{greeting}, {name}!'\n\nLAMBDA:\nsquare = lambda x: x**2\n\nARGS/KWARGS:\ndef func(*args, **kwargs):\n    print(args)   # tuple\n    print(kwargs)  # dict\n\nDECORATOR:\n@my_decorator\ndef my_func(): pass\n\nMODULES:\nimport os, sys, json, datetime",
                        "videos": [
                            {"title": "Python Functions - Complete Tutorial", "url": "https://www.youtube.com/watch?v=9Os0o3wzS_I"},
                            {"title": "Python Decorators in 15 Minutes", "url": "https://www.youtube.com/watch?v=FXUUSfJO_J4"}
                        ],
                        "docs": [
                            {"title": "Python Functions Documentation", "url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions"},
                        ],
                        "quiz_questions": [
                            {"text": "What does **kwargs represent in a function definition?", "a": "A list of arguments", "b": "A dictionary of keyword arguments", "c": "A tuple of values", "d": "A set of parameters", "correct": "B", "exp": "**kwargs collects additional keyword arguments into a dictionary."},
                            {"text": "What is a lambda function?", "a": "A named function", "b": "An anonymous single-expression function", "c": "A recursive function", "d": "A generator function", "correct": "B", "exp": "Lambda functions are anonymous, single-expression functions: lambda x: x * 2."},
                            {"text": "What is a decorator in Python?", "a": "A CSS styling tool", "b": "A function that modifies another function's behavior", "c": "A data type", "d": "A loop construct", "correct": "B", "exp": "Decorators wrap functions to extend their behavior without modifying the original code."},
                        ],
                        "challenges": [
                            {
                                "title": "Decorator: Execution Timer",
                                "description": "Write a decorator that measures and returns the execution time of a function.",
                                "difficulty": "medium",
                                "template_code": "import time\n\ndef timer_decorator(func):\n    # Create a decorator that wraps func\n    # and returns a tuple: (result, elapsed_time_in_seconds)\n    pass\n\n@timer_decorator\ndef slow_add(a, b):\n    time.sleep(0.1)\n    return a + b\n\ndef test_decorator():\n    result, elapsed = slow_add(3, 4)\n    return result",
                                "test_cases": json.dumps([
                                    {"function_name": "test_decorator", "args": [], "expected": 7},
                                ]),
                                "score_points": 20
                            }
                        ]
                    }
                ]
            },
            # =============================================
            # MILESTONE 2: Python OOP & Data Structures
            # =============================================
            {
                "title": "Milestone 2: Object-Oriented Python & Data Structures",
                "description": "Master OOP principles — classes, inheritance, polymorphism, encapsulation — and Python data structures for efficient backend coding.",
                "order": 2,
                "topics": [
                    {
                        "title": "Python OOP: Classes & Objects",
                        "description": "Learn object-oriented programming with classes, objects, constructors, instance/class methods, properties, and magic methods.",
                        "learning_objectives": "Define classes with attributes and methods\nUse __init__ constructor and self\nImplement class methods and static methods\nOverride magic methods like __str__ and __repr__",
                        "difficulty": "medium",
                        "estimated_time": 3.5,
                        "order": 1,
                        "notes": "OOP Fundamentals:\nclass MyClass:\n    class_var = 'shared'\n    \n    def __init__(self, name):\n        self.name = name  # instance variable\n    \n    def greet(self):\n        return f'Hello, {self.name}'\n    \n    @classmethod\n    def from_dict(cls, data):\n        return cls(data['name'])\n    \n    @staticmethod\n    def validate(name):\n        return len(name) > 0\n    \n    def __str__(self):\n        return self.name",
                        "cheat_sheet": "CLASS:\nclass Dog:\n    species = 'Canine'  # class var\n    def __init__(self, name, age):\n        self.name = name  # instance var\n        self.age = age\n    def bark(self):\n        return f'{self.name} says Woof!'\n    def __str__(self):\n        return f'Dog({self.name})'\n\nUSAGE:\ndog = Dog('Rex', 3)\ndog.bark()\nstr(dog)",
                        "videos": [
                            {"title": "Python OOP Tutorial - Full Course", "url": "https://www.youtube.com/watch?v=ZDa-Z5JzLYM"},
                            {"title": "Python Classes and Objects", "url": "https://www.youtube.com/watch?v=apACNr7DC_s"}
                        ],
                        "docs": [
                            {"title": "Python OOP Documentation", "url": "https://docs.python.org/3/tutorial/classes.html"},
                        ],
                        "quiz_questions": [
                            {"text": "What does the __init__ method do in a Python class?", "a": "Deletes the object", "b": "Initializes the object's attributes when created", "c": "Returns the class name", "d": "Creates a new class", "correct": "B", "exp": "__init__ is the constructor method — it runs automatically when creating a new object."},
                            {"text": "What does 'self' refer to in a Python class?", "a": "The class itself", "b": "The current instance of the class", "c": "The parent class", "d": "A global variable", "correct": "B", "exp": "'self' refers to the current instance, allowing access to instance attributes and methods."},
                            {"text": "Which decorator creates a method that belongs to the class, not instances?", "a": "@property", "b": "@staticmethod", "c": "@classmethod", "d": "@abstract", "correct": "C", "exp": "@classmethod receives the class (cls) as its first argument instead of an instance (self)."},
                        ],
                        "challenges": [
                            {
                                "title": "Bank Account Class",
                                "description": "Create a BankAccount class with deposit, withdraw, and get_balance methods.",
                                "difficulty": "medium",
                                "template_code": "class BankAccount:\n    def __init__(self, owner, balance=0):\n        pass\n    \n    def deposit(self, amount):\n        pass\n    \n    def withdraw(self, amount):\n        # Return False if insufficient funds\n        pass\n    \n    def get_balance(self):\n        pass\n\ndef test_bank():\n    acc = BankAccount('Alice', 100)\n    acc.deposit(50)\n    acc.withdraw(30)\n    return acc.get_balance()",
                                "test_cases": json.dumps([
                                    {"function_name": "test_bank", "args": [], "expected": 120},
                                ]),
                                "score_points": 20
                            }
                        ]
                    },
                    {
                        "title": "Python Inheritance & Polymorphism",
                        "description": "Learn inheritance hierarchies, method overriding, super(), multiple inheritance, abstract classes, and polymorphism.",
                        "learning_objectives": "Implement single and multiple inheritance\nOverride methods and use super()\nCreate abstract base classes with ABC\nApply polymorphism in real-world patterns",
                        "difficulty": "medium",
                        "estimated_time": 3.0,
                        "order": 2,
                        "videos": [
                            {"title": "Python Inheritance Tutorial", "url": "https://www.youtube.com/watch?v=Cn7AkDb4pIU"},
                            {"title": "Python OOP - Inheritance & Polymorphism", "url": "https://www.youtube.com/watch?v=RSl87lqOXDE"}
                        ],
                        "docs": [
                            {"title": "Python Inheritance", "url": "https://docs.python.org/3/tutorial/classes.html#inheritance"},
                        ],
                        "quiz_questions": [
                            {"text": "What does super().__init__() do?", "a": "Creates a new class", "b": "Calls the parent class constructor", "c": "Deletes the parent class", "d": "Returns None", "correct": "B", "exp": "super().__init__() calls the parent class's __init__ method to initialize inherited attributes."},
                            {"text": "What is polymorphism in OOP?", "a": "Multiple classes with multiple attributes", "b": "Objects of different classes responding to the same method call differently", "c": "Creating many instances of one class", "d": "Using multiple programming languages", "correct": "B", "exp": "Polymorphism allows different classes to implement the same method with different behaviors."},
                            {"text": "Which module provides Abstract Base Classes in Python?", "a": "os", "b": "sys", "c": "abc", "d": "abstract", "correct": "C", "exp": "The 'abc' module provides the ABC class and @abstractmethod decorator for abstract base classes."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "Python Data Structures & Algorithms",
                        "description": "Master lists, dictionaries, sets, tuples, stacks, queues, sorting algorithms, and Big-O complexity analysis.",
                        "learning_objectives": "Use Python built-in data structures effectively\nImplement stacks and queues\nAnalyze time/space complexity (Big-O)\nApply common sorting and searching algorithms",
                        "difficulty": "hard",
                        "estimated_time": 4.0,
                        "order": 3,
                        "videos": [
                            {"title": "Data Structures in Python - Full Course", "url": "https://www.youtube.com/watch?v=pkYVOmU3MgA"},
                            {"title": "Algorithms and Data Structures - Full Tutorial", "url": "https://www.youtube.com/watch?v=8hly31xKli0"}
                        ],
                        "docs": [
                            {"title": "Python Data Structures", "url": "https://docs.python.org/3/tutorial/datastructures.html"},
                        ],
                        "quiz_questions": [
                            {"text": "What is the time complexity of searching in a Python dictionary?", "a": "O(n)", "b": "O(log n)", "c": "O(1) average", "d": "O(n²)", "correct": "C", "exp": "Python dictionaries use hash tables, giving O(1) average lookup time."},
                            {"text": "Which data structure follows LIFO (Last In, First Out)?", "a": "Queue", "b": "Stack", "c": "Linked List", "d": "Tree", "correct": "B", "exp": "Stacks follow LIFO — the last element added is the first one removed (push/pop)."},
                            {"text": "What is the time complexity of Python's built-in sort()?", "a": "O(n)", "b": "O(n log n)", "c": "O(n²)", "d": "O(log n)", "correct": "B", "exp": "Python uses TimSort, which has O(n log n) average and worst-case complexity."},
                        ],
                        "challenges": [
                            {
                                "title": "Stack Implementation",
                                "description": "Implement a Stack class with push, pop, peek, and is_empty methods.",
                                "difficulty": "medium",
                                "template_code": "class Stack:\n    def __init__(self):\n        pass\n    \n    def push(self, item):\n        pass\n    \n    def pop(self):\n        # Return None if empty\n        pass\n    \n    def peek(self):\n        # Return top without removing, None if empty\n        pass\n    \n    def is_empty(self):\n        pass\n\ndef test_stack():\n    s = Stack()\n    s.push(10)\n    s.push(20)\n    s.push(30)\n    s.pop()\n    return s.peek()",
                                "test_cases": json.dumps([
                                    {"function_name": "test_stack", "args": [], "expected": 20},
                                ]),
                                "score_points": 20
                            }
                        ],
                        "notes": "",
                        "cheat_sheet": ""
                    }
                ]
            },
            # =============================================
            # MILESTONE 3: Databases & SQL
            # =============================================
            {
                "title": "Milestone 3: Databases & SQL Mastery",
                "description": "Master relational databases, SQL queries, joins, indexing, transactions, and ORM integration with SQLAlchemy.",
                "order": 3,
                "topics": [
                    {
                        "title": "SQL Fundamentals & CRUD Operations",
                        "description": "Learn SQL basics — CREATE, SELECT, INSERT, UPDATE, DELETE — data types, constraints, and basic query writing.",
                        "learning_objectives": "Write SQL CREATE TABLE statements\nPerform CRUD operations (SELECT, INSERT, UPDATE, DELETE)\nUse WHERE, ORDER BY, LIMIT, and DISTINCT\nApply data types and constraints (PRIMARY KEY, NOT NULL, UNIQUE)",
                        "difficulty": "easy",
                        "estimated_time": 3.0,
                        "order": 1,
                        "videos": [
                            {"title": "SQL Tutorial - Full Database Course for Beginners", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY"},
                            {"title": "MySQL Tutorial for Beginners", "url": "https://www.youtube.com/watch?v=7S_tz1z_5bA"}
                        ],
                        "docs": [
                            {"title": "W3Schools SQL Tutorial", "url": "https://www.w3schools.com/sql/"},
                            {"title": "MySQL Official Documentation", "url": "https://dev.mysql.com/doc/refman/8.0/en/"}
                        ],
                        "quiz_questions": [
                            {"text": "Which SQL command retrieves data from a database?", "a": "GET", "b": "FETCH", "c": "SELECT", "d": "RETRIEVE", "correct": "C", "exp": "SELECT is the SQL statement used to query and retrieve data from database tables."},
                            {"text": "Which constraint ensures all values in a column are different?", "a": "PRIMARY KEY", "b": "NOT NULL", "c": "UNIQUE", "d": "CHECK", "correct": "C", "exp": "UNIQUE constraint ensures that all values in a column are distinct — no duplicates allowed."},
                            {"text": "Which SQL clause filters records based on a condition?", "a": "ORDER BY", "b": "GROUP BY", "c": "HAVING", "d": "WHERE", "correct": "D", "exp": "WHERE filters rows before grouping based on specified conditions."},
                        ],
                        "challenges": [
                            {
                                "title": "SQL Query Builder",
                                "description": "Write a function that builds a SELECT SQL query string from table name, columns, and optional where clause.",
                                "difficulty": "easy",
                                "template_code": "def build_select_query(table, columns, where=None):\n    # Build a SELECT query string\n    # columns is a list of column names\n    # where is an optional string condition\n    # Return the SQL query string\n    pass",
                                "test_cases": json.dumps([
                                    {"function_name": "build_select_query", "args": ["users", ["name", "email"], None], "expected": "SELECT name, email FROM users"},
                                    {"function_name": "build_select_query", "args": ["orders", ["id", "total"], "total > 100"], "expected": "SELECT id, total FROM orders WHERE total > 100"},
                                ]),
                                "score_points": 15
                            }
                        ],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "SQL Joins, Subqueries & Advanced Queries",
                        "description": "Master SQL JOINs (INNER, LEFT, RIGHT, FULL), subqueries, aggregate functions, GROUP BY, HAVING, and query optimization.",
                        "learning_objectives": "Write INNER, LEFT, RIGHT, and FULL JOIN queries\nUse aggregate functions (COUNT, SUM, AVG, MAX, MIN)\nApply GROUP BY and HAVING clauses\nWrite subqueries and nested queries",
                        "difficulty": "medium",
                        "estimated_time": 3.5,
                        "order": 2,
                        "videos": [
                            {"title": "SQL Joins Explained", "url": "https://www.youtube.com/watch?v=9yeOJ0ZMUYw"},
                            {"title": "Advanced SQL Tutorial", "url": "https://www.youtube.com/watch?v=M-55BmjOuXY"}
                        ],
                        "docs": [
                            {"title": "SQL JOIN Tutorial", "url": "https://www.w3schools.com/sql/sql_join.asp"},
                        ],
                        "quiz_questions": [
                            {"text": "Which JOIN returns all rows when there is a match in either table?", "a": "INNER JOIN", "b": "LEFT JOIN", "c": "FULL OUTER JOIN", "d": "CROSS JOIN", "correct": "C", "exp": "FULL OUTER JOIN returns all rows from both tables, with NULLs where there's no match."},
                            {"text": "Which aggregate function counts the number of rows?", "a": "SUM()", "b": "TOTAL()", "c": "COUNT()", "d": "NUM()", "correct": "C", "exp": "COUNT() returns the number of rows matching the query criteria."},
                            {"text": "Which clause filters groups after GROUP BY?", "a": "WHERE", "b": "FILTER", "c": "HAVING", "d": "GROUP FILTER", "correct": "C", "exp": "HAVING filters groups after GROUP BY aggregation. WHERE filters individual rows before grouping."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "SQLAlchemy ORM & Database Integration",
                        "description": "Learn SQLAlchemy ORM — models, sessions, queries, relationships, migrations, and integrating databases with Python.",
                        "learning_objectives": "Define SQLAlchemy models and table mappings\nPerform CRUD operations with ORM sessions\nCreate relationships (one-to-many, many-to-many)\nUse Alembic for database migrations",
                        "difficulty": "hard",
                        "estimated_time": 4.0,
                        "order": 3,
                        "videos": [
                            {"title": "SQLAlchemy Tutorial - Python ORM", "url": "https://www.youtube.com/watch?v=AKQ3XEDI9Mw"},
                            {"title": "Python SQLAlchemy Complete Tutorial", "url": "https://www.youtube.com/watch?v=cYWiDiIUxQc"}
                        ],
                        "docs": [
                            {"title": "SQLAlchemy Documentation", "url": "https://docs.sqlalchemy.org/en/20/"},
                            {"title": "SQLAlchemy ORM Tutorial", "url": "https://docs.sqlalchemy.org/en/20/orm/tutorial.html"}
                        ],
                        "quiz_questions": [
                            {"text": "What does ORM stand for?", "a": "Object Relational Mapping", "b": "Online Resource Manager", "c": "Output Rendering Module", "d": "Object Request Model", "correct": "A", "exp": "ORM (Object Relational Mapping) maps database tables to Python classes and rows to objects."},
                            {"text": "Which SQLAlchemy function creates a database session?", "a": "connect()", "b": "Session()", "c": "sessionmaker()", "d": "create_session()", "correct": "C", "exp": "sessionmaker() creates a factory for Session objects that manage database transactions."},
                            {"text": "What does db.commit() do in SQLAlchemy?", "a": "Rolls back changes", "b": "Persists pending changes to the database", "c": "Creates a new table", "d": "Closes the connection", "correct": "B", "exp": "db.commit() saves all pending changes (inserts, updates, deletes) to the database permanently."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    }
                ]
            },
            # =============================================
            # MILESTONE 4: REST APIs & FastAPI
            # =============================================
            {
                "title": "Milestone 4: REST APIs & FastAPI",
                "description": "Build production-grade REST APIs with FastAPI — routing, request/response models, validation, middleware, and documentation.",
                "order": 4,
                "topics": [
                    {
                        "title": "REST API Concepts & Design Principles",
                        "description": "Understand REST architecture, HTTP methods, status codes, URL design, request/response formats, and API versioning.",
                        "learning_objectives": "Understand REST architectural principles\nDesign clean URL endpoints\nUse appropriate HTTP methods and status codes\nPlan API versioning strategies",
                        "difficulty": "medium",
                        "estimated_time": 2.5,
                        "order": 1,
                        "videos": [
                            {"title": "REST API Concepts and Examples", "url": "https://www.youtube.com/watch?v=7YcW25PHnAA"},
                            {"title": "RESTful APIs in 100 Seconds", "url": "https://www.youtube.com/watch?v=-MTSQjw5DrM"}
                        ],
                        "docs": [
                            {"title": "REST API Tutorial", "url": "https://restfulapi.net/"},
                            {"title": "HTTP Status Codes", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status"}
                        ],
                        "quiz_questions": [
                            {"text": "What does REST stand for?", "a": "Remote Execution Server Technology", "b": "Representational State Transfer", "c": "Request and Server Transaction", "d": "Resource Endpoint Service Transfer", "correct": "B", "exp": "REST (Representational State Transfer) is an architectural style for designing networked applications."},
                            {"text": "Which HTTP method is used to update an existing resource?", "a": "POST", "b": "GET", "c": "PUT", "d": "DELETE", "correct": "C", "exp": "PUT replaces/updates an existing resource with the provided data."},
                            {"text": "What HTTP status code indicates resource created successfully?", "a": "200", "b": "201", "c": "204", "d": "301", "correct": "B", "exp": "HTTP 201 Created indicates that a new resource was successfully created."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "FastAPI: Routes, Models & Validation",
                        "description": "Build APIs with FastAPI — define routes, path/query parameters, Pydantic models for validation, and automatic documentation.",
                        "learning_objectives": "Create FastAPI applications and routes\nUse path and query parameters\nValidate data with Pydantic models\nGenerate automatic API documentation (Swagger/OpenAPI)",
                        "difficulty": "medium",
                        "estimated_time": 4.0,
                        "order": 2,
                        "videos": [
                            {"title": "FastAPI Full Course for Beginners", "url": "https://www.youtube.com/watch?v=7t2alSnE2-I"},
                            {"title": "FastAPI Tutorial - Building RESTful APIs", "url": "https://www.youtube.com/watch?v=0sOvCWFmrtA"}
                        ],
                        "docs": [
                            {"title": "FastAPI Official Documentation", "url": "https://fastapi.tiangolo.com/"},
                            {"title": "FastAPI Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/"}
                        ],
                        "quiz_questions": [
                            {"text": "What library does FastAPI use for request validation?", "a": "marshmallow", "b": "pydantic", "c": "cerberus", "d": "voluptuous", "correct": "B", "exp": "FastAPI uses Pydantic for data validation, serialization, and type enforcement."},
                            {"text": "Which decorator creates a GET endpoint in FastAPI?", "a": "@app.route('/path')", "b": "@app.get('/path')", "c": "@get('/path')", "d": "@router.api('/path')", "correct": "B", "exp": "@app.get('/path') defines a GET endpoint in FastAPI."},
                            {"text": "What URL provides auto-generated API docs in FastAPI?", "a": "/api", "b": "/docs", "c": "/swagger", "d": "/help", "correct": "B", "exp": "FastAPI auto-generates interactive Swagger UI documentation at /docs."},
                        ],
                        "challenges": [
                            {
                                "title": "API Response Builder",
                                "description": "Write a function that builds standardized API response dictionaries.",
                                "difficulty": "easy",
                                "template_code": "def api_response(status, message, data=None):\n    # Return a dict with keys: 'status', 'message', 'data'\n    # status should be 'success' or 'error'\n    # data defaults to None if not provided\n    pass",
                                "test_cases": json.dumps([
                                    {"function_name": "api_response", "args": ["success", "User created", {"id": 1}], "expected": {"status": "success", "message": "User created", "data": {"id": 1}}},
                                    {"function_name": "api_response", "args": ["error", "Not found"], "expected": {"status": "error", "message": "Not found", "data": None}},
                                ]),
                                "score_points": 10
                            }
                        ],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "FastAPI: Authentication & Middleware",
                        "description": "Implement authentication (JWT, OAuth2), middleware, CORS, rate limiting, and security best practices in FastAPI.",
                        "learning_objectives": "Implement JWT token authentication\nUse OAuth2 password flow\nAdd CORS middleware for cross-origin requests\nApply security best practices (hashing, HTTPS)",
                        "difficulty": "hard",
                        "estimated_time": 4.5,
                        "order": 3,
                        "videos": [
                            {"title": "FastAPI Authentication with JWT", "url": "https://www.youtube.com/watch?v=5GxQ1rLTwaU"},
                            {"title": "FastAPI Security - OAuth2 Tutorial", "url": "https://www.youtube.com/watch?v=6hTRw_HK3Ts"}
                        ],
                        "docs": [
                            {"title": "FastAPI Security", "url": "https://fastapi.tiangolo.com/tutorial/security/"},
                            {"title": "JWT Introduction", "url": "https://jwt.io/introduction"}
                        ],
                        "quiz_questions": [
                            {"text": "What does JWT stand for?", "a": "Java Web Token", "b": "JSON Web Token", "c": "JavaScript Worker Thread", "d": "Joint Web Transfer", "correct": "B", "exp": "JWT (JSON Web Token) is a compact, URL-safe token format for securely transmitting claims."},
                            {"text": "What does CORS stand for?", "a": "Cross-Origin Resource Sharing", "b": "Common Object Request System", "c": "Client Origin Response Server", "d": "Cache Optimized Resource Storage", "correct": "A", "exp": "CORS allows servers to specify which origins can access their resources from a browser."},
                            {"text": "Which Python library is commonly used for password hashing?", "a": "hashlib", "b": "bcrypt", "c": "base64", "d": "hmac", "correct": "B", "exp": "bcrypt is the industry standard for securely hashing passwords with automatic salting."},
                        ],
                        "challenges": [
                            {
                                "title": "JWT Payload Builder",
                                "description": "Write a function that creates a JWT-style payload dictionary with user data and expiration.",
                                "difficulty": "medium",
                                "template_code": "import time\n\ndef create_jwt_payload(user_id, username, role, expires_in_seconds=3600):\n    # Return a dict with:\n    # 'sub': user_id, 'username': username, 'role': role,\n    # 'iat': current timestamp (int), 'exp': iat + expires_in_seconds\n    pass\n\ndef test_jwt_payload():\n    payload = create_jwt_payload(1, 'admin', 'super_admin', 3600)\n    # Check structure\n    return payload['sub'] == 1 and payload['username'] == 'admin' and payload['role'] == 'super_admin' and payload['exp'] - payload['iat'] == 3600",
                                "test_cases": json.dumps([
                                    {"function_name": "test_jwt_payload", "args": [], "expected": True},
                                ]),
                                "score_points": 20
                            }
                        ],
                        "notes": "",
                        "cheat_sheet": ""
                    }
                ]
            },
            # =============================================
            # MILESTONE 5: Testing, Error Handling & Logging
            # =============================================
            {
                "title": "Milestone 5: Testing, Error Handling & Logging",
                "description": "Write robust backend code — unit testing with pytest, error handling patterns, logging, and debugging strategies.",
                "order": 5,
                "topics": [
                    {
                        "title": "Python Error Handling & Exceptions",
                        "description": "Master try/except/finally, custom exceptions, exception hierarchies, and graceful error recovery patterns.",
                        "learning_objectives": "Write try/except/finally blocks\nCreate custom exception classes\nUse exception chaining and context managers\nImplement graceful error recovery patterns",
                        "difficulty": "medium",
                        "estimated_time": 2.5,
                        "order": 1,
                        "videos": [
                            {"title": "Python Exceptions and Error Handling", "url": "https://www.youtube.com/watch?v=NIWwJbo-9_8"},
                            {"title": "Python Try Except Tutorial", "url": "https://www.youtube.com/watch?v=HQqqNBZosn8"}
                        ],
                        "docs": [
                            {"title": "Python Errors and Exceptions", "url": "https://docs.python.org/3/tutorial/errors.html"},
                        ],
                        "quiz_questions": [
                            {"text": "Which block runs regardless of whether an exception occurred?", "a": "except", "b": "else", "c": "finally", "d": "catch", "correct": "C", "exp": "The 'finally' block always runs, whether an exception occurred or not — used for cleanup."},
                            {"text": "How do you create a custom exception in Python?", "a": "def MyError(): pass", "b": "class MyError(Exception): pass", "c": "raise CustomError", "d": "error MyError = Exception", "correct": "B", "exp": "Custom exceptions inherit from the Exception class."},
                            {"text": "What keyword is used to trigger an exception manually?", "a": "throw", "b": "error", "c": "raise", "d": "except", "correct": "C", "exp": "The 'raise' keyword manually triggers an exception."},
                        ],
                        "challenges": [
                            {
                                "title": "Safe Division Function",
                                "description": "Write a function that safely divides two numbers, handling ZeroDivisionError and TypeError.",
                                "difficulty": "easy",
                                "template_code": "def safe_divide(a, b):\n    # Divide a by b safely\n    # Return the result if successful\n    # Return 'Error: Division by zero' for ZeroDivisionError\n    # Return 'Error: Invalid input' for TypeError\n    pass",
                                "test_cases": json.dumps([
                                    {"function_name": "safe_divide", "args": [10, 2], "expected": 5.0},
                                    {"function_name": "safe_divide", "args": [10, 0], "expected": "Error: Division by zero"},
                                    {"function_name": "safe_divide", "args": ["a", 5], "expected": "Error: Invalid input"},
                                ]),
                                "score_points": 10
                            }
                        ],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "Unit Testing with Pytest",
                        "description": "Learn automated testing with pytest — test functions, fixtures, parametrize, mocking, and test-driven development (TDD).",
                        "learning_objectives": "Write test functions with pytest\nUse fixtures for test setup and teardown\nParametrize tests for multiple inputs\nMock external dependencies in tests",
                        "difficulty": "medium",
                        "estimated_time": 3.0,
                        "order": 2,
                        "videos": [
                            {"title": "Pytest Tutorial - Full Course", "url": "https://www.youtube.com/watch?v=cHYq1MRoyI0"},
                            {"title": "Python Testing with Pytest", "url": "https://www.youtube.com/watch?v=YbpKMIUjvK8"}
                        ],
                        "docs": [
                            {"title": "Pytest Documentation", "url": "https://docs.pytest.org/en/stable/"},
                        ],
                        "quiz_questions": [
                            {"text": "What naming convention must pytest test functions follow?", "a": "Start with 'check_'", "b": "Start with 'test_'", "c": "End with '_test'", "d": "Contain 'assert'", "correct": "B", "exp": "Pytest auto-discovers functions starting with 'test_' and files starting with 'test_' or ending with '_test.py'."},
                            {"text": "What is a pytest fixture?", "a": "A broken test", "b": "A function that provides setup data or state for tests", "c": "A test assertion", "d": "A debugging tool", "correct": "B", "exp": "Fixtures provide reusable setup/teardown logic for test functions using the @pytest.fixture decorator."},
                            {"text": "Which command runs all tests in a directory with pytest?", "a": "python test", "b": "pytest", "c": "run tests", "d": "test --all", "correct": "B", "exp": "Running 'pytest' in the terminal auto-discovers and runs all test files and test functions."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "Python Logging & Debugging",
                        "description": "Master Python's logging module — log levels, formatters, handlers, structured logging, and production debugging strategies.",
                        "learning_objectives": "Configure the logging module with levels and formatters\nWrite logs to files and external services\nUse structured logging for production\nDebug with pdb and IDE debuggers",
                        "difficulty": "medium",
                        "estimated_time": 2.0,
                        "order": 3,
                        "videos": [
                            {"title": "Python Logging Tutorial", "url": "https://www.youtube.com/watch?v=jxmzY9soFXg"},
                            {"title": "Debugging Python with pdb", "url": "https://www.youtube.com/watch?v=aZJnGOwzHtU"}
                        ],
                        "docs": [
                            {"title": "Python Logging HOWTO", "url": "https://docs.python.org/3/howto/logging.html"},
                        ],
                        "quiz_questions": [
                            {"text": "What is the correct order of Python log levels from lowest to highest?", "a": "INFO, DEBUG, WARNING, ERROR, CRITICAL", "b": "DEBUG, INFO, WARNING, ERROR, CRITICAL", "c": "WARNING, INFO, DEBUG, ERROR, CRITICAL", "d": "ERROR, WARNING, INFO, DEBUG, CRITICAL", "correct": "B", "exp": "Python log levels: DEBUG (10) < INFO (20) < WARNING (30) < ERROR (40) < CRITICAL (50)."},
                            {"text": "Which method logs a warning-level message?", "a": "logging.info()", "b": "logging.warn()", "c": "logging.warning()", "d": "logging.alert()", "correct": "C", "exp": "logging.warning() logs a message at the WARNING level."},
                            {"text": "What is the default log level in Python's logging module?", "a": "DEBUG", "b": "INFO", "c": "WARNING", "d": "ERROR", "correct": "C", "exp": "The default log level is WARNING — only WARNING, ERROR, and CRITICAL messages are shown by default."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    }
                ]
            },
            # =============================================
            # MILESTONE 6: Deployment & DevOps
            # =============================================
            {
                "title": "Milestone 6: Deployment & DevOps Essentials",
                "description": "Deploy backend applications — Docker, CI/CD, cloud hosting, environment management, and production monitoring.",
                "order": 6,
                "topics": [
                    {
                        "title": "Docker & Containerization",
                        "description": "Learn Docker fundamentals — images, containers, Dockerfiles, docker-compose, and containerizing Python applications.",
                        "learning_objectives": "Write Dockerfiles for Python applications\nBuild and run Docker containers\nUse docker-compose for multi-service setups\nManage volumes and networking",
                        "difficulty": "medium",
                        "estimated_time": 3.5,
                        "order": 1,
                        "videos": [
                            {"title": "Docker Tutorial for Beginners - Full Course", "url": "https://www.youtube.com/watch?v=fqMOX6JJhGo"},
                            {"title": "Docker in 100 Seconds", "url": "https://www.youtube.com/watch?v=Gjnup-PuquQ"}
                        ],
                        "docs": [
                            {"title": "Docker Official Docs", "url": "https://docs.docker.com/get-started/"},
                            {"title": "Docker Compose Docs", "url": "https://docs.docker.com/compose/"}
                        ],
                        "quiz_questions": [
                            {"text": "What is a Docker container?", "a": "A virtual machine", "b": "A lightweight, isolated runtime environment for applications", "c": "A database server", "d": "A code editor", "correct": "B", "exp": "Containers are lightweight, portable, isolated environments that package an application with its dependencies."},
                            {"text": "Which file defines how to build a Docker image?", "a": "docker-compose.yml", "b": "Dockerfile", "c": "config.yml", "d": "image.json", "correct": "B", "exp": "A Dockerfile contains instructions (FROM, COPY, RUN, CMD) for building a Docker image."},
                            {"text": "Which command runs a Docker container from an image?", "a": "docker build", "b": "docker start", "c": "docker run", "d": "docker exec", "correct": "C", "exp": "'docker run' creates and starts a new container from a specified image."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "CI/CD Pipelines & GitHub Actions",
                        "description": "Set up continuous integration and deployment — GitHub Actions workflows, automated testing, and deployment pipelines.",
                        "learning_objectives": "Create GitHub Actions workflow files\nAutomate testing on push/pull requests\nBuild and deploy Docker images automatically\nManage secrets and environment variables",
                        "difficulty": "hard",
                        "estimated_time": 3.0,
                        "order": 2,
                        "videos": [
                            {"title": "GitHub Actions Tutorial", "url": "https://www.youtube.com/watch?v=R8_veQiYBjI"},
                            {"title": "CI/CD Pipeline Explained", "url": "https://www.youtube.com/watch?v=scEDHsr3APg"}
                        ],
                        "docs": [
                            {"title": "GitHub Actions Documentation", "url": "https://docs.github.com/en/actions"},
                        ],
                        "quiz_questions": [
                            {"text": "What does CI/CD stand for?", "a": "Code Integration / Code Deployment", "b": "Continuous Integration / Continuous Deployment", "c": "Central Infrastructure / Central Distribution", "d": "Cloud Integration / Cloud Delivery", "correct": "B", "exp": "CI/CD automates code integration, testing, and deployment for faster and more reliable releases."},
                            {"text": "Which file format do GitHub Actions workflows use?", "a": "JSON", "b": "TOML", "c": "YAML", "d": "XML", "correct": "C", "exp": "GitHub Actions workflows are defined in YAML files under .github/workflows/ directory."},
                            {"text": "What triggers a GitHub Actions workflow?", "a": "Manual only", "b": "Events like push, pull_request, schedule", "c": "Deployment commands", "d": "IDE plugins", "correct": "B", "exp": "Workflows are triggered by GitHub events: push, pull_request, schedule, release, or manual dispatch."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "Cloud Deployment & Production Best Practices",
                        "description": "Deploy to production — cloud platforms (AWS, Railway, Render), environment variables, SSL, monitoring, and scaling.",
                        "learning_objectives": "Deploy FastAPI apps to cloud platforms\nConfigure environment variables and secrets\nSet up SSL/HTTPS and custom domains\nImplement monitoring, health checks, and auto-scaling",
                        "difficulty": "hard",
                        "estimated_time": 3.5,
                        "order": 3,
                        "videos": [
                            {"title": "Deploy FastAPI to Production", "url": "https://www.youtube.com/watch?v=SgSnz7kW-Ko"},
                            {"title": "AWS for Beginners - Full Course", "url": "https://www.youtube.com/watch?v=k1RI5locZE4"}
                        ],
                        "docs": [
                            {"title": "FastAPI Deployment", "url": "https://fastapi.tiangolo.com/deployment/"},
                            {"title": "Render Deployment Guide", "url": "https://render.com/docs"}
                        ],
                        "quiz_questions": [
                            {"text": "Why should secrets never be hardcoded in source code?", "a": "It slows down the application", "b": "They can be exposed in version control and lead to security breaches", "c": "It causes syntax errors", "d": "It increases file size", "correct": "B", "exp": "Hardcoded secrets in Git repos can be leaked publicly — always use environment variables."},
                            {"text": "What does SSL/TLS provide for web applications?", "a": "Faster loading", "b": "Encrypted communication between client and server", "c": "Better SEO", "d": "Database optimization", "correct": "B", "exp": "SSL/TLS encrypts data in transit between the browser and server, preventing interception."},
                            {"text": "What is a health check endpoint used for?", "a": "User authentication", "b": "Monitoring service availability and readiness", "c": "Database backup", "d": "Logging errors", "correct": "B", "exp": "Health check endpoints (e.g., /health) allow monitoring systems to verify the service is running."},
                        ],
                        "challenges": [
                            {
                                "title": "Environment Config Parser",
                                "description": "Write a function that parses environment variable strings (KEY=VALUE format) into a dictionary.",
                                "difficulty": "easy",
                                "template_code": "def parse_env_vars(env_string):\n    # Parse a multi-line string of KEY=VALUE pairs\n    # Return a dictionary\n    # Skip empty lines and lines starting with #\n    pass",
                                "test_cases": json.dumps([
                                    {"function_name": "parse_env_vars", "args": ["DB_HOST=localhost\nDB_PORT=3306\nDB_NAME=mydb"], "expected": {"DB_HOST": "localhost", "DB_PORT": "3306", "DB_NAME": "mydb"}},
                                    {"function_name": "parse_env_vars", "args": ["# comment\nAPI_KEY=abc123\n\nDEBUG=true"], "expected": {"API_KEY": "abc123", "DEBUG": "true"}},
                                ]),
                                "score_points": 15
                            }
                        ],
                        "notes": "",
                        "cheat_sheet": ""
                    }
                ]
            }
        ]

        # ===================================================
        # INSERT ALL DATA
        # ===================================================
        for rm_data in roadmap_data:
            existing_rm = db.query(Roadmap).filter(
                Roadmap.career_id == career.id,
                Roadmap.title == rm_data["title"],
                Roadmap.is_deleted == False
            ).first()

            if existing_rm:
                print(f"  ⏭️  Roadmap already exists: {rm_data['title']}")
                roadmap = existing_rm
            else:
                roadmap = Roadmap(
                    career_id=career.id,
                    title=rm_data["title"],
                    description=rm_data["description"],
                    order=rm_data["order"],
                    is_deleted=False
                )
                db.add(roadmap)
                db.commit()
                db.refresh(roadmap)
                print(f"  ✅ Created Roadmap: {rm_data['title']} (ID: {roadmap.id})")

            for t_data in rm_data["topics"]:
                existing_topic = db.query(Topic).filter(
                    Topic.roadmap_id == roadmap.id,
                    Topic.title == t_data["title"],
                    Topic.is_deleted == False
                ).first()

                if existing_topic:
                    print(f"    ⏭️  Topic already exists: {t_data['title']}")
                    topic = existing_topic
                else:
                    topic = Topic(
                        roadmap_id=roadmap.id,
                        career_id=career.id,
                        title=t_data["title"],
                        description=t_data["description"],
                        learning_objectives=t_data.get("learning_objectives", ""),
                        difficulty=t_data.get("difficulty", "medium"),
                        estimated_time=t_data.get("estimated_time", 2.0),
                        order=t_data.get("order", 1),
                        notes=t_data.get("notes", ""),
                        cheat_sheet=t_data.get("cheat_sheet", ""),
                        youtube_videos=json.dumps(t_data.get("videos", [])),
                        official_documentation=json.dumps(t_data.get("docs", [])),
                        is_admin_modified=True,
                        is_deleted=False
                    )
                    db.add(topic)
                    db.commit()
                    db.refresh(topic)
                    print(f"    ✅ Created Topic: {t_data['title']} (ID: {topic.id})")

                # Insert Videos
                for idx, v_data in enumerate(t_data.get("videos", [])):
                    existing_vid = db.query(Video).filter(
                        Video.topic_id == topic.id,
                        Video.youtube_url == v_data["url"],
                        Video.is_deleted == False
                    ).first()
                    if not existing_vid:
                        vid = Video(
                            topic_id=topic.id,
                            roadmap_id=roadmap.id,
                            career_id=career.id,
                            title=v_data["title"],
                            youtube_url=v_data["url"],
                            display_order=idx + 1,
                            is_active=True,
                            is_deleted=False
                        )
                        db.add(vid)
                db.commit()

                # Insert Quiz + Questions
                quiz_qs = t_data.get("quiz_questions", [])
                if quiz_qs:
                    existing_quiz = db.query(Quiz).filter(
                        Quiz.topic_id == topic.id,
                        Quiz.is_deleted == False
                    ).first()
                    if not existing_quiz:
                        quiz = Quiz(
                            topic_id=topic.id,
                            title=f"{t_data['title']} Checkpoint Quiz",
                            passing_percentage=75,
                            is_admin_modified=True,
                            is_deleted=False
                        )
                        db.add(quiz)
                        db.commit()
                        db.refresh(quiz)
                        print(f"      ✅ Created Quiz (ID: {quiz.id}) with {len(quiz_qs)} questions")

                        for q_data in quiz_qs:
                            question = Question(
                                quiz_id=quiz.id,
                                question_text=q_data["text"],
                                option_a=q_data["a"],
                                option_b=q_data["b"],
                                option_c=q_data["c"],
                                option_d=q_data["d"],
                                correct_option=q_data["correct"],
                                explanation=q_data["exp"],
                                is_deleted=False
                            )
                            db.add(question)
                        db.commit()
                    else:
                        print(f"      ⏭️  Quiz already exists for: {t_data['title']}")

                # Insert Coding Challenges
                for ch_data in t_data.get("challenges", []):
                    existing_ch = db.query(CodingChallenge).filter(
                        CodingChallenge.topic_id == topic.id,
                        CodingChallenge.title == ch_data["title"],
                        CodingChallenge.is_deleted == False
                    ).first()
                    if not existing_ch:
                        challenge = CodingChallenge(
                            topic_id=topic.id,
                            title=ch_data["title"],
                            description=ch_data["description"],
                            difficulty=ch_data.get("difficulty", "medium"),
                            template_code=ch_data.get("template_code", ""),
                            test_cases=ch_data.get("test_cases", "[]"),
                            score_points=ch_data.get("score_points", 10),
                            is_deleted=False
                        )
                        db.add(challenge)
                        db.commit()
                        print(f"      ✅ Created Challenge: {ch_data['title']}")

                # Insert Resources
                for d_data in t_data.get("docs", []):
                    existing_res = db.query(Resource).filter(
                        Resource.topic_id == topic.id,
                        Resource.title == d_data["title"]
                    ).first()
                    if not existing_res:
                        res = Resource(
                            topic_id=topic.id,
                            type="doc",
                            title=d_data["title"],
                            url=d_data["url"],
                            content=f"Official documentation for {t_data['title']}"
                        )
                        db.add(res)
                db.commit()

        # Update career total topics count
        total = db.query(Topic).filter(Topic.career_id == career.id, Topic.is_deleted == False).count()
        career.total_topics = total
        db.commit()

        print(f"\n🎉 Backend Developer Roadmap seeded successfully!")
        print(f"   Career ID: {career.id}")
        print(f"   Total Milestones: {len(roadmap_data)}")
        print(f"   Total Topics: {total}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding roadmap: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
