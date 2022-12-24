from django.db import models

# Create your models here.

class Student:
    def __init__(self, name, regno, student_set) -> None:
        self.name = name
        self.regno = regno
        self.student_set = student_set

import weakref

class OrderedSet(object):
    """
    A linked-list with a uniqueness constraint and O(1) lookups/removal.

    Modification during iteration is partially supported.  If you
    remove the just yielded element, it will go on to what was the
    next element.  If you remove the next element, it will use the
    new next element.  If you remove both, you get an error.
    """
    def __init__(self, iterable=(), allow_move=True):
        self._map = {}
        self._start = _SentinalNode()
        self._end = _SentinalNode()
        self._start.next = self._end
        self._end.prev = self._start
        self._allow_move = allow_move
        self.extend(iterable)

    def __contains__(self, element):
        return element in self._map

    def __eq__(self, other):
        raise TypeError("OrderedSet does not support comparisons")

    def __hash__(self):
        raise TypeError("OrderedSet is not hashable")

    def __iter__(self):
        curnode = self._start
        nextnode = curnode.next

        while True:
            if hasattr(curnode, 'next'):
                curnode = curnode.next
            elif hasattr(nextnode, 'next'):
                curnode = nextnode
            else:
                raise RuntimeError("OrderedSet modified inappropriately "
                    "during iteration")

            if type(curnode) is _SentinalNode:
                return

            nextnode = curnode.next
            yield curnode.content

    def __reversed__(self):
        curnode = self._end
        prevnode = curnode.prev

        while True:
            if hasattr(curnode, 'prev'):
                curnode = curnode.prev
            elif hasattr(prevnode, 'prev'):
                curnode = prevnode
            else:
                raise RuntimeError("OrderedSet modified inappropriately "
                    "during iteration")

            if type(curnode) is _SentinalNode:
                return

            prevnode = curnode.prev
            yield curnode.content

    def __len__(self):
        return len(self._map)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def append(self, element):
        """Add an element to the right side of the OrderedSet."""
        self._insertatnode(self._end.prev, element)

    def appendleft(self, element):
        """Add an element to the left side of the OrderedSet."""
        self._insertatnode(self._start, element)

    def clear(self):
        """Remove all elements from the OrderedSet."""
        while self:
            self.pop()

    def extend(self, iterable):
        """Extend the right side of the OrderedSet with elements from the iterable."""
        for element in iterable:
            self.append(element)

    def extendleft(self, iterable):
        """Extend the left side of the OrderedSet with elements from the iterable."""
        for element in iterable:
            self.appendleft(element)

    def insertleft(self, poselement, element):
        """Inserts element immediately left of poselement's position."""
        self._insertatnode(self._map[poselement].prev, element)

    def insertright(self, poselement, element):
        """Inserts element immediately right of poselement's position."""
        self._insertatnode(self._map[poselement], element)

    def _insertatnode(self, node, element):
        left = node
        right = node.next
        if element in self._map:
            if self._allow_move:
                self.remove(element)
            else:
                raise ValueError("element already exists")

        newnode = _Node()
        newnode.content = element
        newnode.prev = right.prev
        newnode.next = right
        right.prev = newnode
        left.next = newnode
        self._map[element] = newnode

    def pop(self):
        """Remove and return the rightmost element."""
        element = self._end.prev.content
        self.remove(element)
        return element

    def popleft(self):
        """Remove and return the leftmost element."""
        element = self._start.next.content
        self.remove(element)
        return element

    def remove(self, element):
        """Remove element from the OrderedSet."""
        node = self._map.pop(element)
        assert type(node) is not _SentinalNode
        left = node.prev
        right = node.next
        left.next = right
        right.prev = node.prev
        del node.prev
        del node.next


class _Node(object):
    __slots__ = '_prev', 'next', 'content', '__weakref__'
    # A weakref is used for prev so as to avoid creating cycles.

    def _prev_get(self):
        return self._prev()
    def _prev_set(self, value):
        self._prev = weakref.ref(value)
    def _prev_del(self):
        del self._prev
    prev = property(_prev_get, _prev_set, _prev_del)


class _SentinalNode(_Node):
    __slots__ = []