"""Naked singles constraint propagation algorithm."""

from ..core.solver_base import SudokuSolver


class NakedSinglesSolver(SudokuSolver):
    """
    Constraint propagation using naked singles technique.

    Fast for easy-medium puzzles but gets stuck on hard puzzles.
    No backtracking - pure constraint propagation.
    """

    def solve(self) -> bool:
        """
        Solve using naked singles constraint propagation.

        Returns:
            True if solved, False if stuck (but didn't fail)
        """
        # Initialize candidates if not already done
        self._initialize_candidates()

        changed = True
        while changed and not self.board.is_solved():
            changed = False

            # Find and assign naked singles
            naked_singles = self._find_naked_singles()
            if naked_singles:
                changed = True
                for row, col, value in naked_singles:
                    if self.board.board[row][col] == 0:
                        self.board.board[row][col] = value
                        self.board.candidates[row][col] = set()
                        self._record_assignment(row, col, value)
                        self._eliminate_candidates(row, col, value)

        # Return True if solved, False if stuck but valid
        return self.board.is_solved()

    def _initialize_candidates(self) -> None:
        """Initialize candidates for all cells."""
        self.board.candidates = [[set() for _ in range(9)] for _ in range(9)]

        for r in range(9):
            for c in range(9):
                if self.board.board[r][c] == 0:
                    candidates = set(range(1, 10))

                    # Remove values in row
                    for col in range(9):
                        if self.board.board[r][col] != 0:
                            candidates.discard(self.board.board[r][col])

                    # Remove values in column
                    for row in range(9):
                        if self.board.board[row][c] != 0:
                            candidates.discard(self.board.board[row][c])

                    # Remove values in box
                    box_r = (r // 3) * 3
                    box_c = (c // 3) * 3
                    for row in range(box_r, box_r + 3):
                        for col in range(box_c, box_c + 3):
                            if self.board.board[row][col] != 0:
                                candidates.discard(self.board.board[row][col])

                    self.board.candidates[r][c] = candidates

    def _eliminate_candidates(self, row: int, col: int, value: int) -> None:
        """
        Remove a value from candidates of all peers.

        Args:
            row: Row index
            col: Column index
            value: Value that was assigned
        """
        # Remove from row
        for c in range(9):
            if c != col:
                self.board.candidates[row][c].discard(value)

        # Remove from column
        for r in range(9):
            if r != row:
                self.board.candidates[r][col].discard(value)

        # Remove from box
        box_r = (row // 3) * 3
        box_c = (col // 3) * 3
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if r != row or c != col:
                    self.board.candidates[r][c].discard(value)

    def _find_naked_singles(self) -> list:
        """
        Find all naked singles (cells with only one candidate).

        Returns:
            List of (row, col, value) tuples for naked singles found
        """
        naked_singles = []

        for r in range(9):
            for c in range(9):
                if self.board.board[r][c] == 0:
                    candidates = self.board.candidates[r][c]
                    if len(candidates) == 1:
                        value = list(candidates)[0]
                        naked_singles.append((r, c, value))
                    elif len(candidates) == 0:
                        # Contradiction - no valid candidates
                        self.board.board = None  # Mark as invalid
                        return []

        return naked_singles

    def _propagate_constraints(self) -> bool:
        """
        Propagate constraints until fixed point.

        Returns:
            False if contradiction found, True otherwise
        """
        changed = True
        while changed:
            changed = False

            # Find and process naked singles
            naked_singles = self._find_naked_singles()

            if not naked_singles and self.board.board is None:
                # Contradiction found
                return False

            for row, col, value in naked_singles:
                if self.board.board[row][col] == 0:
                    self.board.board[row][col] = value
                    self.board.candidates[row][col] = set()
                    self._record_assignment(row, col, value)
                    self._eliminate_candidates(row, col, value)
                    changed = True

        return True
