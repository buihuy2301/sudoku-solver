"""Dancing Links algorithm (Knuth's Algorithm X) for Sudoku."""

from ..core.solver_base import SudokuSolver
from ..core.sudoku import SudokuBoard


class Node:
    """A node in the doubly-linked list matrix."""

    def __init__(self):
        """Initialize a node."""
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.column = None
        self.row_id = None  # For data rows only


class Column:
    """Column header in the dancing links matrix."""

    def __init__(self, constraint_id):
        """Initialize column header."""
        self.node = Node()
        self.node.column = self
        self.size = 0
        self.constraint_id = constraint_id  # (type, value) e.g., ('cell', r, c)


class DancingLinksSolver(SudokuSolver):
    """
    Dancing Links algorithm (Algorithm X) for Sudoku solving.

    Uses Knuth's Algorithm X with double-ended doubly-linked lists.
    Extremely efficient for constraint satisfaction problems like Sudoku.
    """

    def __init__(self, board: SudokuBoard):
        """Initialize solver."""
        super().__init__(board)
        # Use the original board directly, not the copy
        # This ensures the solution is written to the board passed by the user
        self.board = board
        self.original_board = board.copy()
        self.columns = []
        self.column_map = {}
        self.header = None
        self.solution = []
        self.placement_rows = {}
        self._prepare_matrix()

    def _prepare_matrix(self):
        """Prepare the sparse matrix for Algorithm X."""
        # Create header node
        self.header = Node()

        # Create 324 constraint columns
        for r in range(9):
            for c in range(9):
                col = Column(("cell", r, c))
                self.columns.append(col)
                self.column_map[("cell", r, c)] = col
                col.node.right = self.header
                col.node.left = self.header.left
                self.header.left.right = col.node
                self.header.left = col.node

        for r in range(9):
            for d in range(1, 10):
                col = Column(("row", r, d))
                self.columns.append(col)
                self.column_map[("row", r, d)] = col
                col.node.right = self.header
                col.node.left = self.header.left
                self.header.left.right = col.node
                self.header.left = col.node

        for c in range(9):
            for d in range(1, 10):
                col = Column(("col", c, d))
                self.columns.append(col)
                self.column_map[("col", c, d)] = col
                col.node.right = self.header
                col.node.left = self.header.left
                self.header.left.right = col.node
                self.header.left = col.node

        for b in range(9):
            for d in range(1, 10):
                col = Column(("box", b, d))
                self.columns.append(col)
                self.column_map[("box", b, d)] = col
                col.node.right = self.header
                col.node.left = self.header.left
                self.header.left.right = col.node
                self.header.left = col.node

        # Create rows for all possible placements
        for r in range(9):
            for c in range(9):
                for d in range(1, 10):
                    nodes = []

                    # Cell constraint
                    cell_col = self.column_map[("cell", r, c)]
                    cell_node = self._add_node(cell_col)
                    nodes.append(cell_node)

                    # Row constraint
                    row_col = self.column_map[("row", r, d)]
                    row_node = self._add_node(row_col)
                    nodes.append(row_node)

                    # Column constraint
                    col_col = self.column_map[("col", c, d)]
                    col_node = self._add_node(col_col)
                    nodes.append(col_node)

                    # Box constraint
                    box = (r // 3) * 3 + (c // 3)
                    box_col = self.column_map[("box", box, d)]
                    box_node = self._add_node(box_col)
                    nodes.append(box_node)

                    # Link row nodes horizontally (circular)
                    for i, node in enumerate(nodes):
                        node.left = nodes[i - 1]
                        node.right = nodes[(i + 1) % len(nodes)]

                    # Store placement for reference
                    self.placement_rows[(r, c, d)] = nodes[0]

    def _add_node(self, column):
        """Add a node to a column."""
        node = Node()
        node.column = column

        # Add to column (insert before header)
        node.up = column.node.up
        node.down = column.node
        column.node.up.down = node
        column.node.up = node

        column.size += 1
        return node

    def _cover(self, column):
        """Cover a column and all conflicting rows."""
        column.node.right.left = column.node.left
        column.node.left.right = column.node.right

        cur = column.node.down
        while cur != column.node:
            node = cur.right
            while node != cur:
                node.column.size -= 1
                node.down.up = node.up
                node.up.down = node.down
                node = node.right
            cur = cur.down

    def _uncover(self, column):
        """Uncover a column (reverse of cover)."""
        cur = column.node.up
        while cur != column.node:
            node = cur.left
            while node != cur:
                node.column.size += 1
                node.down.up = node
                node.up.down = node
                node = node.left
            cur = cur.up

        column.node.right.left = column.node
        column.node.left.right = column.node

    def _select_column(self):
        """Select column with minimum size (heuristic)."""
        min_size = float("inf")
        min_col = None

        node = self.header.right
        while node != self.header:
            if node.column.size < min_size:
                min_size = node.column.size
                min_col = node.column
            node = node.right

        return min_col

    def _search(self):
        """Recursive search using Algorithm X."""
        # Check if solved
        if self.header.right == self.header:
            return True

        # Select column with minimum size
        col = self._select_column()

        if col.size == 0:
            return False

        self._cover(col)

        # Try each row in the column
        cur = col.node.down
        while cur != col.node:
            self.solution.append(cur)

            # Cover all columns in this row
            node = cur.right
            while node != cur:
                self._cover(node.column)
                node = node.right

            self.guesses += 1

            if self._search():
                return True

            # Uncover columns (backtrack)
            self.solution.pop()
            self.backtracks += 1

            node = cur.left
            while node != cur:
                self._uncover(node.column)
                node = node.left

            cur = cur.down

        self._uncover(col)
        return False

    def solve(self) -> bool:
        """
        Solve using Dancing Links algorithm (Algorithm X).

        Returns:
            True if solved, False if no solution exists
        """
        # Handle pre-filled cells by forcing their selection
        for r in range(9):
            for c in range(9):
                if self.board.board[r][c] != 0:
                    d = self.board.board[r][c]
                    if (r, c, d) in self.placement_rows:
                        row_node = self.placement_rows[(r, c, d)]
                        self.solution.append(row_node)

                        # Cover all 4 constraints for this placement
                        node = row_node
                        for _ in range(4):
                            self._cover(node.column)
                            node = node.right

        # Run the recursive search algorithm
        success = self._search()

        if success:
            # Extract solution from all selected rows
            for row_node in self.solution:
                # Traverse the 4 nodes in this row
                r, c, d = None, None, None
                node = row_node
                for _ in range(4):
                    constraint_type = node.column.constraint_id[0]
                    if constraint_type == "cell":
                        r = node.column.constraint_id[1]
                        c = node.column.constraint_id[2]
                    elif constraint_type == "row":
                        d = node.column.constraint_id[2]
                    node = node.right

                # Set the cell value if we found valid r, c, d
                if r is not None and c is not None and d is not None:
                    self.board.board[r][c] = d
                    self._record_assignment(r, c, d)

        return success

    def reset(self) -> None:
        """Reset solver to initial state and rebuild the matrix structure."""
        # Call parent's reset to reset board and statistics
        super().reset()
        
        # Reset solver-specific state
        self.solution = []
        
        # Rebuild the matrix structure
        self.columns = []
        self.column_map = {}
        self.header = None
        self.placement_rows = {}
        self._prepare_matrix()
