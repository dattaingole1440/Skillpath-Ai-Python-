import json
import datetime
from sqlalchemy.orm import Session
from app.models.models import (
    User, Career, Roadmap, Topic, Quiz, Question, CodingChallenge,
    Certificate, StudentProgress, QuizAttempt, CodingSubmission,
    ActivityLog, Analytics, student_careers, College, Department,
    AcademicYear, Semester, Division, Subject, Assignment,
    AssignmentSubmission, AttendanceRecord, ActivityTrack, EarlyWarningAlert,
    TeacherNotification, PlacementRecord
)
from app.utils.security import get_password_hash

def get_topic_challenge_data(title, diff, career_name):
    """
    Generates a unique, topic-specific coding challenge for the student,
    matching the language/compilation rules of the active career path.
    """
    title_lower = title.lower()
    fn_name = title.lower().replace(" ", "_").replace("++", "pp").replace("+", "p").replace("-", "_")
    
    if career_name == "Java Developer":
        # JAVA GENERATION
        if "installation" in title_lower or "setup" in title_lower or "idea" in title_lower or "vs code" in title_lower:
            desc = f"<p>Write a Java static method <code>verify_{fn_name}_status()</code> inside the <code>Solution</code> class that returns the string <code>\"success\"</code>.</p>"
            tmpl = f"public class Solution {{\n    public static String verify_{fn_name}_status() {{\n        // Write your code here\n        return \"success\";\n    }}\n}}"
            cases = [{"function_name": f"verify_{fn_name}_status", "args": [], "expected": "success"}]
            points = 10
        elif "variables" in title_lower:
            desc = f"<p>Write a Java static method <code>initialize_variables(int a, String b)</code> inside the <code>Solution</code> class that returns the string <code>\"val1: \" + a + \", val2: \" + b</code>.</p>"
            tmpl = "public class Solution {\n    public static String initialize_variables(int a, String b) {\n        // Write your code here\n        return \"val1: \" + a + \", val2: \" + b;\n    }\n}"
            cases = [{"function_name": "initialize_variables", "args": [10, "hello"], "expected": "val1: 10, val2: hello"}]
            points = 10
        elif "data types" in title_lower:
            desc = f"<p>Write a Java static method <code>get_data_type_name(double val)</code> inside the <code>Solution</code> class that returns <code>\"double\"</code> if val has fractional parts, otherwise <code>\"integer\"</code>.</p>"
            tmpl = "public class Solution {\n    public static String get_data_type_name(double val) {\n        // Write your code here\n        return (val % 1 == 0) ? \"integer\" : \"double\";\n    }\n}"
            cases = [{"function_name": "get_data_type_name", "args": [45.5], "expected": "double"}]
            points = 10
        elif "operators" in title_lower:
            desc = f"<p>Write a Java static method <code>is_even_and_positive(int n)</code> inside the <code>Solution</code> class that returns <code>true</code> if positive and even, <code>false</code> otherwise.</p>"
            tmpl = "public class Solution {\n    public static boolean is_even_and_positive(int n) {\n        // Write your code here\n        return (n > 0 && n % 2 == 0);\n    }\n}"
            cases = [{"function_name": "is_even_and_positive", "args": [4], "expected": True}, {"function_name": "is_even_and_positive", "args": [-2], "expected": False}]
            points = 10
        elif "conditionals" in title_lower or "if else" in title_lower:
            desc = f"<p>Write a Java static method <code>get_ticket_price(int age)</code> inside the <code>Solution</code> class that returns <code>5</code> if age &lt; 12, <code>15</code> if age &gt;= 60, and <code>10</code> otherwise.</p>"
            tmpl = "public class Solution {\n    public static int get_ticket_price(int age) {\n        // Write your code here\n        return 0;\n    }\n}"
            cases = [{"function_name": "get_ticket_price", "args": [8], "expected": 5}, {"function_name": "get_ticket_price", "args": [25], "expected": 10}]
            points = 10
        elif "loops" in title_lower:
            desc = f"<p>Write a Java static method <code>sum_even_numbers(int n)</code> inside the <code>Solution</code> class that calculates the sum of all positive even integers up to and including <code>n</code>.</p>"
            tmpl = "public class Solution {\n    public static int sum_even_numbers(int n) {\n        // Write your code here\n        return 0;\n    }\n}"
            cases = [{"function_name": "sum_even_numbers", "args": [6], "expected": 12}]
            points = 10
        elif "methods" in title_lower or "functions" in title_lower:
            desc = f"<p>Write a Java static method <code>celsius_to_fahrenheit(double c)</code> inside the <code>Solution</code> class that converts Celsius to Fahrenheit using <code>(c * 9/5) + 32</code>.</p>"
            tmpl = "public class Solution {\n    public static double celsius_to_fahrenheit(double c) {\n        // Write your code here\n        return 0.0;\n    }\n}"
            cases = [{"function_name": "celsius_to_fahrenheit", "args": [100.0], "expected": 212.0}]
            points = 10
        elif "strings" in title_lower:
            desc = f"<p>Write a Java static method <code>reverse_string(String s)</code> inside the <code>Solution</code> class that returns the reversed string.</p>"
            tmpl = "public class Solution {\n    public static String reverse_string(String s) {\n        // Write your code here\n        return \"\";\n    }\n}"
            cases = [{"function_name": "reverse_string", "args": ["hello"], "expected": "olleh"}]
            points = 10
        elif "arrays" in title_lower or "lists" in title_lower:
            desc = f"<p>Write a Java static method <code>sum_array(int[] arr)</code> inside the <code>Solution</code> class that returns the sum of array values.</p>"
            tmpl = "public class Solution {\n    public static int sum_array(int[] arr) {\n        // Write your code here\n        return 0;\n    }\n}"
            cases = [{"function_name": "sum_array", "args": [[1, 2, 3, 4]], "expected": 10}]
            points = 10
        elif "collections" in title_lower:
            desc = f"<p>Write a Java static method <code>get_list_size(int n)</code> inside the <code>Solution</code> class that creates an ArrayList, adds integers from 1 to n, and returns its size.</p>"
            tmpl = "import java.util.ArrayList;\n\npublic class Solution {\n    public static int get_list_size(int n) {\n        // Write your code here\n        return 0;\n    }\n}"
            cases = [{"function_name": "get_list_size", "args": [5], "expected": 5}]
            points = 15
        elif "file" in title_lower:
            desc = f"<p>Write a Java static method <code>format_filename(String base, String ext)</code> inside the <code>Solution</code> class that returns <code>base + \".\" + ext</code>.</p>"
            tmpl = "public class Solution {\n    public static String format_filename(String base, String ext) {\n        // Write your code here\n        return \"\";\n    }\n}"
            cases = [{"function_name": "format_filename", "args": ["test", "java"], "expected": "test.java"}]
            points = 10
        elif "exception" in title_lower:
            desc = f"<p>Write a Java static method <code>safe_divide(int a, int b)</code> inside the <code>Solution</code> class that returns <code>a / b</code>, or returns <code>0</code> if b is 0 (catching ArithmeticException).</p>"
            tmpl = "public class Solution {\n    public static int safe_divide(int a, int b) {\n        // Write your code here\n        return 0;\n    }\n}"
            cases = [{"function_name": "safe_divide", "args": [10, 0], "expected": 0}]
            points = 10
        elif "oop" in title_lower or "object" in title_lower or "classes" in title_lower or "structures" in title_lower:
            desc = f"<p>Write a Java static method <code>create_instance_desc(String name, String role)</code> inside the <code>Solution</code> class that returns <code>\"Name: \" + name + \", Role: \" + role</code>.</p>"
            tmpl = "public class Solution {\n    public static String create_instance_desc(String name, String role) {\n        // Write your code here\n        return \"\";\n    }\n}"
            cases = [{"function_name": "create_instance_desc", "args": ["Jane", "Student"], "expected": "Name: Jane, Role: Student"}]
            points = 15
        else:
            desc = f"<p>Write a Java static method <code>simple_addition(int a, int b)</code> inside the <code>Solution</code> class that returns <code>a + b</code>.</p>"
            tmpl = "public class Solution {\n    public static int simple_addition(int a, int b) {\n        // Write your code here\n        return a + b;\n    }\n}"
            cases = [{"function_name": "simple_addition", "args": [4, 5], "expected": 9}]
            points = 20

    elif career_name == "C++ Developer":
        # C++ GENERATION
        if "installation" in title_lower or "setup" in title_lower or "idea" in title_lower or "vs code" in title_lower:
            desc = f"<p>Write a C++ function <code>verify_{fn_name}_status()</code> that returns the string <code>\"success\"</code>.</p>"
            tmpl = f"#include <string>\n\nstd::string verify_{fn_name}_status() {{\n    // Write your code here\n    return \"success\";\n}}"
            cases = [{"function_name": f"verify_{fn_name}_status", "args": [], "expected": "success"}]
            points = 10
        elif "variables" in title_lower:
            desc = f"<p>Write a C++ function <code>initialize_variables(int a, std::string b)</code> that returns the string <code>\"val1: \" + std::to_string(a) + \", val2: \" + b</code>.</p>"
            tmpl = "#include <string>\n\nstd::string initialize_variables(int a, std::string b) {\n    // Write your code here\n    return \"val1: \" + std::to_string(a) + \", val2: \" + b;\n}"
            cases = [{"function_name": "initialize_variables", "args": [10, "hello"], "expected": "val1: 10, val2: hello"}]
            points = 10
        elif "data types" in title_lower:
            desc = f"<p>Write a C++ function <code>get_data_type_name(float val)</code> that returns <code>\"float\"</code> if val has a fractional part, else <code>\"int\"</code>.</p>"
            tmpl = "#include <string>\n\nstd::string get_data_type_name(float val) {\n    // Write your code here\n    return \"\";\n}"
            cases = [{"function_name": "get_data_type_name", "args": [45.5], "expected": "float"}]
            points = 10
        elif "operators" in title_lower:
            desc = f"<p>Write a C++ function <code>is_even_and_positive(int n)</code> that returns <code>true</code> if positive and even, <code>false</code> otherwise.</p>"
            tmpl = "bool is_even_and_positive(int n) {\n    // Write your code here\n    return (n > 0 && n % 2 == 0);\n}"
            cases = [{"function_name": "is_even_and_positive", "args": [4], "expected": True}, {"function_name": "is_even_and_positive", "args": [-2], "expected": False}]
            points = 10
        elif "conditionals" in title_lower or "if else" in title_lower:
            desc = f"<p>Write a C++ function <code>get_ticket_price(int age)</code> that returns <code>5</code> if age &lt; 12, <code>15</code> if age &gt;= 60, and <code>10</code> otherwise.</p>"
            tmpl = "int get_ticket_price(int age) {\n    // Write your code here\n    return 0;\n}"
            cases = [{"function_name": "get_ticket_price", "args": [8], "expected": 5}, {"function_name": "get_ticket_price", "args": [25], "expected": 10}]
            points = 10
        elif "loops" in title_lower:
            desc = f"<p>Write a C++ function <code>sum_even_numbers(int n)</code> that calculates the sum of all positive even integers up to and including <code>n</code>.</p>"
            tmpl = "int sum_even_numbers(int n) {\n    // Write your code here\n    return 0;\n}"
            cases = [{"function_name": "sum_even_numbers", "args": [6], "expected": 12}]
            points = 10
        elif "functions" in title_lower or "methods" in title_lower:
            desc = f"<p>Write a C++ function <code>celsius_to_fahrenheit(double c)</code> that converts Celsius to Fahrenheit using <code>(c * 9/5) + 32</code>.</p>"
            tmpl = "double celsius_to_fahrenheit(double c) {\n    // Write your code here\n    return 0.0;\n}"
            cases = [{"function_name": "celsius_to_fahrenheit", "args": [100.0], "expected": 212.0}]
            points = 10
        elif "strings" in title_lower:
            desc = f"<p>Write a C++ function <code>reverse_string(std::string s)</code> that returns the reversed string.</p>"
            tmpl = "#include <string>\n#include <algorithm>\n\nstd::string reverse_string(std::string s) {\n    // Write your code here\n    return \"\";\n}"
            cases = [{"function_name": "reverse_string", "args": ["hello"], "expected": "olleh"}]
            points = 10
        elif "pointers" in title_lower:
            desc = f"<p>Write a C++ function <code>double_val(int* ptr)</code> that doubles the value pointed to by <code>ptr</code> and returns it.</p>"
            tmpl = "int double_val(int* ptr) {\n    // Write your code here\n    return 0;\n}"
            cases = [{"function_name": "double_val", "args": [21], "expected": 42}]
            points = 15
        else:
            desc = f"<p>Write a C++ function <code>simple_addition(int a, int b)</code> that returns <code>a + b</code>.</p>"
            tmpl = "int simple_addition(int a, int b) {\n    // Write your code here\n    return a + b;\n}"
            cases = [{"function_name": "simple_addition", "args": [4, 5], "expected": 9}]
            points = 20

    else:
        # PYTHON GENERATION (default)
        if "installation" in title_lower or "setup" in title_lower or "idea" in title_lower or "vs code" in title_lower:
            desc = f"<p>Write a function <code>verify_{fn_name}_status()</code> that returns the string <code>'success'</code>, indicating the setup verification check passed.</p>"
            tmpl = f"def verify_{fn_name}_status():\n    # Write your code here\n    pass"
            cases = [{"function_name": f"verify_{fn_name}_status", "args": [], "expected": "success"}]
            points = 10
        elif "variables" in title_lower:
            desc = f"<p>Write a function <code>initialize_variables(a, b)</code> that stores inputs in a dictionary <code>{{'val1': a, 'val2': b}}</code> and returns it.</p>"
            tmpl = "def initialize_variables(a, b):\n    # Write your code here\n    pass"
            cases = [{"function_name": "initialize_variables", "args": [10, "hello"], "expected": {"val1": 10, "val2": "hello"}}]
            points = 10
        elif "data types" in title_lower:
            desc = f"<p>Write a function <code>get_data_type_name(val)</code> that returns the class type of the value as a string (e.g. <code>'int'</code>, <code>'str'</code>, <code>'float'</code>, <code>'list'</code>).</p>"
            tmpl = "def get_data_type_name(val):\n    # Write your code here\n    pass"
            cases = [
                {"function_name": "get_data_type_name", "args": [45], "expected": "int"},
                {"function_name": "get_data_type_name", "args": ["hi"], "expected": "str"}
            ]
            points = 10
        elif "operators" in title_lower:
            desc = f"<p>Write a function <code>is_even_and_positive(n)</code> that returns <code>True</code> if the integer <code>n</code> is positive and even, <code>False</code> otherwise.</p>"
            tmpl = "def is_even_and_positive(n):\n    # Write your code here\n    pass"
            cases = [
                {"function_name": "is_even_and_positive", "args": [4], "expected": True},
                {"function_name": "is_even_and_positive", "args": [-2], "expected": False}
            ]
            points = 10
        elif "input output" in title_lower or "streams" in title_lower:
            desc = f"<p>Write a function <code>format_greeting(name, age)</code> that returns <code>'Hello ' + name + ', age ' + str(age)</code>.</p>"
            tmpl = "def format_greeting(name, age):\n    # Write your code here\n    pass"
            cases = [{"function_name": "format_greeting", "args": ["Jane", 20], "expected": "Hello Jane, age 20"}]
            points = 10
        elif "conditional" in title_lower or "if else" in title_lower:
            desc = f"<p>Write a function <code>get_ticket_price(age)</code> that returns <code>5</code> if age &lt; 12, <code>15</code> if age &gt;= 60, and <code>10</code> otherwise.</p>"
            tmpl = "def get_ticket_price(age):\n    # Write your code here\n    pass"
            cases = [
                {"function_name": "get_ticket_price", "args": [8], "expected": 5},
                {"function_name": "get_ticket_price", "args": [65], "expected": 15},
                {"function_name": "get_ticket_price", "args": [25], "expected": 10}
            ]
            points = 10
        elif "loops" in title_lower:
            desc = f"<p>Write a function <code>sum_even_numbers(n)</code> that calculates the sum of all positive even integers up to and including <code>n</code>.</p>"
            tmpl = "def sum_even_numbers(n):\n    # Write your code here\n    pass"
            cases = [{"function_name": "sum_even_numbers", "args": [6], "expected": 12}]
            points = 10
        elif "functions" in title_lower or "methods" in title_lower:
            desc = f"<p>Write a function <code>celsius_to_fahrenheit(c)</code> that converts temperature from Celsius to Fahrenheit using <code>(c * 9/5) + 32</code>.</p>"
            tmpl = "def celsius_to_fahrenheit(c):\n    # Write your code here\n    pass"
            cases = [
                {"function_name": "celsius_to_fahrenheit", "args": [0], "expected": 32.0},
                {"function_name": "celsius_to_fahrenheit", "args": [100], "expected": 212.0}
            ]
            points = 10
        elif "strings" in title_lower:
            desc = f"<p>Write a function <code>is_palindrome(s)</code> that returns <code>True</code> if the string (ignoring case) is a palindrome, <code>False</code> otherwise.</p>"
            tmpl = "def is_palindrome(s):\n    # Write your code here\n    pass"
            cases = [
                {"function_name": "is_palindrome", "args": ["Racecar"], "expected": True},
                {"function_name": "is_palindrome", "args": ["hello"], "expected": False}
            ]
            points = 10
        elif "lists" in title_lower or "arrays" in title_lower:
            desc = f"<p>Write a function <code>find_min_max(arr)</code> that takes a list of numbers and returns a list <code>[min_val, max_val]</code>.</p>"
            tmpl = "def find_min_max(arr):\n    # Write your code here\n    pass"
            cases = [{"function_name": "find_min_max", "args": [[4, 2, 9, 1, 7]], "expected": [1, 9]}]
            points = 10
        elif "tuples" in title_lower:
            desc = f"<p>Write a function <code>swap_tuple_elements(tup)</code> that takes a 2-element tuple and returns a new list with the elements swapped.</p>"
            tmpl = "def swap_tuple_elements(tup):\n    # Write your code here\n    pass"
            cases = [{"function_name": "swap_tuple_elements", "args": [(1, 2)], "expected": [2, 1]}]
            points = 10
        elif "sets" in title_lower:
            desc = f"<p>Write a function <code>get_set_union_intersection(lst1, lst2)</code> that returns a dictionary with the count of elements in the union and the intersection of the two lists: <code>{{'union_count': u, 'intersection_count': i}}</code>.</p>"
            tmpl = "def get_set_union_intersection(lst1, lst2):\n    # Write your code here\n    pass"
            cases = [{"function_name": "get_set_union_intersection", "args": [[1, 2, 3], [3, 4]], "expected": {"union_count": 4, "intersection_count": 1}}]
            points = 10
        elif "dictionary" in title_lower or "collections" in title_lower:
            desc = f"<p>Write a function <code>get_frequency_map(items)</code> that returns a dictionary mapping each unique item in the list to its count.</p>"
            tmpl = "def get_frequency_map(items):\n    # Write your code here\n    pass"
            cases = [{"function_name": "get_frequency_map", "args": [["apple", "banana", "apple"]], "expected": {"apple": 2, "banana": 1}}]
            points = 10
        elif "file" in title_lower:
            desc = f"<p>Write a function <code>get_filename_details(path)</code> that extracts the basename and extension from a path string, returning a list <code>[basename, ext]</code>. E.g. <code>'data.csv' -> ['data', '.csv']</code>.</p>"
            tmpl = "def get_filename_details(path):\n    # Write your code here\n    pass"
            cases = [{"function_name": "get_filename_details", "args": ["script.py"], "expected": ["script", ".py"]}]
            points = 10
        elif "exception" in title_lower:
            desc = f"<p>Write a function <code>safe_to_int(val)</code> that returns the integer conversion of <code>val</code> if valid, and <code>None</code> if a ValueError is raised.</p>"
            tmpl = "def safe_to_int(val):\n    # Write your code here\n    pass"
            cases = [
                {"function_name": "safe_to_int", "args": ["123"], "expected": 123},
                {"function_name": "safe_to_int", "args": ["abc"], "expected": None}
            ]
            points = 10
        elif "oop" in title_lower or "object" in title_lower or "classes" in title_lower or "structures" in title_lower:
            desc = f"<p>Write a function <code>create_instance_dict(name, role)</code> that simulates a Class object representation, returning a dictionary: <code>{{'name': name, 'role': role, 'active': True}}</code>.</p>"
            tmpl = "def create_instance_dict(name, role):\n    # Write your code here\n    pass"
            cases = [{"function_name": "create_instance_dict", "args": ["Jane", "Student"], "expected": {"name": "Jane", "role": "Student", "active": True}}]
            points = 15
        elif "environment" in title_lower or "modules" in title_lower or "packages" in title_lower or "maven" in title_lower or "templates" in title_lower:
            desc = f"<p>Write a function <code>get_package_path(module, pkg)</code> that formats the import path as <code>module + '.' + pkg</code>.</p>"
            tmpl = "def get_package_path(module, pkg):\n    # Write your code here\n    pass"
            cases = [{"function_name": "get_package_path", "args": ["os", "path"], "expected": "os.path"}]
            points = 10
        elif "mysql" in title_lower or "database" in title_lower or "jdbc" in title_lower or "hibernate" in title_lower or "sqlalchemy" in title_lower:
            desc = f"<p>Write a function <code>generate_sql_select(table, key, val)</code> that returns a query string matching: <code>'SELECT * FROM ' + table + ' WHERE ' + key + ' = \\'' + str(val) + '\\''</code>.</p>"
            tmpl = "def generate_sql_select(table, key, val):\n    # Write your code here\n    pass"
            cases = [{"function_name": "generate_sql_select", "args": ["users", "id", 42], "expected": "SELECT * FROM users WHERE id = '42'"}]
            points = 15
        elif "numpy" in title_lower or "pandas" in title_lower or "matplotlib" in title_lower or "stl" in title_lower:
            desc = f"<p>Write a function <code>calculate_array_mean(arr)</code> that takes a list of integers and returns their average as a float.</p>"
            tmpl = "def calculate_array_mean(arr):\n    # Write your code here\n    pass"
            cases = [{"function_name": "calculate_array_mean", "args": [[1, 2, 3, 4]], "expected": 2.5}]
            points = 15
        elif "flask" in title_lower or "fastapi" in title_lower or "rest" in title_lower or "spring" in title_lower:
            desc = f"<p>Write a function <code>create_api_response(status, payload)</code> that returns a standard dictionary: <code>{{'status': status, 'payload': payload, 'timestamp': '2026'}}</code>.</p>"
            tmpl = "def create_api_response(status, payload):\n    # Write your code here\n    pass"
            cases = [{"function_name": "create_api_response", "args": ["success", {"id": 1}], "expected": {"status": "success", "payload": {"id": 1}, "timestamp": "2026"}}]
            points = 15
        elif "jwt" in title_lower or "security" in title_lower or "auth" in title_lower:
            desc = f"<p>Write a function <code>verify_token_format(auth_header)</code> that returns <code>True</code> if the header string is a valid Bearer token structure (starts with <code>'Bearer '</code> and length &gt; 15), <code>False</code> otherwise.</p>"
            tmpl = "def verify_token_format(auth_header):\n    # Write your code here\n    pass"
            cases = [
                {"function_name": "verify_token_format", "args": ["Bearer xyz123abc456"], "expected": False},
                {"function_name": "verify_token_format", "args": ["Bearer securetokenxyz123abc456"], "expected": True}
            ]
            points = 15
        elif "docker" in title_lower or "cloud" in title_lower or "devops" in title_lower:
            desc = f"<p>Write a function <code>configure_port_mapping(host_port, container_port)</code> that returns a port mapping string matching: <code>str(host_port) + ':' + str(container_port)</code>.</p>"
            tmpl = "def configure_port_mapping(host_port, container_port):\n    # Write your code here\n    pass"
            cases = [{"function_name": "configure_port_mapping", "args": [8000, 80], "expected": "8000:80"}]
            points = 15
        elif "git" in title_lower or "github" in title_lower:
            desc = f"<p>Write a function <code>format_git_commit(branch, message)</code> that returns a formatted commit status string: <code>'[' + branch + '] ' + message</code>.</p>"
            tmpl = "def format_git_commit(branch, message):\n    # Write your code here\n    pass"
            cases = [{"function_name": "format_git_commit", "args": ["main", "Initial commit"], "expected": "[main] Initial commit"}]
            points = 10
        elif "pointers" in title_lower or "memory" in title_lower or "references" in title_lower:
            desc = f"<p>Write a function <code>double_referenced_value(val)</code> that returns the double of the input value <code>val * 2</code>. This simulates referencing and doubling.</p>"
            tmpl = "def double_referenced_value(val):\n    # Write your code here\n    pass"
            cases = [{"function_name": "double_referenced_value", "args": [21], "expected": 42}]
            points = 15
        elif "structures" in title_lower or "algorithms" in title_lower or "programming" in title_lower or "multithreading" in title_lower:
            desc = f"<p>Write a function <code>find_target_index(arr, target)</code> that searches the list for a target value and returns its 0-indexed position, or <code>-1</code> if not found.</p>"
            tmpl = "def find_target_index(arr, target):\n    # Write your code here\n    pass"
            cases = [
                {"function_name": "find_target_index", "args": [[10, 20, 30, 40], 30], "expected": 2},
                {"function_name": "find_target_index", "args": [[10, 20, 30], 50], "expected": -1}
            ]
            points = 15
        else:
            desc = f"<p>Write a function <code>fizzbuzz_simple(n)</code> that returns <code>'Fizz'</code> if n is divisible by 3, <code>'Buzz'</code> if divisible by 5, <code>'FizzBuzz'</code> if divisible by both 3 and 5, and the string of the number otherwise.</p>"
            tmpl = "def fizzbuzz_simple(n):\n    # Write your code here\n    pass"
            cases = [
                {"function_name": "fizzbuzz_simple", "args": [15], "expected": "FizzBuzz"},
                {"function_name": "fizzbuzz_simple", "args": [9], "expected": "Fizz"},
                {"function_name": "fizzbuzz_simple", "args": [4], "expected": "4"}
            ]
            points = 20

    return {
        "description": desc,
        "template_code": tmpl,
        "test_cases": json.dumps(cases),
        "score_points": points
    }

