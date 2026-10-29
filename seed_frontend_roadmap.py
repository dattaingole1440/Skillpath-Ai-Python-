"""
Seed Script: Frontend Developer Roadmap
========================================
Creates a full career roadmap with milestones, topics, YouTube videos,
quizzes (with MCQ questions), and coding challenges.

Run: py seed_frontend_roadmap.py
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
        career = db.query(Career).filter(Career.name == "Frontend Developer").first()
        if not career:
            career = Career(
                name="Frontend Developer",
                slug="frontend-developer",
                icon="bi-code-slash",
                badge="🎨",
                description="Master HTML, CSS, JavaScript, React, and modern frontend technologies to build stunning, responsive web applications.",
                total_topics=18,
                is_active=True,
                is_deleted=False
            )
            db.add(career)
            db.commit()
            db.refresh(career)
            print(f"✅ Created Career: Frontend Developer (ID: {career.id})")
        else:
            print(f"ℹ️  Career 'Frontend Developer' already exists (ID: {career.id}). Checking for missing data...")

        # ===================================================
        # 2. ROADMAP MILESTONES + TOPICS + VIDEOS + QUIZZES + CHALLENGES
        # ===================================================
        roadmap_data = [
            {
                "title": "Milestone 1: HTML & Web Foundations",
                "description": "Learn the building blocks of the web — HTML structure, semantic elements, forms, and accessibility.",
                "order": 1,
                "topics": [
                    {
                        "title": "HTML Basics & Document Structure",
                        "description": "Learn HTML5 document structure, head/body sections, meta tags, and essential HTML elements like headings, paragraphs, lists, and links.",
                        "learning_objectives": "Understand HTML5 document structure and DOCTYPE\nUse semantic HTML elements correctly\nCreate well-structured web pages\nUnderstand meta tags and SEO basics",
                        "difficulty": "easy",
                        "estimated_time": 2.0,
                        "order": 1,
                        "notes": "HTML (HyperText Markup Language) is the standard markup language for creating web pages.\n\nKey Concepts:\n- <!DOCTYPE html> declares the document type\n- <html> is the root element\n- <head> contains metadata\n- <body> contains visible content\n- Semantic elements: <header>, <nav>, <main>, <section>, <article>, <footer>",
                        "cheat_sheet": "TAGS:\n<h1>-<h6> = Headings\n<p> = Paragraph\n<a href='url'> = Link\n<img src='url' alt='desc'> = Image\n<ul>/<ol>/<li> = Lists\n<div> = Division\n<span> = Inline container\n\nATTRIBUTES:\nid, class, style, title, src, href, alt",
                        "videos": [
                            {"title": "HTML Full Course for Beginners", "url": "https://www.youtube.com/watch?v=kUMe1FH4CHE"},
                            {"title": "HTML Crash Course For Absolute Beginners", "url": "https://www.youtube.com/watch?v=UB1O30fR-EE"}
                        ],
                        "docs": [
                            {"title": "MDN Web Docs - HTML", "url": "https://developer.mozilla.org/en-US/docs/Web/HTML"},
                            {"title": "W3Schools HTML Tutorial", "url": "https://www.w3schools.com/html/"}
                        ],
                        "quiz_questions": [
                            {"text": "What does HTML stand for?", "a": "Hyper Text Markup Language", "b": "High Tech Machine Language", "c": "Hyper Transfer Markup Language", "d": "Home Tool Markup Language", "correct": "A", "exp": "HTML stands for HyperText Markup Language — the standard language for web pages."},
                            {"text": "Which HTML element is used for the largest heading?", "a": "<heading>", "b": "<h6>", "c": "<h1>", "d": "<head>", "correct": "C", "exp": "<h1> is the largest heading element. Headings range from <h1> (largest) to <h6> (smallest)."},
                            {"text": "Which HTML tag is used to define an unordered list?", "a": "<ol>", "b": "<ul>", "c": "<list>", "d": "<dl>", "correct": "B", "exp": "<ul> creates an unordered (bulleted) list. <ol> creates an ordered (numbered) list."},
                            {"text": "What is the correct HTML element for inserting a line break?", "a": "<break>", "b": "<lb>", "c": "<br>", "d": "<newline>", "correct": "C", "exp": "<br> is a self-closing tag that inserts a line break in HTML."},
                        ],
                        "challenges": [
                            {
                                "title": "Create an HTML Page Structure",
                                "description": "Write a function that returns a valid HTML5 document string with a title, heading, and paragraph.",
                                "difficulty": "easy",
                                "template_code": "def create_html_page(title, heading, paragraph):\n    # Return a complete HTML5 document string\n    # with the given title in <title>, heading in <h1>, and paragraph in <p>\n    pass",
                                "test_cases": json.dumps([
                                    {"function_name": "create_html_page", "args": ["My Page", "Hello World", "Welcome to my website."], "expected": "<!DOCTYPE html><html><head><title>My Page</title></head><body><h1>Hello World</h1><p>Welcome to my website.</p></body></html>"},
                                ]),
                                "score_points": 10
                            }
                        ]
                    },
                    {
                        "title": "HTML Forms & Input Elements",
                        "description": "Master HTML forms, input types, validation attributes, textarea, select dropdowns, and form submission handling.",
                        "learning_objectives": "Create forms with various input types\nUse HTML5 form validation attributes\nUnderstand form methods (GET vs POST)\nImplement accessible form labels",
                        "difficulty": "easy",
                        "estimated_time": 2.5,
                        "order": 2,
                        "notes": "Forms are essential for user interaction. Key elements:\n- <form action='/submit' method='POST'>\n- <input type='text|email|password|number|date|checkbox|radio'>\n- <select> and <option> for dropdowns\n- <textarea> for multi-line text\n- <button type='submit'>",
                        "cheat_sheet": "INPUT TYPES:\ntext, email, password, number, date, tel, url, file, color, range, checkbox, radio, hidden, submit\n\nVALIDATION:\nrequired, minlength, maxlength, min, max, pattern, placeholder",
                        "videos": [
                            {"title": "HTML Forms Tutorial - Full Course", "url": "https://www.youtube.com/watch?v=fNcJuPIZ2WE"},
                            {"title": "Learn HTML Forms in 25 Minutes", "url": "https://www.youtube.com/watch?v=2O8pkybH6po"}
                        ],
                        "docs": [
                            {"title": "MDN - HTML Forms Guide", "url": "https://developer.mozilla.org/en-US/docs/Learn/Forms"},
                        ],
                        "quiz_questions": [
                            {"text": "Which attribute specifies where to send the form data?", "a": "method", "b": "action", "c": "target", "d": "enctype", "correct": "B", "exp": "The 'action' attribute specifies the URL where the form data should be sent upon submission."},
                            {"text": "Which input type creates a checkbox?", "a": "type='check'", "b": "type='tick'", "c": "type='checkbox'", "d": "type='box'", "correct": "C", "exp": "type='checkbox' creates a checkbox input that can be toggled on/off."},
                            {"text": "Which HTML5 attribute prevents form submission if a field is empty?", "a": "validate", "b": "required", "c": "notnull", "d": "mandatory", "correct": "B", "exp": "The 'required' attribute ensures the field must be filled before submission."},
                        ],
                        "challenges": []
                    },
                    {
                        "title": "HTML5 Semantic Elements & Accessibility",
                        "description": "Learn semantic HTML5 elements like <header>, <nav>, <main>, <article>, <section>, <aside>, <footer> and web accessibility with ARIA attributes.",
                        "learning_objectives": "Use semantic HTML5 elements for better structure\nImplement ARIA roles and attributes\nUnderstand web accessibility standards (WCAG)\nCreate screen-reader friendly content",
                        "difficulty": "medium",
                        "estimated_time": 2.0,
                        "order": 3,
                        "notes": "Semantic HTML improves accessibility and SEO.\n\nKey Elements:\n<header> - Page or section header\n<nav> - Navigation links\n<main> - Main content area\n<article> - Self-contained content\n<section> - Thematic grouping\n<aside> - Side content\n<footer> - Page or section footer\n\nARIA:\nrole, aria-label, aria-labelledby, aria-describedby, aria-hidden",
                        "cheat_sheet": "SEMANTIC ELEMENTS:\n<header>, <nav>, <main>, <article>, <section>, <aside>, <footer>, <figure>, <figcaption>, <details>, <summary>, <time>, <mark>\n\nARIA:\nrole='navigation|banner|main|complementary|contentinfo'\naria-label='description'\naria-hidden='true|false'",
                        "videos": [
                            {"title": "Semantic HTML5 Elements Explained", "url": "https://www.youtube.com/watch?v=kGW8Al_cga4"},
                            {"title": "Web Accessibility - Complete Guide", "url": "https://www.youtube.com/watch?v=e2nkq3h1P68"}
                        ],
                        "docs": [
                            {"title": "MDN - Semantics in HTML", "url": "https://developer.mozilla.org/en-US/docs/Glossary/Semantics"},
                            {"title": "WebAIM - Web Accessibility", "url": "https://webaim.org/intro/"}
                        ],
                        "quiz_questions": [
                            {"text": "Which HTML5 element represents the main content of a document?", "a": "<content>", "b": "<body>", "c": "<main>", "d": "<div>", "correct": "C", "exp": "The <main> element contains the dominant content unique to the document, excluding sidebars, nav, and footers."},
                            {"text": "What does ARIA stand for in web accessibility?", "a": "Accessible Rich Internet Applications", "b": "Advanced Responsive Interface Architecture", "c": "Automated Readable Internet Access", "d": "Application Resource Interaction API", "correct": "A", "exp": "ARIA (Accessible Rich Internet Applications) provides attributes to make web content more accessible."},
                            {"text": "Which semantic element is best for navigation links?", "a": "<links>", "b": "<navigation>", "c": "<nav>", "d": "<menu>", "correct": "C", "exp": "The <nav> element represents a section of navigation links."},
                        ],
                        "challenges": []
                    }
                ]
            },
            {
                "title": "Milestone 2: CSS & Styling Mastery",
                "description": "Master CSS selectors, box model, flexbox, grid, animations, and responsive design principles.",
                "order": 2,
                "topics": [
                    {
                        "title": "CSS Fundamentals & Selectors",
                        "description": "Learn CSS syntax, selectors (element, class, ID, attribute, pseudo-classes), specificity, cascade, and inheritance.",
                        "learning_objectives": "Write CSS rules using various selectors\nUnderstand specificity and cascade order\nApply colors, fonts, and text styling\nUse CSS units (px, em, rem, %, vh, vw)",
                        "difficulty": "easy",
                        "estimated_time": 3.0,
                        "order": 1,
                        "notes": "CSS (Cascading Style Sheets) controls visual presentation.\n\nSelectors:\n- element: p { }\n- class: .classname { }\n- ID: #idname { }\n- attribute: [type='text'] { }\n- pseudo-class: :hover, :focus, :nth-child()\n- pseudo-element: ::before, ::after\n\nSpecificity: inline > ID > class > element",
                        "cheat_sheet": "SELECTORS:\nelement, .class, #id, *, element element, element > child, element + sibling, [attr], :hover, :focus, :first-child, :nth-child(n), ::before, ::after\n\nUNITS:\npx, em, rem, %, vw, vh, vmin, vmax, fr",
                        "videos": [
                            {"title": "CSS Tutorial - Full Course for Beginners", "url": "https://www.youtube.com/watch?v=1Rs2ND1ryYc"},
                            {"title": "CSS Crash Course For Absolute Beginners", "url": "https://www.youtube.com/watch?v=yfoY53QXEnI"}
                        ],
                        "docs": [
                            {"title": "MDN - CSS Basics", "url": "https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/CSS_basics"},
                        ],
                        "quiz_questions": [
                            {"text": "Which CSS property is used to change the text color?", "a": "font-color", "b": "text-color", "c": "color", "d": "foreground-color", "correct": "C", "exp": "The 'color' property sets the foreground color of text content."},
                            {"text": "What does CSS stand for?", "a": "Colorful Style Sheets", "b": "Cascading Style Sheets", "c": "Creative Style System", "d": "Computer Style Sheets", "correct": "B", "exp": "CSS stands for Cascading Style Sheets — the language for styling web pages."},
                            {"text": "Which selector has the highest specificity?", "a": "element", "b": ".class", "c": "#id", "d": "*", "correct": "C", "exp": "ID selectors (#id) have higher specificity than class selectors, which are higher than element selectors."},
                        ],
                        "challenges": []
                    },
                    {
                        "title": "CSS Flexbox Layout",
                        "description": "Master CSS Flexbox for one-dimensional layouts — align, justify, wrap, grow, shrink, and order items in containers.",
                        "learning_objectives": "Create flexible layouts using display: flex\nAlign items with justify-content and align-items\nUse flex-grow, flex-shrink, and flex-basis\nBuild responsive navigation bars and card layouts",
                        "difficulty": "medium",
                        "estimated_time": 3.0,
                        "order": 2,
                        "notes": "Flexbox is a one-dimensional layout method for arranging items in rows or columns.\n\nContainer Properties:\ndisplay: flex\nflex-direction: row | column\njustify-content: flex-start | center | space-between | space-around | space-evenly\nalign-items: stretch | center | flex-start | flex-end\nflex-wrap: wrap | nowrap\ngap: 10px\n\nItem Properties:\nflex-grow, flex-shrink, flex-basis, order, align-self",
                        "cheat_sheet": "CONTAINER:\ndisplay: flex;\nflex-direction: row | row-reverse | column | column-reverse;\njustify-content: flex-start | center | space-between | space-around | space-evenly;\nalign-items: stretch | center | flex-start | flex-end | baseline;\nflex-wrap: wrap | nowrap;\ngap: 10px;\n\nITEMS:\nflex: 1; (shorthand for grow shrink basis)\norder: 0;\nalign-self: auto;",
                        "videos": [
                            {"title": "Flexbox CSS in 20 Minutes", "url": "https://www.youtube.com/watch?v=JJSoEo8JSnc"},
                            {"title": "CSS Flexbox Tutorial - Complete Guide", "url": "https://www.youtube.com/watch?v=u044iM9xsWU"}
                        ],
                        "docs": [
                            {"title": "CSS-Tricks: Complete Guide to Flexbox", "url": "https://css-tricks.com/snippets/css/a-guide-to-flexbox/"},
                            {"title": "MDN - Flexbox", "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Flexbox"}
                        ],
                        "quiz_questions": [
                            {"text": "Which CSS property creates a flex container?", "a": "display: block", "b": "display: flex", "c": "display: grid", "d": "display: inline", "correct": "B", "exp": "display: flex turns an element into a flex container, enabling flexbox layout for its children."},
                            {"text": "Which property distributes space between flex items along the main axis?", "a": "align-items", "b": "flex-wrap", "c": "justify-content", "d": "align-content", "correct": "C", "exp": "justify-content aligns flex items along the main axis (horizontal by default)."},
                            {"text": "What does flex-wrap: wrap do?", "a": "Prevents items from wrapping", "b": "Allows items to wrap onto multiple lines", "c": "Reverses the order of items", "d": "Centers items vertically", "correct": "B", "exp": "flex-wrap: wrap allows flex items to wrap onto new lines when they exceed the container width."},
                        ],
                        "challenges": []
                    },
                    {
                        "title": "CSS Grid Layout",
                        "description": "Learn CSS Grid for two-dimensional layouts — define rows, columns, template areas, and build complex page layouts.",
                        "learning_objectives": "Create two-dimensional layouts with CSS Grid\nDefine grid templates with rows and columns\nUse grid-template-areas for named layouts\nImplement responsive grids with minmax() and auto-fill",
                        "difficulty": "medium",
                        "estimated_time": 3.5,
                        "order": 3,
                        "notes": "CSS Grid is a two-dimensional layout system for complex page layouts.\n\nContainer:\ndisplay: grid;\ngrid-template-columns: 1fr 1fr 1fr;\ngrid-template-rows: auto;\ngap: 20px;\ngrid-template-areas: 'header header' 'sidebar main' 'footer footer';\n\nItems:\ngrid-column: 1 / 3;\ngrid-row: 1 / 2;\ngrid-area: header;",
                        "cheat_sheet": "CONTAINER:\ndisplay: grid;\ngrid-template-columns: repeat(3, 1fr);\ngrid-template-rows: auto 1fr auto;\ngap: 20px;\ngrid-template-areas: '...';\n\nITEMS:\ngrid-column: start / end;\ngrid-row: start / end;\ngrid-area: name;\n\nFUNCTIONS:\nrepeat(), minmax(), auto-fill, auto-fit",
                        "videos": [
                            {"title": "CSS Grid Layout Crash Course", "url": "https://www.youtube.com/watch?v=jV8B24rSN5o"},
                            {"title": "Learn CSS Grid - Full Course", "url": "https://www.youtube.com/watch?v=EFafSYg-PkI"}
                        ],
                        "docs": [
                            {"title": "CSS-Tricks: Complete Guide to Grid", "url": "https://css-tricks.com/snippets/css/complete-guide-grid/"},
                            {"title": "MDN - CSS Grid Layout", "url": "https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout"}
                        ],
                        "quiz_questions": [
                            {"text": "Which property defines the number of columns in a CSS Grid?", "a": "grid-columns", "b": "grid-template-columns", "c": "columns", "d": "grid-cols", "correct": "B", "exp": "grid-template-columns defines the column tracks of the grid container."},
                            {"text": "What does 'fr' unit represent in CSS Grid?", "a": "Fixed ratio", "b": "Fractional unit of available space", "c": "Frame rate", "d": "Font ratio", "correct": "B", "exp": "The 'fr' unit represents a fraction of the available space in the grid container."},
                            {"text": "Which function creates responsive grid columns that auto-fill available space?", "a": "auto()", "b": "responsive()", "c": "repeat(auto-fill, minmax())", "d": "grid-auto()", "correct": "C", "exp": "repeat(auto-fill, minmax(250px, 1fr)) creates as many columns as fit, each at least 250px wide."},
                        ],
                        "challenges": []
                    }
                ]
            },
            {
                "title": "Milestone 3: JavaScript Core",
                "description": "Master JavaScript fundamentals — variables, functions, arrays, objects, DOM manipulation, events, and ES6+ features.",
                "order": 3,
                "topics": [
                    {
                        "title": "JavaScript Variables, Data Types & Operators",
                        "description": "Learn JavaScript variables (var, let, const), primitive data types (string, number, boolean, null, undefined, symbol, BigInt), and operators.",
                        "learning_objectives": "Declare variables using let, const, and var\nUnderstand primitive and reference data types\nUse arithmetic, comparison, logical, and assignment operators\nPerform type coercion and type checking",
                        "difficulty": "easy",
                        "estimated_time": 2.5,
                        "order": 1,
                        "notes": "JavaScript Variables:\n- let: block-scoped, reassignable\n- const: block-scoped, cannot be reassigned\n- var: function-scoped (legacy)\n\nData Types:\nPrimitive: string, number, boolean, null, undefined, symbol, BigInt\nReference: object, array, function\n\nOperators:\nArithmetic: + - * / % **\nComparison: == === != !== < > <= >=\nLogical: && || !\nAssignment: = += -= *= /=",
                        "cheat_sheet": "VARIABLES:\nlet name = 'John';\nconst PI = 3.14;\n\nTYPE CHECK:\ntypeof variable\n\nSTRING METHODS:\n.length, .toUpperCase(), .toLowerCase(), .includes(), .split(), .trim(), .slice(), .replace()\n\nNUMBER METHODS:\nparseInt(), parseFloat(), .toFixed(), Number.isNaN()",
                        "videos": [
                            {"title": "JavaScript Tutorial for Beginners - Full Course", "url": "https://www.youtube.com/watch?v=PkZNo7MFNFg"},
                            {"title": "JavaScript Crash Course For Beginners", "url": "https://www.youtube.com/watch?v=hdI2bqOjy3c"}
                        ],
                        "docs": [
                            {"title": "MDN - JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"},
                            {"title": "JavaScript.info - The Modern Tutorial", "url": "https://javascript.info/"}
                        ],
                        "quiz_questions": [
                            {"text": "Which keyword declares a block-scoped variable that cannot be reassigned?", "a": "var", "b": "let", "c": "const", "d": "static", "correct": "C", "exp": "'const' declares a block-scoped variable whose value cannot be reassigned after initialization."},
                            {"text": "What is the result of typeof null in JavaScript?", "a": "null", "b": "undefined", "c": "object", "d": "string", "correct": "C", "exp": "typeof null returns 'object' — this is a known JavaScript quirk from its early design."},
                            {"text": "Which operator checks both value AND type equality?", "a": "==", "b": "===", "c": "!=", "d": "=", "correct": "B", "exp": "=== (strict equality) checks both value and type without type coercion."},
                        ],
                        "challenges": [
                            {
                                "title": "Variable Type Checker",
                                "description": "Write a function that takes a value and returns its JavaScript-style type as a string.",
                                "difficulty": "easy",
                                "template_code": "def check_type(value):\n    # Return 'string', 'number', 'boolean', 'list', 'dict', or 'none'\n    # based on the Python type of the value\n    pass",
                                "test_cases": json.dumps([
                                    {"function_name": "check_type", "args": ["hello"], "expected": "string"},
                                    {"function_name": "check_type", "args": [42], "expected": "number"},
                                    {"function_name": "check_type", "args": [True], "expected": "boolean"},
                                    {"function_name": "check_type", "args": [[1,2]], "expected": "list"},
                                    {"function_name": "check_type", "args": [None], "expected": "none"},
                                ]),
                                "score_points": 15
                            }
                        ]
                    },
                    {
                        "title": "JavaScript Functions & Scope",
                        "description": "Master function declarations, expressions, arrow functions, closures, scope chain, and higher-order functions.",
                        "learning_objectives": "Write function declarations and expressions\nUse ES6 arrow functions\nUnderstand closures and lexical scope\nImplement higher-order functions (map, filter, reduce)",
                        "difficulty": "medium",
                        "estimated_time": 3.0,
                        "order": 2,
                        "videos": [
                            {"title": "JavaScript Functions - Beginner to Advanced", "url": "https://www.youtube.com/watch?v=FOD408a0EzU"},
                            {"title": "Closures Explained in 100 Seconds", "url": "https://www.youtube.com/watch?v=vKJpN5FAeF4"}
                        ],
                        "docs": [
                            {"title": "MDN - Functions", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions"},
                        ],
                        "quiz_questions": [
                            {"text": "What is a closure in JavaScript?", "a": "A function that closes the browser", "b": "A function that has access to its outer scope variables even after the outer function returns", "c": "A method to close a database connection", "d": "A loop that terminates automatically", "correct": "B", "exp": "A closure is a function that retains access to variables from its lexical scope even after the enclosing function has finished."},
                            {"text": "Which array method creates a new array with elements that pass a test?", "a": "map()", "b": "reduce()", "c": "filter()", "d": "forEach()", "correct": "C", "exp": "filter() creates a new array containing only elements for which the callback returns true."},
                            {"text": "What is the syntax for an ES6 arrow function?", "a": "function => {}", "b": "(params) => {}", "c": "arrow(params) {}", "d": "=> function(params) {}", "correct": "B", "exp": "Arrow functions use (params) => {} syntax. They have lexical 'this' binding."},
                        ],
                        "challenges": [
                            {
                                "title": "Higher-Order Functions",
                                "description": "Implement a function that takes a list of numbers and returns only the even numbers doubled.",
                                "difficulty": "medium",
                                "template_code": "def double_evens(numbers):\n    # Filter even numbers, then double each one\n    # Return the resulting list\n    pass",
                                "test_cases": json.dumps([
                                    {"function_name": "double_evens", "args": [[1, 2, 3, 4, 5, 6]], "expected": [4, 8, 12]},
                                    {"function_name": "double_evens", "args": [[10, 15, 20, 25]], "expected": [20, 40]},
                                    {"function_name": "double_evens", "args": [[1, 3, 5]], "expected": []},
                                ]),
                                "score_points": 20
                            }
                        ],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "DOM Manipulation & Events",
                        "description": "Learn to interact with the Document Object Model (DOM) — select elements, modify content, handle events, and build interactive UIs.",
                        "learning_objectives": "Select DOM elements using various methods\nModify element content, attributes, and styles\nHandle user events (click, input, submit)\nCreate and remove elements dynamically",
                        "difficulty": "medium",
                        "estimated_time": 3.5,
                        "order": 3,
                        "videos": [
                            {"title": "JavaScript DOM Tutorial", "url": "https://www.youtube.com/watch?v=0ik6X4DJKCc"},
                            {"title": "DOM Crash Course - Parts 1-4", "url": "https://www.youtube.com/watch?v=wiozYyXQEVk"}
                        ],
                        "docs": [
                            {"title": "MDN - DOM Introduction", "url": "https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction"},
                        ],
                        "quiz_questions": [
                            {"text": "Which method selects an element by its ID?", "a": "document.querySelector()", "b": "document.getElementByClass()", "c": "document.getElementById()", "d": "document.selectById()", "correct": "C", "exp": "document.getElementById() returns the element with the specified ID attribute."},
                            {"text": "Which event fires when a user clicks on an element?", "a": "onhover", "b": "onclick", "c": "onpress", "d": "ontap", "correct": "B", "exp": "The 'click' event fires when the user clicks (or taps) on an element."},
                            {"text": "Which property sets or gets the HTML content inside an element?", "a": "innerText", "b": "textContent", "c": "innerHTML", "d": "outerHTML", "correct": "C", "exp": "innerHTML gets or sets the HTML markup inside an element, including tags."},
                        ],
                        "challenges": [
                            {
                                "title": "Element Selector Counter",
                                "description": "Write a function that counts HTML tags in a string.",
                                "difficulty": "medium",
                                "template_code": "def count_html_tags(html_string):\n    # Count the number of opening HTML tags (e.g., <div>, <p>, <span>)\n    # Don't count closing tags (</div>)\n    # Return the count as integer\n    import re\n    pass",
                                "test_cases": json.dumps([
                                    {"function_name": "count_html_tags", "args": ["<div><p>Hello</p></div>"], "expected": 2},
                                    {"function_name": "count_html_tags", "args": ["<h1>Title</h1><p>Text</p><span>More</span>"], "expected": 3},
                                    {"function_name": "count_html_tags", "args": ["No tags here"], "expected": 0},
                                ]),
                                "score_points": 20
                            }
                        ],
                        "notes": "",
                        "cheat_sheet": ""
                    }
                ]
            },
            {
                "title": "Milestone 4: Modern JavaScript (ES6+)",
                "description": "Master modern JavaScript — destructuring, spread/rest, promises, async/await, modules, and template literals.",
                "order": 4,
                "topics": [
                    {
                        "title": "ES6+ Features: Destructuring, Spread & Template Literals",
                        "description": "Learn modern JavaScript features including destructuring assignment, spread/rest operators, template literals, default parameters, and enhanced object literals.",
                        "learning_objectives": "Use array and object destructuring\nApply spread and rest operators\nWrite template literal strings\nUse default parameters and shorthand properties",
                        "difficulty": "medium",
                        "estimated_time": 2.5,
                        "order": 1,
                        "videos": [
                            {"title": "JavaScript ES6 Features - Full Tutorial", "url": "https://www.youtube.com/watch?v=NCwa_xi0Uuc"},
                            {"title": "ES6 JavaScript Tutorial for Beginners", "url": "https://www.youtube.com/watch?v=nZ1DMMsyVyI"}
                        ],
                        "docs": [
                            {"title": "MDN - Destructuring", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment"},
                        ],
                        "quiz_questions": [
                            {"text": "What does the spread operator (...) do with arrays?", "a": "Deletes all array elements", "b": "Expands an array into individual elements", "c": "Creates a nested array", "d": "Reverses the array", "correct": "B", "exp": "The spread operator (...) expands an iterable into individual elements."},
                            {"text": "Which syntax creates a template literal in JavaScript?", "a": "Single quotes ''", "b": "Double quotes \"\"", "c": "Backticks ``", "d": "Parentheses ()", "correct": "C", "exp": "Template literals use backticks (`) and allow embedded expressions with ${expression}."},
                            {"text": "What is destructuring in JavaScript?", "a": "Deleting an object", "b": "Unpacking values from arrays or properties from objects into distinct variables", "c": "Creating a new data structure", "d": "Breaking code into smaller files", "correct": "B", "exp": "Destructuring extracts values from arrays/objects into separate variables."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "Promises & Async/Await",
                        "description": "Master asynchronous JavaScript — callbacks, promises, promise chaining, async/await syntax, and error handling with try/catch.",
                        "learning_objectives": "Understand asynchronous programming concepts\nCreate and chain Promises\nUse async/await for cleaner async code\nHandle errors with try/catch in async functions",
                        "difficulty": "hard",
                        "estimated_time": 4.0,
                        "order": 2,
                        "videos": [
                            {"title": "JavaScript Promises in 10 Minutes", "url": "https://www.youtube.com/watch?v=DHvZLI7Db8E"},
                            {"title": "Async/Await - JavaScript Tutorial", "url": "https://www.youtube.com/watch?v=V_Kr9OSfDeU"}
                        ],
                        "docs": [
                            {"title": "MDN - Using Promises", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises"},
                            {"title": "JavaScript.info - Async/Await", "url": "https://javascript.info/async-await"}
                        ],
                        "quiz_questions": [
                            {"text": "What are the three states of a JavaScript Promise?", "a": "start, running, end", "b": "pending, fulfilled, rejected", "c": "open, closed, error", "d": "waiting, success, failure", "correct": "B", "exp": "A Promise is in one of three states: pending (initial), fulfilled (resolved), or rejected (error)."},
                            {"text": "What keyword makes a function return a Promise automatically?", "a": "await", "b": "promise", "c": "async", "d": "then", "correct": "C", "exp": "The 'async' keyword before a function makes it return a Promise automatically."},
                            {"text": "Where should you handle errors in async/await code?", "a": ".catch() only", "b": ".then() callback", "c": "try/catch block", "d": "finally block", "correct": "C", "exp": "In async/await, errors are handled using try/catch blocks for cleaner error handling."},
                        ],
                        "challenges": [
                            {
                                "title": "Promise Simulator",
                                "description": "Write a function that simulates promise resolution — given a list of (status, value) tuples, return only the 'resolved' values.",
                                "difficulty": "medium",
                                "template_code": "def resolve_promises(promise_list):\n    # promise_list is a list of tuples: [('resolved', value), ('rejected', error), ...]\n    # Return a list of values from resolved promises only\n    pass",
                                "test_cases": json.dumps([
                                    {"function_name": "resolve_promises", "args": [[["resolved", 42], ["rejected", "error"], ["resolved", 100]]], "expected": [42, 100]},
                                    {"function_name": "resolve_promises", "args": [[["rejected", "fail"], ["rejected", "err"]]], "expected": []},
                                ]),
                                "score_points": 20
                            }
                        ],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "Fetch API & HTTP Requests",
                        "description": "Learn to make HTTP requests using the Fetch API — GET, POST, PUT, DELETE, headers, JSON parsing, and error handling.",
                        "learning_objectives": "Make GET and POST requests with fetch()\nParse JSON responses\nHandle HTTP errors and status codes\nSend data with request headers and body",
                        "difficulty": "medium",
                        "estimated_time": 2.5,
                        "order": 3,
                        "videos": [
                            {"title": "JavaScript Fetch API Tutorial", "url": "https://www.youtube.com/watch?v=cuEtnrL9-H0"},
                            {"title": "Fetch API - Complete Guide", "url": "https://www.youtube.com/watch?v=Oive66jrwBs"}
                        ],
                        "docs": [
                            {"title": "MDN - Fetch API", "url": "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API"},
                        ],
                        "quiz_questions": [
                            {"text": "Which method is used to parse JSON from a fetch response?", "a": "response.text()", "b": "response.json()", "c": "response.parse()", "d": "JSON.parse(response)", "correct": "B", "exp": "response.json() parses the response body as JSON and returns a Promise."},
                            {"text": "What HTTP method is used to create a new resource on the server?", "a": "GET", "b": "PUT", "c": "POST", "d": "DELETE", "correct": "C", "exp": "POST is used to submit data and create new resources on the server."},
                            {"text": "What does a 404 HTTP status code mean?", "a": "Server Error", "b": "Unauthorized", "c": "Not Found", "d": "Bad Request", "correct": "C", "exp": "HTTP 404 means the requested resource was not found on the server."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    }
                ]
            },
            {
                "title": "Milestone 5: React.js Fundamentals",
                "description": "Learn React.js — components, JSX, props, state, hooks, event handling, and building single-page applications.",
                "order": 5,
                "topics": [
                    {
                        "title": "React Components & JSX",
                        "description": "Learn React component architecture — functional components, JSX syntax, component composition, and rendering logic.",
                        "learning_objectives": "Create functional React components\nWrite JSX with embedded JavaScript expressions\nCompose components with children\nUnderstand React component lifecycle",
                        "difficulty": "medium",
                        "estimated_time": 3.0,
                        "order": 1,
                        "videos": [
                            {"title": "React JS Full Course for Beginners", "url": "https://www.youtube.com/watch?v=bMknfKXIFA8"},
                            {"title": "React Tutorial for Beginners", "url": "https://www.youtube.com/watch?v=SqcY0GlETPk"}
                        ],
                        "docs": [
                            {"title": "React Official Docs", "url": "https://react.dev/learn"},
                            {"title": "React Quick Start", "url": "https://react.dev/learn/tutorial-tic-tac-toe"}
                        ],
                        "quiz_questions": [
                            {"text": "What is JSX in React?", "a": "A database query language", "b": "A syntax extension that lets you write HTML-like code in JavaScript", "c": "A CSS preprocessor", "d": "A testing framework", "correct": "B", "exp": "JSX is a syntax extension for JavaScript that looks like HTML and gets compiled to React.createElement() calls."},
                            {"text": "How do you create a functional component in React?", "a": "class MyComp extends React.Component", "b": "function MyComp() { return <div/> }", "c": "new Component('MyComp')", "d": "React.create('MyComp')", "correct": "B", "exp": "Functional components are JavaScript functions that return JSX elements."},
                            {"text": "What must a React component's name start with?", "a": "Lowercase letter", "b": "Underscore", "c": "Uppercase letter", "d": "Dollar sign", "correct": "C", "exp": "React components must start with an uppercase letter to distinguish them from HTML elements."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "React Hooks: useState & useEffect",
                        "description": "Master React Hooks — useState for state management, useEffect for side effects, and custom hooks.",
                        "learning_objectives": "Manage component state with useState\nHandle side effects with useEffect\nUnderstand dependency arrays\nCreate custom hooks for reusable logic",
                        "difficulty": "hard",
                        "estimated_time": 4.0,
                        "order": 2,
                        "videos": [
                            {"title": "React Hooks Tutorial - useState and useEffect", "url": "https://www.youtube.com/watch?v=O6P86uwfdR0"},
                            {"title": "All React Hooks Explained", "url": "https://www.youtube.com/watch?v=LlvBzyy-558"}
                        ],
                        "docs": [
                            {"title": "React Hooks Reference", "url": "https://react.dev/reference/react"},
                        ],
                        "quiz_questions": [
                            {"text": "What does useState return in React?", "a": "A single value", "b": "An array with the state value and a setter function", "c": "A Promise", "d": "An object with get and set methods", "correct": "B", "exp": "useState returns an array: [stateValue, setterFunction]. const [count, setCount] = useState(0)."},
                            {"text": "When does useEffect with an empty dependency array [] run?", "a": "On every render", "b": "Only once after the initial render", "c": "Never", "d": "Before the component mounts", "correct": "B", "exp": "useEffect with [] runs once after the initial render, similar to componentDidMount."},
                            {"text": "What is a custom hook in React?", "a": "A built-in React function", "b": "A function starting with 'use' that uses other hooks", "c": "A CSS hook", "d": "A lifecycle method", "correct": "B", "exp": "Custom hooks are functions that start with 'use' and let you extract and reuse stateful logic."},
                        ],
                        "challenges": [
                            {
                                "title": "State Manager Simulator",
                                "description": "Write a simple state manager that tracks state changes. Create a class that supports get_state(), set_state(), and get_history().",
                                "difficulty": "medium",
                                "template_code": "class StateManager:\n    def __init__(self, initial_state):\n        # Initialize with the given initial state\n        # Track history of all state changes\n        pass\n    \n    def get_state(self):\n        # Return current state\n        pass\n    \n    def set_state(self, new_state):\n        # Update state and record in history\n        pass\n    \n    def get_history(self):\n        # Return list of all state values (including initial)\n        pass\n\ndef test_state_manager():\n    sm = StateManager(0)\n    sm.set_state(1)\n    sm.set_state(5)\n    sm.set_state(10)\n    return sm.get_history()",
                                "test_cases": json.dumps([
                                    {"function_name": "test_state_manager", "args": [], "expected": [0, 1, 5, 10]},
                                ]),
                                "score_points": 25
                            }
                        ],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "React Router & Navigation",
                        "description": "Learn client-side routing with React Router — Routes, Links, nested routes, URL parameters, and programmatic navigation.",
                        "learning_objectives": "Set up React Router in a project\nCreate routes and navigation links\nUse URL parameters and query strings\nImplement nested and protected routes",
                        "difficulty": "medium",
                        "estimated_time": 2.5,
                        "order": 3,
                        "videos": [
                            {"title": "React Router Tutorial", "url": "https://www.youtube.com/watch?v=Ul3y1LXxzdU"},
                            {"title": "React Router v6 Complete Guide", "url": "https://www.youtube.com/watch?v=oTIJunBa6MA"}
                        ],
                        "docs": [
                            {"title": "React Router Official Docs", "url": "https://reactrouter.com/en/main"},
                        ],
                        "quiz_questions": [
                            {"text": "Which React Router component renders the first matching route?", "a": "<Switch>", "b": "<Routes>", "c": "<Router>", "d": "<Match>", "correct": "B", "exp": "In React Router v6, <Routes> renders the first child <Route> that matches the current URL."},
                            {"text": "Which component is used for client-side navigation without page reload?", "a": "<a href>", "b": "<Link to>", "c": "<Navigate>", "d": "<Redirect>", "correct": "B", "exp": "<Link> provides client-side navigation that updates the URL without a full page reload."},
                            {"text": "How do you access URL parameters in React Router v6?", "a": "this.props.params", "b": "useParams() hook", "c": "getParams()", "d": "window.location.params", "correct": "B", "exp": "The useParams() hook returns an object of key/value pairs from the dynamic URL segments."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    }
                ]
            },
            {
                "title": "Milestone 6: Frontend Tools & Deployment",
                "description": "Learn essential frontend tools — Git/GitHub, npm, bundlers (Vite/Webpack), testing, and deploying to Vercel/Netlify.",
                "order": 6,
                "topics": [
                    {
                        "title": "Git & GitHub for Frontend Developers",
                        "description": "Learn version control with Git — init, add, commit, branch, merge, pull requests, and GitHub collaboration workflows.",
                        "learning_objectives": "Initialize and manage Git repositories\nCreate branches and merge changes\nResolve merge conflicts\nCollaborate using GitHub pull requests",
                        "difficulty": "medium",
                        "estimated_time": 2.5,
                        "order": 1,
                        "videos": [
                            {"title": "Git and GitHub for Beginners - Crash Course", "url": "https://www.youtube.com/watch?v=RGOj5yH7evk"},
                            {"title": "Git Tutorial for Beginners - Full Course", "url": "https://www.youtube.com/watch?v=8JJ101D3knE"}
                        ],
                        "docs": [
                            {"title": "GitHub Docs - Getting Started", "url": "https://docs.github.com/en/get-started"},
                            {"title": "Pro Git Book", "url": "https://git-scm.com/book/en/v2"}
                        ],
                        "quiz_questions": [
                            {"text": "Which Git command creates a new branch?", "a": "git new branch", "b": "git branch <name>", "c": "git create <name>", "d": "git add branch", "correct": "B", "exp": "'git branch <name>' creates a new branch. Use 'git checkout -b <name>' to create and switch."},
                            {"text": "What does 'git pull' do?", "a": "Pushes local changes to remote", "b": "Fetches and merges remote changes into local branch", "c": "Deletes a branch", "d": "Creates a new repository", "correct": "B", "exp": "'git pull' is equivalent to 'git fetch' + 'git merge' — it downloads and integrates remote changes."},
                            {"text": "Which command stages all changed files for commit?", "a": "git commit -a", "b": "git add .", "c": "git stage all", "d": "git push .", "correct": "B", "exp": "'git add .' stages all modified and new files in the current directory for the next commit."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "NPM, Build Tools & Vite",
                        "description": "Learn npm package management, build tools, Vite for fast development, and modern frontend project structure.",
                        "learning_objectives": "Use npm to install and manage packages\nUnderstand package.json and node_modules\nSet up Vite for React projects\nUse environment variables and build scripts",
                        "difficulty": "medium",
                        "estimated_time": 2.0,
                        "order": 2,
                        "videos": [
                            {"title": "NPM Crash Course", "url": "https://www.youtube.com/watch?v=jHDhaSSKmB0"},
                            {"title": "Vite in 100 Seconds", "url": "https://www.youtube.com/watch?v=KCrXgy8qtjM"}
                        ],
                        "docs": [
                            {"title": "npm Docs", "url": "https://docs.npmjs.com/"},
                            {"title": "Vite Guide", "url": "https://vitejs.dev/guide/"}
                        ],
                        "quiz_questions": [
                            {"text": "Which file lists all project dependencies in a Node.js project?", "a": "index.js", "b": "package.json", "c": "node_modules.json", "d": "config.json", "correct": "B", "exp": "package.json is the manifest file that lists project metadata, dependencies, and scripts."},
                            {"text": "What command installs all dependencies listed in package.json?", "a": "npm start", "b": "npm build", "c": "npm install", "d": "npm run", "correct": "C", "exp": "'npm install' (or 'npm i') reads package.json and installs all listed dependencies."},
                            {"text": "What advantage does Vite offer over Webpack for development?", "a": "Better CSS support", "b": "Native ES module-based fast hot module replacement", "c": "More plugins", "d": "Easier deployment", "correct": "B", "exp": "Vite uses native ES modules for instant server start and blazing-fast HMR during development."},
                        ],
                        "challenges": [],
                        "notes": "",
                        "cheat_sheet": ""
                    },
                    {
                        "title": "Responsive Design & Deployment",
                        "description": "Build responsive websites using media queries, mobile-first design, and deploy to Vercel, Netlify, or GitHub Pages.",
                        "learning_objectives": "Write media queries for responsive design\nImplement mobile-first CSS strategies\nDeploy React apps to Vercel or Netlify\nOptimize performance with lazy loading and code splitting",
                        "difficulty": "medium",
                        "estimated_time": 3.0,
                        "order": 3,
                        "videos": [
                            {"title": "Responsive Web Design Tutorial", "url": "https://www.youtube.com/watch?v=srvUrASNj0s"},
                            {"title": "Deploy React App to Vercel", "url": "https://www.youtube.com/watch?v=FvsvHzcwOmQ"}
                        ],
                        "docs": [
                            {"title": "MDN - Responsive Design", "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design"},
                            {"title": "Vercel Deployment Docs", "url": "https://vercel.com/docs"}
                        ],
                        "quiz_questions": [
                            {"text": "What CSS feature is used to apply styles based on screen size?", "a": "Flexbox", "b": "Grid", "c": "Media queries", "d": "Animations", "correct": "C", "exp": "Media queries (@media) apply CSS rules conditionally based on device characteristics like screen width."},
                            {"text": "What does 'mobile-first' design mean?", "a": "Only designing for mobile phones", "b": "Starting the design for small screens first, then scaling up", "c": "Using mobile frameworks only", "d": "Testing only on mobile devices", "correct": "B", "exp": "Mobile-first means designing for the smallest screens first, then using media queries to enhance for larger screens."},
                            {"text": "Which meta tag is essential for responsive design?", "a": "<meta charset>", "b": "<meta viewport>", "c": "<meta description>", "d": "<meta author>", "correct": "B", "exp": "<meta name='viewport' content='width=device-width, initial-scale=1.0'> ensures proper scaling on mobile devices."},
                        ],
                        "challenges": [],
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
            # Check if roadmap already exists
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

            # Insert topics
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

                # Insert Resources (docs links)
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

        print(f"\n🎉 Frontend Developer Roadmap seeded successfully!")
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
