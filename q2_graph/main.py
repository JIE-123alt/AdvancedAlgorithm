"""main.py - menu-driven University Course Prerequisite System (Question 2).

Run:  python main.py
"""

from course import CORE, ELECTIVE, Course
from course_system import CourseSystemError
from sample_data import build_sample_system


# --------------------------------------------------------------------------- input helpers
def ask_course(system, label="Enter Course Code: "):
    """Ask for a course code; print an error and return None if it does not exist."""
    try:
        return system.get_course(input(label))
    except CourseSystemError as error:
        print(error)
        return None


def ask_text(label, allow_blank=False):
    while True:
        value = input(label).strip()
        if value or allow_blank:
            return value
        print("  Input cannot be empty.")


def ask_positive_int(label):
    while True:
        raw = input(label).strip()
        try:
            value = int(raw)
            if value > 0:
                return value
        except ValueError:
            pass
        print("  Please enter a positive whole number.")


def ask_level():
    while True:
        choice = input("Level - 1. Core  2. Elective: ").strip()
        if choice == "1":
            return CORE
        if choice == "2":
            return ELECTIVE
        print("  Please enter 1 or 2.")


def describe(course):
    """'CS201 (Data Structures)' - compact form used in lists of related courses."""
    return f"{course.course_code} ({course.course_name})"


# --------------------------------------------------------------------------- mandatory features
def view_all_courses(system):
    print("\nAvailable Courses:")
    for number, course in enumerate(system.list_courses(), start=1):
        print(f"{number}. {course.short()}")


def view_course_details(system):
    course = ask_course(system)
    if course:
        print("\n" + course.details())          # full information, level ignored


def view_prerequisites(system):
    course = ask_course(system)
    if course is None:
        return
    prerequisites = system.list_prerequisites(course.course_code)
    print(f"Prerequisites for {course.short()}:")
    if not prerequisites:
        print("- None (no prerequisite required)")
    for prerequisite in prerequisites:
        print(f"- {describe(prerequisite)}")


def view_unlocked_courses(system):
    course = ask_course(system)
    if course is None:
        return
    unlocked = system.list_unlocked_courses(course.course_code)
    print(f"Courses unlocked by {course.short()}:")
    if not unlocked:
        print("- None (this course is not a prerequisite of any other course)")
    for item in unlocked:
        print(f"- {describe(item)}")


# --------------------------------------------------------------------------- advanced features
def view_course_profile(system):
    course = ask_course(system)
    if course:
        print("\n" + course.profile())          # electives hide their details


def add_new_course(system):
    code = ask_text("New Course Code: ")
    name = ask_text("Course Name: ")
    credits = ask_positive_int("Credit Hours: ")
    level = ask_level()
    description = ask_text("Description (optional): ", allow_blank=True)
    try:
        course = Course(code, name, credits, level, description)
        system.add_course(course)
    except (ValueError, CourseSystemError) as error:
        print(f"Could not add course: {error}")
        return
    print(f"Course {course.short()} added. It has no prerequisites yet - use "
          f"'Add a Prerequisite to a Course' to link it.")


def add_prerequisite(system):
    course = ask_course(system, "Course that needs a prerequisite (X): ")
    if course is None:
        return
    prerequisite = ask_course(system, "Course to add as its prerequisite (Y): ")
    if prerequisite is None:
        return
    try:
        system.add_prerequisite(course.course_code, prerequisite.course_code)
    except CourseSystemError as error:
        print(error)
        return
    print(f"Done: {prerequisite.course_code} is now a prerequisite of {course.course_code}.")


def remove_prerequisite(system):
    course = ask_course(system, "Course to remove a prerequisite from (X): ")
    if course is None:
        return
    prerequisite = ask_course(system, "Prerequisite to remove (Y): ")
    if prerequisite is None:
        return
    try:
        system.remove_prerequisite(course.course_code, prerequisite.course_code)
    except CourseSystemError as error:
        print(error)
        return
    print(f"Done: {prerequisite.course_code} is no longer a prerequisite of {course.course_code}.")


# --------------------------------------------------------------------------- main loop
MENU = [
    ("1", "View All Courses", view_all_courses),
    ("2", "View Course Details", view_course_details),
    ("3", "View Prerequisites of a Course", view_prerequisites),
    ("4", "View Courses Unlocked by a Course", view_unlocked_courses),
    ("5", "View Course Profile (electives hide details)", view_course_profile),
    ("6", "Add a New Course", add_new_course),
    ("7", "Add a Prerequisite to a Course", add_prerequisite),
    ("8", "Remove a Prerequisite from a Course", remove_prerequisite),
]


def main():
    system = build_sample_system()
    actions = {key: action for key, _, action in MENU}
    try:
        while True:
            print("\n==== University Course Prerequisite System ====")
            for key, title, _ in MENU:
                print(f"{key}. {title}")
            print("0. Exit")
            choice = input("Enter choice: ").strip()
            if choice == "0":
                print("Exiting program. Goodbye!")
                break
            action = actions.get(choice)
            if action is None:
                print("Invalid choice, please enter a number from the menu.")
                continue
            action(system)
    except (EOFError, KeyboardInterrupt):          # Ctrl+D / Ctrl+Z / Ctrl+C
        print("\nInput closed. Exiting program......")


if __name__ == "__main__":
    main()