def get_topic_video_data(title, career_name):
    """
    Returns realistic, high-quality, topic-specific YouTube tutorial reference video(s).
    """
    title_lower = title.lower().strip()
    
    python_videos_map = {
        "python installation": ("Python Installation & VS Code Setup - CodeWithHarry", "https://www.youtube.com/watch?v=dYfM6JwICnU"),
        "vs code setup": ("VS Code Configuration Guide - CodeWithHarry", "https://www.youtube.com/watch?v=M576z3Uo870"),
        "variables": ("Python Variables and Rules - CodeWithHarry", "https://www.youtube.com/watch?v=vLqTf2b6GZw"),
        "data types": ("Python Primitives and Dynamic Typing - CodeWithHarry", "https://www.youtube.com/watch?v=gCCV6GCOkyU"),
        "operators": ("Python Arithmetic and Logical Operators - CodeWithHarry", "https://www.youtube.com/watch?v=vLqTf2b6GZw"),
        "input output": ("Python Standard IO & formatting - CodeWithHarry", "https://www.youtube.com/watch?v=vLqTf2b6GZw"),
        "conditional statements": ("Python Conditional if-elif-else - CodeWithHarry", "https://www.youtube.com/watch?v=AWek49wXGzI"),
        "loops": ("Python for & while iteration loops - CodeWithHarry", "https://www.youtube.com/watch?v=6iF8Xb7Z3kQ"),
        "functions": ("Python Functions & Scope Parameters - CodeWithHarry", "https://www.youtube.com/watch?v=84G2yZqS_pE"),
        "strings": ("Python String Methods and Slicing - CodeWithHarry", "https://www.youtube.com/watch?v=vLqTf2b6GZw"),
        "lists": ("Python Lists sequences - CodeWithHarry", "https://www.youtube.com/watch?v=8M6A4kAQ5bA"),
        "tuples": ("Python Tuples immutability - CodeWithHarry", "https://www.youtube.com/watch?v=8M6A4kAQ5bA"),
        "sets": ("Python Sets uniques hashing - CodeWithHarry", "https://www.youtube.com/watch?v=8M6A4kAQ5bA"),
        "dictionary": ("Python Dictionaries keys value lookups - CodeWithHarry", "https://www.youtube.com/watch?v=8M6A4kAQ5bA"),
        "file handling": ("Python Reading & Writing Files - CodeWithHarry", "https://www.youtube.com/watch?v=u51ZjZ2pL1E"),
        "exception handling": ("Python Try-Except exceptions logic - CodeWithHarry", "https://www.youtube.com/watch?v=6iF8Xb7Z3kQ"),
        "modules": ("Python Builtin & Custom Modules - CodeWithHarry", "https://www.youtube.com/watch?v=6iF8Xb7Z3kQ"),
        "packages": ("Python Package namespaces imports - CodeWithHarry", "https://www.youtube.com/watch?v=6iF8Xb7Z3kQ"),
        "object oriented programming": ("Python OOPs Complete Class Guide - Corey Schafer", "https://www.youtube.com/watch?v=JeznW_7DlB0"),
        "virtual environment": ("Python virtualenv isolated builds - Corey Schafer", "https://www.youtube.com/watch?v=N5vscPTWKOk"),
        "mysql with python": ("Python DB Connections & MySQL - Programming with Mosh", "https://www.youtube.com/watch?v=HXV3zeQKqGY"),
        "numpy": ("Python NumPy Arrays & Vectors - freeCodeCamp", "https://www.youtube.com/watch?v=QUT1VHiLgKQ"),
        "pandas": ("Python Pandas Data Analysis Tutorial - Keith Galli", "https://www.youtube.com/watch?v=vmEHCJof1kU"),
        "matplotlib": ("Python Matplotlib Plotting Charts - Corey Schafer", "https://www.youtube.com/watch?v=DAQNHzOcO5A"),
        "flask": ("Python Flask Web App Framework - Corey Schafer", "https://www.youtube.com/watch?v=Z1RJmh_OqeA"),
        "fastapi": ("FastAPI Complete Rest API Crash Course - freeCodeCamp", "https://www.youtube.com/watch?v=tLKKmouUams"),
        "rest api": ("RESTful API Web Design Standards - Traversy Media", "https://www.youtube.com/watch?v=qbLc5a95X-Y"),
        "jwt authentication": ("JWT JSON Web Token Authentication - freeCodeCamp", "https://www.youtube.com/watch?v=7Q17ubqLfaM"),
        "sqlalchemy": ("SQLAlchemy Object Relational Mapper Tutorial - CodingWithMitch", "https://www.youtube.com/watch?v=wqKQ81jVx28"),
        "docker": ("Docker Containers Complete Crash Course - Programming with Mosh", "https://www.youtube.com/watch?v=pTFZFxd4hOI"),
        "git": ("Git Version Control Complete Crash Course - Traversy Media", "https://www.youtube.com/watch?v=RGOj5yH7evk"),
        "github": ("GitHub Collaborations & Repo Release - Traversy Media", "https://www.youtube.com/watch?v=RGOj5yH7evk"),
        "final python project": ("Full Python Projects Portfolio Build - freeCodeCamp", "https://www.youtube.com/watch?v=8Ext9G7xspg"),
        "interview preparation": ("Python Developer Coding Interview Prep - freeCodeCamp", "https://www.youtube.com/watch?v=7uM1u02J-gU")
    }

    java_videos_map = {
        "java installation": ("Java JDK Installation & Path Setup - Telusko", "https://www.youtube.com/watch?v=yRpLlJmRo2w"),
        "intellij idea": ("IntelliJ IDEA Installation & Run - Telusko", "https://www.youtube.com/watch?v=yRpLlJmRo2w"),
        "variables": ("Java Variables declarations rules - Telusko", "https://www.youtube.com/watch?v=A74TOX803D0"),
        "data types": ("Java Primitives & Non-Primitives - Telusko", "https://www.youtube.com/watch?v=A74TOX803D0"),
        "operators": ("Java Logic Arithmetic Operators - Telusko", "https://www.youtube.com/watch?v=A74TOX803D0"),
        "if else": ("Java Conditional If Else statements - Apna College", "https://www.youtube.com/watch?v=O82Lhth7p04"),
        "loops": ("Java For, While & Do-While loops - Apna College", "https://www.youtube.com/watch?v=O82Lhth7p04"),
        "methods": ("Java Methods syntax & arguments - Telusko", "https://www.youtube.com/watch?v=A74TOX803D0"),
        "arrays": ("Java 1D and Multi-Dimensional Arrays - Telusko", "https://www.youtube.com/watch?v=2d9s-WfSntk"),
        "strings": ("Java String Pool and Methods - Telusko", "https://www.youtube.com/watch?v=2d9s-WfSntk"),
        "oop": ("Java Object Oriented Programming (OOP) - Apna College", "https://www.youtube.com/watch?v=aPArx50V5r8"),
        "exception handling": ("Java Try-Catch exception throwables - Telusko", "https://www.youtube.com/watch?v=A74TOX803D0"),
        "collections": ("Java Collections ArrayList HashSet HashMap - Apna College", "https://www.youtube.com/watch?v=2d9s-WfSntk"),
        "multithreading": ("Java Multithreading & Synchronization - Telusko", "https://www.youtube.com/watch?v=A74TOX803D0"),
        "file handling": ("Java File Reading & Writing streams - Telusko", "https://www.youtube.com/watch?v=A74TOX803D0"),
        "jdbc": ("Java Database Connectivity (JDBC) - Telusko", "https://www.youtube.com/watch?v=A74TOX803D0"),
        "maven": ("Maven Dependency Management & Builds - Telusko", "https://www.youtube.com/watch?v=A74TOX803D0"),
        "spring boot": ("Spring Boot Starter Complete Tutorial - Amigoscode", "https://www.youtube.com/watch?v=9SGDpanrc8U"),
        "rest api": ("Spring Boot Rest Controllers design - Amigoscode", "https://www.youtube.com/watch?v=9SGDpanrc8U"),
        "hibernate": ("Hibernate & JPA Java ORM Complete Guide - Telusko", "https://www.youtube.com/watch?v=JR7-EdxDSf0"),
        "spring security": ("Spring Security Auth & JWT Setup - Telusko", "https://www.youtube.com/watch?v=her_7pa0vyg"),
        "mysql": ("MySQL Databases tables querying - Programming with Mosh", "https://www.youtube.com/watch?v=HXV3zeQKqGY"),
        "docker": ("Docker Containers for Spring Boot - Programming with Mosh", "https://www.youtube.com/watch?v=pTFZFxd4hOI"),
        "git": ("Git Version Control complete walkthrough - Traversy Media", "https://www.youtube.com/watch?v=RGOj5yH7evk"),
        "github": ("GitHub remote repos collaboration - Traversy Media", "https://www.youtube.com/watch?v=RGOj5yH7evk"),
        "final java project": ("Java Spring Boot Full Capstone Project - Amigoscode", "https://www.youtube.com/watch?v=9SGDpanrc8U"),
        "interview preparation": ("Java Coding Interview QA & Algorithms - freeCodeCamp", "https://www.youtube.com/watch?v=B31LgI4Y4DQ")
    }

    cpp_videos_map = {
        "c++ installation": ("C++ Compiler GCC MinGW Installation - The Cherno", "https://www.youtube.com/watch?v=18c3MTX0PK0"),
        "ide setup": ("C++ IDE Setup Visual Studio Code - The Cherno", "https://www.youtube.com/watch?v=18c3MTX0PK0"),
        "variables": ("C++ Variables initialization - The Cherno", "https://www.youtube.com/watch?v=18c3MTX0PK0"),
        "data types": ("C++ Primitive Data types - The Cherno", "https://www.youtube.com/watch?v=18c3MTX0PK0"),
        "operators": ("C++ Operators - The Cherno", "https://www.youtube.com/watch?v=18c3MTX0PK0"),
        "input output": ("C++ cout cin Streams console - The Cherno", "https://www.youtube.com/watch?v=18c3MTX0PK0"),
        "if else": ("C++ Conditional Branching statements - Apna College", "https://www.youtube.com/watch?v=z9bZufPHFLU"),
        "loops": ("C++ Loops For and While logic - Apna College", "https://www.youtube.com/watch?v=z9bZufPHFLU"),
        "functions": ("C++ Custom functions arguments - The Cherno", "https://www.youtube.com/watch?v=18c3MTX0PK0"),
        "arrays": ("C++ Contiguous arrays memory - Apna College", "https://www.youtube.com/watch?v=z9bZufPHFLU"),
        "strings": ("C++ std::string class methods - The Cherno", "https://www.youtube.com/watch?v=18c3MTX0PK0"),
        "pointers": ("C++ Memory Pointers & Dereferencing - The Cherno", "https://www.youtube.com/watch?v=IUtMCZskn8o"),
        "structures": ("C++ structs vs classes - The Cherno", "https://www.youtube.com/watch?v=18c3MTX0PK0"),
        "oop": ("C++ Object Oriented Classes Inheritance - The Cherno", "https://www.youtube.com/watch?v=wN0x9eLVM9g"),
        "templates": ("C++ Templates programming - The Cherno", "https://www.youtube.com/watch?v=IUtMCZskn8o"),
        "stl": ("C++ Standard Template Library Containers - Luv", "https://www.youtube.com/watch?v=g-1Cn35wUx4"),
        "file handling": ("C++ File Stream fstream reading - Luv", "https://www.youtube.com/watch?v=g-1Cn35wUx4"),
        "dynamic memory": ("C++ stack vs heap allocations - The Cherno", "https://www.youtube.com/watch?v=18c3MTX0PK0"),
        "data structures": ("C++ Data Structures Trees & Graphs - freeCodeCamp", "https://www.youtube.com/watch?v=B31LgI4Y4DQ"),
        "algorithms": ("C++ Algorithms Bubble Quick Sort - freeCodeCamp", "https://www.youtube.com/watch?v=B31LgI4Y4DQ"),
        "competitive programming": ("Competitive Programming C++ setups - Luv", "https://www.youtube.com/watch?v=g-1Cn35wUx4"),
        "git": ("Git version control complete course - Traversy Media", "https://www.youtube.com/watch?v=RGOj5yH7evk"),
        "github": ("GitHub online repositories guide - Traversy Media", "https://www.youtube.com/watch?v=RGOj5yH7evk"),
        "final c++ project": ("C++ Game Project Development - The Cherno", "https://www.youtube.com/watch?v=18c3MTX0PK0"),
        "interview preparation": ("C++ Interview QA Coding challenges - freeCodeCamp", "https://www.youtube.com/watch?v=7uM1u02J-gU")
    }

    if career_name == "Python Developer" and title_lower in python_videos_map:
        title_str, url_str = python_videos_map[title_lower]
        return [{"title": title_str, "url": url_str}]
    elif career_name == "Java Developer" and title_lower in java_videos_map:
        title_str, url_str = java_videos_map[title_lower]
        return [{"title": title_str, "url": url_str}]
    elif career_name == "C++ Developer" and title_lower in cpp_videos_map:
        title_str, url_str = cpp_videos_map[title_lower]
        return [{"title": title_str, "url": url_str}]
    
    # Generic distinct fallbacks based on career path to make videos unique
    if career_name == "Python Developer":
        return [{"title": f"Python {title} Tutorial - CodeWithHarry", "url": "https://www.youtube.com/watch?v=vLqTf2b6GZw"}]
    elif career_name == "Java Developer":
        return [{"title": f"Java {title} Course - Telusko", "url": "https://www.youtube.com/watch?v=A74TOX803D0"}]
    elif career_name == "C++ Developer":
        return [{"title": f"C++ {title} Tutorial - The Cherno", "url": "https://www.youtube.com/watch?v=18c3MTX0PK0"}]
    else:
        return [{"title": f"{title} Learning Tutorial", "url": "https://www.youtube.com/watch?v=vLqTf2b6GZw"}]

