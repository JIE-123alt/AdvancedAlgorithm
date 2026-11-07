"""course.py - entity class for one university course."""

CORE = "Core"                   # compulsory course
ELECTIVE = "Elective"           # optional course
LEVELS = (CORE, ELECTIVE)


class Course:
    """One course offered by the university.

    course_code   str  unique identifier, e.g. "CS201" (stored in upper case)
    course_name   str  e.g. "Data Structures"
    credit_hours  int  weight of the course, a positive whole number
    level         str  CORE or ELECTIVE
    description   str  short summary of the content

    A Course is used directly as a vertex of the graph. A plain object can be a
    dictionary key, and the course system keeps exactly one Course object for each course code.
    """

    def __init__(self, course_code, course_name, credit_hours, level, description=""):
        code = str(course_code).strip().upper()
        if not code:
            raise ValueError("Course code cannot be empty.")
        name = str(course_name).strip()
        if not name:
            raise ValueError("Course name cannot be empty.")
        # `type(x) is not int` also rejects True and False
        if type(credit_hours) is not int or credit_hours <= 0:
            raise ValueError("Credit hours must be a positive whole number.")
        if level not in LEVELS:
            raise ValueError(f"Level must be {CORE} or {ELECTIVE}.")
        self._course_code = code
        self.course_name = name
        self.credit_hours = credit_hours
        self.level = level
        self.description = str(description).strip()

    def short(self):
        """e.g. 'CS201 - Data Structures'"""
        return f"{self.course_code} - {self.course_name}"

    def details(self):
        """FULL information, ignoring the level (used by the mandatory 'view details')."""
        return (f"Course Code   : {self.course_code}\n"
                f"Course Name   : {self.course_name}\n"
                f"Credit Hours  : {self.credit_hours}\n"
                f"Level         : {self.level}\n"
                f"Description   : {self.description or '-'}")

    def profile(self):
        """Profile that RESPECTS the level: electives show only their name, core shows all."""
        if self.level == ELECTIVE:
            return (f"Course Name   : {self.course_name}\n"
                    f"(Elective course - other details are hidden)")
        return self.details()

    @property
    def course_code(self):
        """Read-only code used to identify the course."""
        return self._course_code