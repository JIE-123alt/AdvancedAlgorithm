"""course_system.py - the course-prerequisite domain layer built ON TOP of DirectedGraph.

Convention used everywhere:   prerequisite  ->  course
i.e. an edge  CS201 -> CS301  means "CS201 must be completed before CS301".

    prerequisites of X   =  INCOMING neighbours of X   (listIncomingAdjacentVertex)
    courses unlocked by X =  OUTGOING neighbours of X   (listOutgoingAdjacentVertex)

The graph itself stays generic; every course rule (no self-prerequisite, no duplicate,
no circular prerequisite) is enforced here.
"""

from graph import DirectedGraph


MAX_COURSES = 10            # the coursework allows at most ten courses


class CourseSystemError(Exception):
    """A user-facing problem such as an unknown course code or an invalid prerequisite."""


class CoursePrerequisiteSystem:
    """Courses plus their prerequisite relationships."""

    def __init__(self):
        self._graph = DirectedGraph()
        self._by_code = {}       # course code -> Course, O(1) lookup

    # ------------------------------------------------------------------ courses
    def add_course(self, course):
        """Register a course (creates a new vertex). Codes must be unique."""
        if course.course_code in self._by_code:
            raise CourseSystemError(f"Course {course.course_code} already exists.")
        if len(self._by_code) >= MAX_COURSES:
            raise CourseSystemError(f"The system allows at most {MAX_COURSES} courses.")
        self._graph.addVertex(course)
        self._by_code[course.course_code] = course

    def get_course(self, course_code):
        """Look a course up by code (case-insensitive)."""
        course = self._by_code.get(course_code.strip().upper())
        if course is None:
            raise CourseSystemError(f"Course '{course_code.strip().upper()}' was not found.")
        return course

    def list_courses(self):
        return self._graph.vertices()

    # ------------------------------------------------------------------ prerequisites
    def list_prerequisites(self, course_code):
        """Courses that must be completed BEFORE `course_code` (its incoming edges)."""
        return self._graph.listIncomingAdjacentVertex(self.get_course(course_code))

    def list_unlocked_courses(self, course_code):
        """Courses for which `course_code` is a prerequisite (its outgoing edges)."""
        return self._graph.listOutgoingAdjacentVertex(self.get_course(course_code))

    def add_prerequisite(self, course_code, prerequisite_code):
        """Make `prerequisite_code` a prerequisite of `course_code` (new edge Y -> X)."""
        course = self.get_course(course_code)
        prerequisite = self.get_course(prerequisite_code)
        if course == prerequisite:
            raise CourseSystemError("A course cannot be a prerequisite of itself.")
        if self._graph.hasEdge(prerequisite, course):
            raise CourseSystemError(
                f"{prerequisite.course_code} is already a prerequisite of {course.course_code}.")
        # Y -> X closes a loop exactly when X can already reach Y.
        if self._graph.hasPath(course, prerequisite):
            raise CourseSystemError(
                f"Not allowed: {prerequisite.course_code} already depends on "
                f"{course.course_code} (directly or indirectly), so this would create a "
                f"prerequisite loop.")
        self._graph.addEdge(prerequisite, course)

    def remove_prerequisite(self, course_code, prerequisite_code):
        """Remove `prerequisite_code` from the prerequisites of `course_code` (delete edge Y -> X)."""
        course = self.get_course(course_code)
        prerequisite = self.get_course(prerequisite_code)
        if not self._graph.removeEdge(prerequisite, course):
            raise CourseSystemError(
                f"{prerequisite.course_code} is not a prerequisite of {course.course_code}.")
