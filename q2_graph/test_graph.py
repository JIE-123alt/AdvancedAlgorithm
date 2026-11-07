"""Unit tests for DirectedGraph and the course system.   Run:  python -m unittest -v"""

import unittest

from course import CORE, ELECTIVE, Course
from course_system import CourseSystemError
from graph import DirectedGraph, VertexNotFoundError
from sample_data import build_sample_system


class DirectedGraphTests(unittest.TestCase):

    def setUp(self):
        self.g = DirectedGraph()
        for v in "ABCD":
            self.g.addVertex(v)
        self.g.addEdge("A", "B")
        self.g.addEdge("A", "C")
        self.g.addEdge("B", "D")
        self.g.addEdge("C", "D")

    def test_add_vertex_twice(self):
        self.assertFalse(self.g.addVertex("A"))
        self.assertEqual(len(self.g), 4)

    def test_incoming_and_outgoing(self):
        self.assertEqual(self.g.listIncomingAdjacentVertex("D"), ["B", "C"])
        self.assertEqual(self.g.listIncomingAdjacentVertex("A"), [])
        self.assertEqual(self.g.listOutgoingAdjacentVertex("A"), ["B", "C"])

    def test_edges_are_directed(self):
        self.assertTrue(self.g.hasEdge("A", "B"))
        self.assertFalse(self.g.hasEdge("B", "A"))

    def test_duplicate_edge_ignored(self):
        self.assertFalse(self.g.addEdge("A", "B"))
        self.assertEqual(self.g.listOutgoingAdjacentVertex("A"), ["B", "C"])

    def test_unknown_vertex_raises(self):
        with self.assertRaises(VertexNotFoundError):
            self.g.addEdge("A", "Z")
        with self.assertRaises(VertexNotFoundError):
            self.g.listIncomingAdjacentVertex("Z")

    def test_remove_edge_updates_both_directions(self):
        self.assertTrue(self.g.removeEdge("B", "D"))
        self.assertEqual(self.g.listIncomingAdjacentVertex("D"), ["C"])
        self.assertEqual(self.g.listOutgoingAdjacentVertex("B"), [])
        self.assertFalse(self.g.removeEdge("B", "D"))

    def test_degrees(self):
        self.assertEqual((self.g.inDegree("D"), self.g.outDegree("A")), (2, 2))

    def test_has_path(self):
        self.assertTrue(self.g.hasPath("A", "D"))
        self.assertFalse(self.g.hasPath("D", "A"))
        self.assertTrue(self.g.hasPath("A", "A"))
    def test_graph_accepts_any_hashable_vertex(self):
        g = DirectedGraph()
        for n in (1, 2, 3):
            g.addVertex(n)
        g.addEdge(1, 2)
        g.addEdge(3, 2)
        self.assertEqual(g.listIncomingAdjacentVertex(2), [1, 3])


class CourseTests(unittest.TestCase):

    def test_elective_profile_hides_details(self):
        elective = Course("CS402", "AI", 3, ELECTIVE, "secret description")
        self.assertIn("AI", elective.profile())
        self.assertNotIn("secret description", elective.profile())
        self.assertIn("secret description", elective.details())     # details ignore level

    def test_core_profile_shows_everything(self):
        core = Course("CS101", "Intro", 4, CORE, "learn python")
        self.assertEqual(core.profile(), core.details())

    def test_code_normalised_and_invalid_rejected(self):
        self.assertEqual(Course(" cs101 ", "Intro", 4, CORE).course_code, "CS101")
        for bad in (("", "x", 3), ("A1", "", 3), ("A1", "x", 0), ("A1", "x", -2), ("A1", "x", 2.5)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                Course(*bad, CORE)


class CourseSystemTests(unittest.TestCase):

    def setUp(self):
        self.system = build_sample_system()

    def codes(self, courses):
        return [c.course_code for c in courses]

    def test_sample_data_size_within_brief(self):
        self.assertTrue(5 <= len(self.system.list_courses()) <= 10)

    def test_prerequisites_are_incoming_edges(self):
        self.assertEqual(self.codes(self.system.list_prerequisites("CS301")), ["CS201", "MA101"])
        self.assertEqual(self.codes(self.system.list_prerequisites("CS101")), [])

    def test_unlocked_courses_are_outgoing_edges(self):
        self.assertEqual(self.codes(self.system.list_unlocked_courses("CS201")), ["CS301", "CS302"])
        self.assertEqual(self.codes(self.system.list_unlocked_courses("CS401")), [])

    def test_lookup_is_case_insensitive(self):
        self.assertEqual(self.system.get_course("cs201").course_code, "CS201")

    def test_unknown_course(self):
        with self.assertRaises(CourseSystemError):
            self.system.get_course("XX999")

    def test_add_course_on_demand(self):
        self.system.add_course(Course("CS499", "Capstone", 6, CORE))
        self.assertEqual(self.system.list_prerequisites("CS499"), [])
        with self.assertRaises(CourseSystemError):
            self.system.add_course(Course("cs499", "Duplicate", 3, CORE))

    def test_tenth_course_allowed_but_eleventh_rejected(self):
        self.system.add_course(Course("CS499", "Capstone", 6, CORE))
        with self.assertRaises(CourseSystemError):
            self.system.add_course(Course("CS500", "Extra", 3, ELECTIVE))
        self.assertEqual(len(self.system.list_courses()), 10)

    def test_add_and_remove_prerequisite(self):
        self.system.add_prerequisite("CS401", "CS301")
        self.assertIn("CS301", self.codes(self.system.list_prerequisites("CS401")))
        self.assertIn("CS401", self.codes(self.system.list_unlocked_courses("CS301")))
        self.system.remove_prerequisite("CS401", "CS301")
        self.assertNotIn("CS301", self.codes(self.system.list_prerequisites("CS401")))

    def test_invalid_prerequisites_rejected(self):
        with self.assertRaises(CourseSystemError):          # itself
            self.system.add_prerequisite("CS201", "CS201")
        with self.assertRaises(CourseSystemError):          # already present
            self.system.add_prerequisite("CS201", "CS101")
        with self.assertRaises(CourseSystemError):          # direct cycle
            self.system.add_prerequisite("CS101", "CS201")
        with self.assertRaises(CourseSystemError):          # indirect cycle: CS402 needs CS301 needs CS201
            self.system.add_prerequisite("CS201", "CS402")
        with self.assertRaises(CourseSystemError):          # removing a link that does not exist
            self.system.remove_prerequisite("CS101", "CS401")

if __name__ == "__main__":
    unittest.main()
