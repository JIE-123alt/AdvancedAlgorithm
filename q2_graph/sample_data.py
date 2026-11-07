"""sample_data.py - the pre-defined courses and prerequisite links (9 courses)."""

from course import CORE, ELECTIVE, Course
from course_system import CoursePrerequisiteSystem

COURSES = [
    Course("CS101", "Introduction to Programming", 4, CORE,
           "Variables, control flow, functions and basic problem solving in Python."),
    Course("MA101", "Discrete Mathematics", 3, CORE,
           "Logic, sets, relations, graphs and counting techniques."),
    Course("CS201", "Data Structures", 4, CORE,
           "Lists, stacks, queues, trees, hash tables and graphs."),
    Course("CS202", "Object-Oriented Programming", 3, CORE,
           "Classes, inheritance, polymorphism and design principles."),
    Course("CS301", "Algorithms", 4, CORE,
           "Algorithm design, complexity analysis, sorting and graph algorithms."),
    Course("CS302", "Database Systems", 3, CORE,
           "Relational model, SQL, normalisation and transactions."),
    Course("CS401", "Software Engineering", 3, CORE,
           "Requirements, design, testing and teamwork on a software project."),
    Course("CS402", "Artificial Intelligence", 3, ELECTIVE,
           "Search, knowledge representation and introductory machine learning."),
    Course("CS403", "Cloud Computing", 3, ELECTIVE,
           "Virtualisation, containers and cloud service models."),
]

# (course, prerequisite) pairs - read as "course requires prerequisite"
PREREQUISITES = [
    ("CS201", "CS101"),
    ("CS202", "CS101"),
    ("CS301", "CS201"),
    ("CS301", "MA101"),
    ("CS302", "CS201"),
    ("CS401", "CS202"),
    ("CS401", "CS302"),
    ("CS402", "CS301"),
    ("CS403", "CS302"),
]


def build_sample_system():
    """Create a CoursePrerequisiteSystem pre-loaded with the sample data."""
    system = CoursePrerequisiteSystem()
    for course in COURSES:
        system.add_course(course)
    for course_code, prerequisite_code in PREREQUISITES:
        system.add_prerequisite(course_code, prerequisite_code)
    return system
