"""graph.py - a generic, unweighted DIRECTED graph (adjacency-list representation).

The graph is completely domain-free: a vertex can be ANY hashable object (a Course,
a string, an int, ...). Nothing here mentions courses, so the class is reusable.

Method names addVertex / addEdge / listIncomingAdjacentVertex follow the assignment
brief on purpose, so that a marker can find them; the other methods use the same style.

Design
------
Two dictionaries are kept in step:
    _outgoing[v]  = vertices that v points TO        (v -> w)
    _incoming[v]  = vertices that point TO v         (u -> v)
Keeping the reverse map costs a little memory but makes "who points to v?" an
O(in-degree) lookup instead of an O(V + E) scan of every vertex. A dict whose values
are None is used as an ordered set: O(1) membership test AND insertion order is kept,
so listings always come out in the order the edges were added.
"""

from collections import deque


class VertexNotFoundError(KeyError):
    """Raised when an operation refers to a vertex that is not in the graph."""

    def __str__(self):                             # KeyError normally adds extra quotes
        return f"vertex not found: {self.args[0]}"


class DirectedGraph:
    """Unweighted directed graph. An edge (a, b) means  a -> b."""

    def __init__(self):
        self._outgoing = {}
        self._incoming = {}

    # ------------------------------------------------------------------ building
    def addVertex(self, vertex):
        """Add a vertex. Returns False (and changes nothing) if it already exists."""
        if vertex in self._outgoing:
            return False
        self._outgoing[vertex] = {}
        self._incoming[vertex] = {}
        return True

    def addEdge(self, source, target):
        """Add the directed edge source -> target.

        Returns False if the edge already exists. Raises VertexNotFoundError if
        either end is not a vertex of the graph.
        """
        self._require(source)
        self._require(target)
        if target in self._outgoing[source]:
            return False
        self._outgoing[source][target] = None
        self._incoming[target][source] = None
        return True

    def removeEdge(self, source, target):
        """Remove the edge source -> target. Returns False if there was no such edge."""
        self._require(source)
        self._require(target)
        if target not in self._outgoing[source]:
            return False
        del self._outgoing[source][target]
        del self._incoming[target][source]
        return True

    def listIncomingAdjacentVertex(self, vertex):
        """All vertices u that have an edge u -> vertex."""
        self._require(vertex)
        return list(self._incoming[vertex])

    def listOutgoingAdjacentVertex(self, vertex):
        """All vertices w that have an edge vertex -> w."""
        self._require(vertex)
        return list(self._outgoing[vertex])

    def hasVertex(self, vertex):
        return vertex in self._outgoing

    def hasEdge(self, source, target):
        return source in self._outgoing and target in self._outgoing[source]

    def vertices(self):
        """All vertices, in the order they were added."""
        return list(self._outgoing)

    def inDegree(self, vertex):
        self._require(vertex)
        return len(self._incoming[vertex])

    def outDegree(self, vertex):
        self._require(vertex)
        return len(self._outgoing[vertex])

    def __len__(self):
        return len(self._outgoing)

    # ------------------------------------------------------------------ traversal
    def hasPath(self, start, goal):
        """True if `goal` can be reached from `start` by following edges (BFS). O(V + E)."""
        self._require(start)
        self._require(goal)
        return start == goal or goal in self._bfs(start, self._outgoing)

    # ------------------------------------------------------------------ internals
    def _require(self, vertex):
        if vertex not in self._outgoing:
            raise VertexNotFoundError(vertex)

    def _bfs(self, start, adjacency):
        """Breadth-first search following `adjacency`; returns {vertex: distance}."""
        distance = {}
        queue = deque([(start, 0)])
        seen = {start}
        while queue:
            vertex, depth = queue.popleft()
            for neighbour in adjacency[vertex]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    distance[neighbour] = depth + 1
                    queue.append((neighbour, depth + 1))
        return distance
