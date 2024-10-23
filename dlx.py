# Implementation of Donald Knuth's Algorithm X with Daning Links in Python
# https://arxiv.org/pdf/cs/0011047.pdf
# Implementation derived from implementation by Nicolau Werneck
# https://xor0110.wordpress.com/2011/05/09/dlx-in-python-with-actual-pointers/

class Node:
    """Node in doubly linked list.

    Attributes:
        column: A pointer to the column header.
        down: A pointer to the node below the current node.
        left: A pointer to the node to the left of the current node.
        right: A pointer to the node to the right of the current node.
        up: A pointer to the node above the current node.
    """

    def __init__(self):

        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.column = self

    def left_sweep(self):
        """Does a left sweep over nodes in the doubly linked list."""
        x = self.left
        while x != self:
            yield x
            x = x.left
        return

    def right_sweep(self):
        """Does a right sweep over nodes in the doubly linked list."""
        x = self.right
        while x != self:
            yield x
            x = x.right
        return

    def down_sweep(self):
        """Does a down sweep over nodes in the doubly linked list."""
        x = self.down
        while x != self:
            yield x
            x = x.down
        return

    def up_sweep(self):
        """Does an up sweep over nodes in the doubly linked list."""
        x = self.up
        while x != self:
            yield x
            x = x.up
        return

class DLX:
    """Implementation of Don Knuth's DLX algorithm.

    Uses the Dancing Links as described in this paper:
        https://arxiv.org/pdf/cs/0011047.pdf.

    Attributes:
        h: Root node for the list header.
        hdic: Dictionary with each key being a column header and its value the
              pointer to the column in the list header.
        kcount: List with Number of calls to the search method for each
                level inthe recursion.
    """

    def __init__(self, labels, rows):
        """Construct the incidence matrix as doubly linked lists.

        Args:
            labels: List with labels of each column.
            rows: List of lists. Each sublist represent a row in the incidence
                  matrix, and must contain the labels of the elements.
        """
        self.h = Node()
        self.hdic = dict()
        self.kcount = [0]

        h = self.h
        hdic = self.hdic

        # make header row
        for label in labels:
            # append new column to end of the doubly linked list
            h.left.right = Node()
            h.left.right.right = h
            h.left.right.left = h.left
            h.left = h.left.right

            h.left.label = label
            h.left.size = 0
            hdic[label] = h.left

        for row in rows:
            last = None
            for rlabel in row:
                element = Node()

                # get column header
                element.column = hdic[rlabel]
                element.column.size += 1

                # append Node to bottom of column
                element.column.up.down = element
                element.up = element.column.up
                element.down = element.column
                element.column.up = element

                if last:
                    element.left = last
                    element.right = last.right
                    last.right.left = element
                    last.right = element
                last = element

    def cover(self, c):
        """Cover column c.

        Args:
            c: Column to cover.
        """
        c.right.left = c.left
        c.left.right = c.right
        for i in c.down_sweep():
            for j in i.right_sweep():
                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1

    def uncover(self, c):
        """Uncover column c.

        Args:
            c: Column to uncover
        """
        for i in c.up_sweep():
            for j in i.left_sweep():
                j.column.size += 1
                j.down.up = j
                j.up.down = j
        c.right.left = c
        c.left.right = c

    def search(self, k=0, o=None):
        """Recursive search algorithm to find exact cover solutions.

        Args:
            k: Level of the recursive call. Should initially be called with
               k=0.
            o: List of rows in the (partial) solution up to this point.

        Yields:
            List of rows constituting a solution.
        """
        if o is None:
            o = []

        if len(self.kcount) <= k:
            self.kcount.append(0)
        self.kcount[k] += 1

        if self.h.right == self.h:
            yield o
            return

        # choose the smallest column
        size = 10**9
        for column in self.h.right_sweep():
            if column.size < size:
                size = column.size
                c = column

        self.cover(c)
        for r in c.down_sweep():
            o_k = r
            for j in r.right_sweep():
                self.cover(j.column)
            yield from self.search(k=k+1, o=o+[o_k])

            for j in r.left_sweep():
                self.uncover(j.column)
        self.uncover(c)

    def get_row_labels(self, row, sort=True, key=str, reverse=False):
        """Get labels of a row in the incidence matrix.

        Args:
            row: Node in the incidence matrix.
            sort (bool): Sort labels.
            key (func): Key function to sort on (Default: str)
            reverse (bool, optional): Reverse sort.

        Returns:
            List of all column labels in the row.
        """
        labels = [row.column.label]
        for r in row.right_sweep():
            labels.append(r.column.label)

        if sort:
            labels = sorted(labels, key=key, reverse=reverse)
        return labels

    def generate_solutions(self, **kw):
        """Wrapper for search method

        Runs search iterator and gets the labels for the rows that are pat of
        the solution. Then yields the solution

        Args:
            **kw: Keyword arguments for get_row_labels.

        Yields:
            Solution found by the algorithm
        """
        self.kcount = [0]

        for solution in self.search():
            yield [self.get_row_labels(s, **kw) for s in solution]

    def run_search(self, **kw):
        """Wrapper for search method.

        Runs search iterator, gets the labels for the rows that are part of the
        solution, and returns the list of solutions.

        Args:
            **kw: Keyword arguments for get_row_labels.

        Returns:
            List of solutions.
        """
        self.kcount = [0] # reset call counter

        solutions = []
        for solution in self.search():
            solutions.append([self.get_row_labels(s, **kw) for s in solution])

        return solutions

if __name__ == '__main__':

    # test problem
    COLS = [1, 2, 3, 4, 5, 6, 7]
    ROWS = [[1, 4, 7],
            [1, 4],
            [4, 5, 7],
            [3, 5, 6],
            [2, 3, 6, 7],
            [2, 7]]

    COVER = DLX(COLS, ROWS)

    SOLUTIONS = COVER.run_search()

    print("Found solution:", SOLUTIONS)