def seed_database(db: Session, force: bool = False):
    """
    Safely seeds initial career pathways, roadmaps, topics, quizzes, and coding
    challenges ONLY when the database is genuinely empty.
    Never deletes or overwrites existing user progress, custom roadmaps, videos, or configurations.
    """
    # 1. Non-destructive safety check: preserve existing data permanently
    if not force:
        try:
            user_count = db.query(User).count()
            career_count = db.query(Career).count()
            if user_count > 0 or career_count > 0:
                roadmap_count = db.query(Roadmap).count()
                topic_count = db.query(Topic).count()
                print(f"[DATABASE] Existing data preserved: {user_count} Users, {career_count} Careers, {roadmap_count} Roadmaps, {topic_count} Topics.")
                print("[STARTUP] No destructive initialization performed.")
                return
        except Exception as e:
            print(f"[DATABASE SAFETY WARNING] Could not verify database record count: {e}")
            print("[DATABASE SAFETY] Aborting database seeding to protect existing application state.")
            return

    print("[DATABASE] Database is genuinely empty. Performing safe initial setup without deleting records...")

    # 2. Seed Colleges & Organization Hierarchy
    c1 = College(name="Apex Institute of Technology", code="AIT", contact_email="contact@apex.edu", address="100 Innovation Park, Tech Valley")
    c2 = College(name="Metropolitan Engineering College", code="MEC", contact_email="info@metropolitan.edu", address="45 Campus Drive, City Center")
    db.add_all([c1, c2])
    db.commit()
    db.refresh(c1)
    db.refresh(c2)

    d1 = Department(college_id=c1.id, name="Computer Science & Engineering", code="CSE")
    d2 = Department(college_id=c1.id, name="Information Technology", code="IT")
    d3 = Department(college_id=c1.id, name="Artificial Intelligence & Data Science", code="AIDS")
    db.add_all([d1, d2, d3])
    db.commit()
    db.refresh(d1)

    s1 = Semester(department_id=d1.id, number=5, name="Semester 5")
    s2 = Semester(department_id=d1.id, number=6, name="Semester 6")
    db.add_all([s1, s2])
    db.commit()
    db.refresh(s1)

    div1 = Division(semester_id=s1.id, name="Division A")
    div2 = Division(semester_id=s1.id, name="Division B")
    db.add_all([div1, div2])
    db.commit()
    db.refresh(div1)

    # Seed Default User Accounts for all 5 roles
    super_admin = User(
        name="Super Admin",
        email="superadmin@skillpath.ai",
        password_hash=get_password_hash("Admin@123"),
        role="super_admin",
        college_id=c1.id,
        phone_number="+1-555-0100"
    )
    principal_user = User(
        name="Dr. Robert Vance (Principal)",
        email="principal@skillpath.ai",
        password_hash=get_password_hash("Principal@123"),
        role="principal",
        college_id=c1.id,
        employee_id="PRIN-1001",
        phone_number="+1-555-0199"
    )
    hod_user = User(
        name="Dr. HOD Computer Science",
        email="hod@skillpath.ai",
        password_hash=get_password_hash("Hod@123"),
        role="hod",
        college_id=c1.id,
        department_id=d1.id,
        employee_id="HOD-1001",
        phone_number="+1-555-0101"
    )
    teacher_user = User(
        name="Prof. Alan Turing",
        email="teacher@skillpath.ai",
        password_hash=get_password_hash("Teacher@123"),
        role="teacher",
        college_id=c1.id,
        department_id=d1.id,
        employee_id="TCH-2001",
        phone_number="+1-555-0102"
    )
    student_user = User(
        name="Jane Student",
        email="student@skillpath.ai",
        password_hash=get_password_hash("Student@123"),
        role="student",
        college_id=c1.id,
        department_id=d1.id,
        semester_id=s1.id,
        division_id=div1.id,
        roll_number="CS-2025-042",
        phone_number="+1-555-0103",
        quiz_avg=88.5,
        coding_avg=82.0,
        learning_hours=14.5,
        daily_streak=7,
        xp=450,
        level=2
    )
    admin_legacy = User(
        name="Legacy Admin",
        email="admin@skillpath.ai",
        password_hash=get_password_hash("admin123"),
        role="admin",
        college_id=c1.id
    )

    db.add_all([super_admin, principal_user, hod_user, teacher_user, student_user, admin_legacy])
    db.commit()

    # Link HOD to Department
    d1.hod_id = hod_user.id
    db.commit()

    db.refresh(teacher_user)
    db.refresh(student_user)

    # Seed Subjects & Assignments
    subj1 = Subject(department_id=d1.id, semester_id=s1.id, name="Data Structures & Algorithms", code="CS501", teacher_id=teacher_user.id)
    subj2 = Subject(department_id=d1.id, semester_id=s1.id, name="Object Oriented Systems", code="CS502", teacher_id=teacher_user.id)
    db.add_all([subj1, subj2])
    db.commit()
    db.refresh(subj1)

    ass1 = Assignment(
        subject_id=subj1.id,
        teacher_id=teacher_user.id,
        title="Implementation of Binary Search Tree & Balancing",
        description="Implement a BST in Python/C++ with insert, delete, and in-order traversal methods.",
        type="coding",
        due_date=datetime.datetime.utcnow() + datetime.timedelta(days=5),
        max_marks=100
    )
    ass2 = Assignment(
        subject_id=subj1.id,
        teacher_id=teacher_user.id,
        title="Analysis of Time & Space Complexity",
        description="Write a detailed paper explaining Big-O notation, master theorem, and asymptotic bounds.",
        type="pdf",
        due_date=datetime.datetime.utcnow() + datetime.timedelta(days=7),
        max_marks=100
    )
    db.add_all([ass1, ass2])
    db.commit()
    db.refresh(ass1)

    # Seed Submission, Attendance, Activity Tracks, Notifications
    sub1 = AssignmentSubmission(
        assignment_id=ass1.id,
        student_id=student_user.id,
        code="class Node:\n    def __init__(self, val):\n        self.val = val\n        self.left = None\n        self.right = None",
        marks_obtained=92.0,
        feedback="Excellent code structure and clean variable naming.",
        ai_feedback="Tree structure implementation follows standard specifications. Time complexity is optimal O(log n)."
    )
    db.add(sub1)

    # Attendance logs for past 3 days
    today = datetime.date.today()
    for i in range(5):
        d_day = today - datetime.timedelta(days=i)
        db.add(AttendanceRecord(
            student_id=student_user.id,
            subject_id=subj1.id,
            date=d_day,
            status="Present",
            study_minutes=45
        ))
        db.add(ActivityTrack(
            student_id=student_user.id,
            activity_type="coding",
            duration_minutes=35.0,
            details="Solved BST coding assignment",
            timestamp=datetime.datetime.combine(d_day, datetime.time(10, 0))
        ))

    # Notification & Placement record
    db.add(TeacherNotification(
        sender_teacher_id=teacher_user.id,
        recipient_student_id=student_user.id,
        type="congratulations",
        title="Great Performance in Coding Lab!",
        message="Keep up the great work on your Data Structures assignments!"
    ))

    db.add(PlacementRecord(
        student_id=student_user.id,
        placement_score=85.4,
        coding_score=82.0,
        quiz_score=88.5,
        projects_score=85.0,
        attendance_score=100.0,
        resume_score=80.0,
        interview_score=78.0,
        roadmap_completion_score=75.0,
        ai_recommendations="Focus on mock interviews to elevate spoken explanation clarity."
    ))
    db.commit()

    # 3. Seed Career Pathways (All 14 Paths)
    careers_list = [
        ("Python Developer", "Master Python syntax, object-oriented software patterns, backend APIs, data libraries, and tools."),
        ("Java Developer", "Master static compilation engineering using Java core classes, collection structures, JDBC, Spring Boot, and Docker."),
        ("C++ Developer", "Master low-level programming compilation, pointers dereferencing, structures, STL container templates, and data structures."),
        ("Frontend Developer", "Learn HTML5, CSS3, ES6 JavaScript, responsive design principles, web standards, and UI kits."),
        ("Backend Developer", "Design databases, API controllers, server routes, SQL models, auth handlers, and middleware services."),
        ("Full Stack Developer", "Integrate responsive client pages with structured server endpoints, managing database entities and assets."),
        ("Android Developer", "Build responsive mobile apps using Java/Kotlin, UI constraints, local databases, and Android Studio."),
        ("Data Science", "Analyze statistical datasets using Python, data cleansers, tables indexing, and charts visuals."),
        ("Machine Learning", "Train predictive algorithms, regressions, neural nodes classifiers, and weights tuning using ML modules."),
        ("AI Engineer", "Deploy intelligent LLM interfaces, vector index search, automated prompts parsing, and agents integrations."),
        ("Cyber Security", "Protect system endpoints, audit authorization mechanisms, handle encryption, and run networking tests."),
        ("Cloud Engineer", "Manage dynamic container platforms, cloud virtualization, object buckets storage, and scale configurations."),
        ("DevOps Engineer", "Configure continuous building scripts, CI/CD runtimes, server monitors, and automated releases."),
        ("UI UX Designer", "Design user wireframes, dark/light theme templates, typography ratios, and responsive UI components.")
    ]

    careers_map = {}
    for name, desc in careers_list:
        career = Career(name=name, description=desc)
        db.add(career)
        db.commit()
        db.refresh(career)
        careers_map[name] = career

    # Enroll default student in all pathways
    for career in careers_map.values():
        student_user.enrolled_careers.append(career)
    student_user.current_career_id = careers_map["Python Developer"].id # default focus
    db.commit()

    # 4. Seed Roadmaps & Topics

    # --- Python Topics List (34 Topics) ---
    python_topics = [
        "Python Installation", "VS Code Setup", "Variables", "Data Types", "Operators",
        "Input Output", "Conditional Statements", "Loops", "Functions", "Strings",
        "Lists", "Tuples", "Sets", "Dictionary", "File Handling", "Exception Handling",
        "Modules", "Packages", "Object Oriented Programming", "Virtual Environment",
        "MySQL with Python", "NumPy", "Pandas", "Matplotlib", "Flask", "FastAPI",
        "REST API", "JWT Authentication", "SQLAlchemy", "Docker", "Git", "GitHub",
        "Final Python Project", "Interview Preparation"
    ]

    # --- Java Topics List (27 Topics) ---
    java_topics = [
        "Java Installation", "IntelliJ IDEA", "Variables", "Data Types", "Operators",
        "If Else", "Loops", "Methods", "Arrays", "Strings", "OOP", "Exception Handling",
        "Collections", "Multithreading", "File Handling", "JDBC", "Maven", "Spring Boot",
        "REST API", "Hibernate", "Spring Security", "MySQL", "Docker", "Git", "GitHub",
        "Final Java Project", "Interview Preparation"
    ]

    # --- C++ Topics List (25 Topics) ---
    cpp_topics = [
        "C++ Installation", "IDE Setup", "Variables", "Data Types", "Operators",
        "Input Output", "If Else", "Loops", "Functions", "Arrays", "Strings", "Pointers",
        "Structures", "OOP", "Templates", "STL", "File Handling", "Dynamic Memory",
        "Data Structures", "Algorithms", "Competitive Programming", "Git", "GitHub",
        "Final C++ Project", "Interview Preparation"
    ]

    # Map topics to logical milestones/roadmaps (6 Milestones per pathway)
    def get_roadmap_index(topic_order, total_topics):
        if topic_order <= int(total_topics * 0.18):
            return 0  # Milestone 1: Basics
        elif topic_order <= int(total_topics * 0.36):
            return 1  # Milestone 2: Flow & Structs
        elif topic_order <= int(total_topics * 0.54):
            return 2  # Milestone 3: Intermediate Core
        elif topic_order <= int(total_topics * 0.70):
            return 3  # Milestone 4: Advanced Core
        elif topic_order <= int(total_topics * 0.86):
            return 4  # Milestone 5: Web & DB Frameworks
        else:
            return 5  # Milestone 6: Deployment & Projects

    # Helper to generate milestones
    def build_pathway_roadmaps(career_id, prefix_title):
        milestones = [
            ("Core Basics", "Get started with setup, installations, variables, and basic operators."),
            ("Control Structures", "Master loops, conditionals, methods, and functions logic."),
            ("Data Collections", "Learn sequences, collections, lists, vectors, and arrays storage."),
            ("Advanced Programming", "Explore object-oriented patterns, multithreading, and files."),
            ("Frameworks & Databases", "Utilize backend frameworks, SQL, connections, and ORM objects."),
            ("Dev Tools & Capstone", "Learn containers, version controls, projects, and interview questions.")
        ]
        roadmap_objs = []
        for i, (title, desc) in enumerate(milestones):
            rm = Roadmap(career_id=career_id, title=f"{prefix_title}: {title}", description=desc, order=i+1)
            db.add(rm)
            db.commit()
            db.refresh(rm)
            roadmap_objs.append(rm)
        return roadmap_objs

    # Generate roadmaps
    py_roadmaps = build_pathway_roadmaps(careers_map["Python Developer"].id, "Python")
    java_roadmaps = build_pathway_roadmaps(careers_map["Java Developer"].id, "Java")
    cpp_roadmaps = build_pathway_roadmaps(careers_map["C++ Developer"].id, "C++")

    # Helper to seed a list of topics under a pathway
    def seed_topic_list(topics, roadmap_objs, channel_name, base_video_url, doc_base_url, career_name):
        total = len(topics)
        for i, title in enumerate(topics):
            order = i + 1
            rm_idx = get_roadmap_index(order, total)
            roadmap = roadmap_objs[rm_idx]
            
            # Difficulty mapping
            diff = "easy"
            if order > int(total * 0.7):
                diff = "hard"
            elif order > int(total * 0.3):
                diff = "medium"

            # Dynamic resource generation
            doc_url = f"{doc_base_url}/{title.lower().replace(' ', '-')}"

            # Objectives
            obj_list = [
                f"Understand core principles of {title}.",
                f"Implement functional logic using {title} syntax.",
                f"Verify correctness with coding exercises."
            ]

            # Notes and Cheat sheets
            notes_code = f"# Notes for {title}\n# Follow code syntax patterns below\n"
            if "C++" in roadmap.title:
                notes_code = f"// C++ Notes for {title}\n// Follow memory structures\n"
            elif "Java" in roadmap.title:
                notes_code = f"// Java Notes for {title}\n// Follow class templates\n"

            # Fetch custom video array dynamically
            topic_videos = get_topic_video_data(title, career_name)

            # Create topic
            topic = Topic(
                roadmap_id=roadmap.id,
                title=title,
                description=f"This comprehensive module covers {title}. Students will master how to implement, optimize, and debug programs using {title} concepts, setting a strong engineering foundation.",
                learning_objectives="\n".join(obj_list),
                youtube_videos=json.dumps(topic_videos),
                official_documentation=json.dumps([{"title": f"Official {title} Documentation Guide", "url": doc_url}]),
                notes=f"{notes_code}def main():\n    print('Exploring {title}')\n\nif __name__ == '__main__':\n    main()",
                cheat_sheet=f"{title} cheatsheet:\n- Use clean formatting\n- Test variables boundaries\n- Review diagnostics output",
                practice_questions=json.dumps([
                    f"Explain the purpose and mechanics of {title} in software engineering.",
                    f"Write a script that demonstrates {title} in a real-world project context.",
                    f"What are the best practices and potential traps when implementing {title}?"
                ]),
                mini_project=f"Create a mini-application (e.g. {title} Analyzer) that structures inputs, processes them, and prints diagnostics outputs.",
                difficulty=diff,
                estimated_time=float(1.5 if diff == "easy" else 2.5 if diff == "medium" else 4.0),
                order=order
            )
            db.add(topic)
            db.commit()
            db.refresh(topic)

            # Unlock the very first topic of this career path, lock subsequent levels
            prog_status = "Unlocked" if order == 1 else "Locked"

            progress = StudentProgress(
                student_id=student_user.id,
                topic_id=topic.id,
                status=prog_status,
                study_time_minutes=0
            )
            db.add(progress)

            # Create Quiz
            quiz = Quiz(topic_id=topic.id, passing_percentage=70)
            db.add(quiz)
            db.commit()
            db.refresh(quiz)

            # Add two quiz questions
            q1 = Question(
                quiz_id=quiz.id,
                question_text=f"Which of the following best describes the core utility of {title}?",
                option_a=f"Handling core {title} configurations dynamically.",
                option_b="Compiling simple variables values to print them.",
                option_c="Evaluating random system loops controls.",
                option_d="None of the options listed.",
                correct_option="A",
                explanation=f"{title} primarily handles core configuration and execution parameters in this learning module."
            )
            q2 = Question(
                quiz_id=quiz.id,
                question_text=f"What is a common trap to watch out for when working with {title}?",
                option_a="Compilations take too long.",
                option_b="Syntax errors due to missing brackets, variables mismatch, or logical loops flaws.",
                option_c="It uses too much database rows storage.",
                option_d="None of the above.",
                correct_option="B",
                explanation=f"Missing brackets, logic operators flaws, or variable types mismatches are common bugs when implementing {title}."
            )
            db.add_all([q1, q2])

            # Add Custom Topic-Specific Coding Challenge
            chal_data = get_topic_challenge_data(title, diff, career_name)
            challenge = CodingChallenge(
                topic_id=topic.id,
                title=f"{title} Code Lab",
                description=chal_data["description"],
                difficulty=diff,
                template_code=chal_data["template_code"],
                test_cases=chal_data["test_cases"],
                score_points=chal_data["score_points"]
            )
            db.add(challenge)
            db.commit()

    # Seed Python topics
    seed_topic_list(
        python_topics, py_roadmaps,
        channel_name="CodeWithHarry",
        base_video_url="https://www.youtube.com/watch?v=vLqTf2b6GZw&list=PLu0W_9lII9agwh1XjRtDYKeyD3Ie160e1",
        doc_base_url="https://docs.python.org/3/tutorial",
        career_name="Python Developer"
    )

    # Seed Java topics
    seed_topic_list(
        java_topics, java_roadmaps,
        channel_name="Telusko",
        base_video_url="https://www.youtube.com/watch?v=A74TOX803D0&list=PLsyeobzWxl7pe_IiTfNspVyL_k608FCy0",
        doc_base_url="https://docs.oracle.com/javase/tutorial",
        career_name="Java Developer"
    )

    # Seed C++ topics
    seed_topic_list(
        cpp_topics, cpp_roadmaps,
        channel_name="The Cherno",
        base_video_url="https://www.youtube.com/watch?v=18c3MTX0PK0&list=PLlrATfQZw1h1v1dPL_I7Z7FIdA06S2jA5",
        doc_base_url="https://en.cppreference.com/w",
        career_name="C++ Developer"
    )

    print("Database cleared. 14 Career pathways registered.")
    print("Python (34), Java (27), and C++ (25) topics seeded successfully with Quizzes, MCQs, and Coding Challenges.")
