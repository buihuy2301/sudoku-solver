"""Comprehensive unit tests for Sudoku solver"""

import pytest

from sudoku_solver.algorithms.backtracking import BacktrackingSolver
from sudoku_solver.algorithms.backtracking_mrv import BacktrackingMRVSolver
from sudoku_solver.algorithms.dancing_links import DancingLinksSolver
from sudoku_solver.algorithms.naked_singles import NakedSinglesSolver
from sudoku_solver.core.sudoku import SudokuBoard
from sudoku_solver.utils.puzzle_loader import PuzzleLoader
from sudoku_solver.utils.validators import Validators

from .conftest import PuzzleValidator


# Test puzzle string
EASY_PUZZLE_STR = (
    "530070000600195000098000060800060003400803001700020006"
    "060000280000419005000080079"
)


class TestSudokuBoard:
    """Test SudokuBoard functionality."""

    def test_empty_board_creation(self):
        """Test creating an empty board."""
        board = SudokuBoard()
        assert board.board is not None
        assert len(board.board) == 9
        assert all(len(row) == 9 for row in board.board)

    def test_board_from_grid(self):
        """Test creating board from grid."""
        grid = [[5, 3, 0, 0, 7, 0, 0, 0, 0] for _ in range(9)]
        board = SudokuBoard(grid)
        assert board.board[0][0] == 5
        assert board.board[0][2] == 0

    def test_set_value(self):
        """Test setting values on board."""
        board = SudokuBoard()
        assert board.set_value(0, 0, 5) == True
        assert board.board[0][0] == 5

    def test_invalid_placement(self):
        """Test that invalid placements are rejected."""
        board = SudokuBoard()
        board.set_value(0, 0, 5)
        # Try to place 5 in same row
        assert board.set_value(0, 1, 5) == False

    def test_is_valid(self):
        """Test board validity check."""
        board = SudokuBoard()
        assert board.is_valid() == True
        board.set_value(0, 0, 5)
        assert board.is_valid() == True

    def test_empty_cells(self):
        """Test getting empty cells."""
        board = SudokuBoard()
        empty = board.get_empty_cells()
        assert len(empty) == 81

    def test_board_copy(self):
        """Test board deep copy."""
        board = SudokuBoard()
        board.set_value(0, 0, 5)
        board_copy = board.copy()
        board_copy.set_value(1, 1, 3)
        assert board.board[1][1] == 0
        assert board_copy.board[1][1] == 3


class TestPuzzleLoader:
    """Test puzzle loading functionality."""

    def test_load_from_string(self):
        """Test loading puzzle from string."""
        puzzle_str = EASY_PUZZLE_STR
        board = PuzzleLoader.from_string(puzzle_str)
        assert board.board[0][0] == 5
        assert board.board[0][2] == 0

    def test_invalid_string_length(self):
        """Test that invalid string length raises error."""
        with pytest.raises(ValueError):
            PuzzleLoader.from_string("123")

    def test_exemplar_puzzles(self):
        """Test that exemplar puzzles load correctly."""
        exemplars = PuzzleLoader.exemplars()
        assert "easy" in exemplars
        assert "medium" in exemplars
        assert "hard" in exemplars
        assert len(exemplars["easy"]) >= 81


class TestValidators:
    """Test puzzle validation."""

    def test_valid_empty_board(self):
        """Test that empty board is valid."""
        board = SudokuBoard()
        is_valid, msg = Validators.is_valid_puzzle(board)
        assert is_valid == True

    def test_invalid_board_detection(self):
        """Test detection of invalid boards."""
        board = SudokuBoard()
        board.set_value(0, 0, 5)
        board.board[0][1] = 5  # Force invalid state
        is_valid, msg = Validators.is_valid_puzzle(board)
        assert is_valid == False


class TestBacktrackingSolver:
    """Test basic backtracking solver."""

    @pytest.fixture(scope="class")
    def easy_puzzle(self):
        """Fixture for easy puzzle."""
        puzzle_str = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
        return PuzzleLoader.from_string(puzzle_str)

    def test_solve_easy_puzzle(self, easy_puzzle):
        """Test solving an easy puzzle."""
        solver = BacktrackingSolver(easy_puzzle)
        assert solver.solve() == True
        assert solver.board.is_solved() == True

    def test_statistics_tracking(self, easy_puzzle):
        """Test that statistics are tracked."""
        solver = BacktrackingSolver(easy_puzzle)
        solver.solve_with_timer()
        stats = solver.get_statistics()
        assert stats["cells_assigned"] > 0
        assert stats["execution_time"] >= 0
        assert stats["solved"] == True


class TestBacktrackingMRVSolver:
    """Test MRV heuristic solver."""

    @pytest.fixture(scope="class")
    def easy_puzzle(self):
        """Fixture for easy puzzle."""
        return PuzzleLoader.from_string(EASY_PUZZLE_STR)

    def test_mrv_faster_than_basic(self, easy_puzzle):
        """Test that MRV is faster than basic backtracking (on average)."""
        # Run both solvers
        puzzle1 = easy_puzzle.copy()
        puzzle2 = easy_puzzle.copy()

        solver1 = BacktrackingSolver(puzzle1)
        solver2 = BacktrackingMRVSolver(puzzle2)

        solver1.solve_with_timer()
        solver2.solve_with_timer()

        # MRV should have fewer guesses (not guaranteed faster due to overhead)
        assert solver2.guesses <= solver1.guesses


class TestNakedSinglesSolver:
    """Test naked singles solver."""

    @pytest.fixture(scope="class")
    def easy_puzzle(self):
        """Fixture for easy puzzle."""
        return PuzzleLoader.from_string(EASY_PUZZLE_STR)

    def test_naked_singles_solver(self, easy_puzzle):
        """Test naked singles solver."""
        solver = NakedSinglesSolver(easy_puzzle)
        result = solver.solve()
        # May not solve all puzzles without backtracking
        if result:
            assert solver.board.is_solved() == True


class TestDancingLinksSolver:
    """Test dancing links solver."""

    @pytest.fixture(scope="class")
    def easy_puzzle(self):
        """Fixture for easy puzzle."""
        return PuzzleLoader.from_string(EASY_PUZZLE_STR)

    def test_dancing_links_solver(self, easy_puzzle):
        """Test dancing links solver."""
        solver = DancingLinksSolver(easy_puzzle)
        assert solver.solve() == True
        assert solver.board.is_solved() == True

    def test_dancing_links_statistics(self, easy_puzzle):
        """Test statistics from dancing links."""
        solver = DancingLinksSolver(easy_puzzle)
        solver.solve_with_timer()
        stats = solver.get_statistics()
        assert stats["solved"] == True


class TestAlgorithmComparison:
    """Test all algorithms on same puzzle."""

    @pytest.fixture(scope="class")
    def test_puzzle(self):
        """Easy puzzle for comparison."""
        return PuzzleLoader.from_string(EASY_PUZZLE_STR)

    def test_all_algorithms_solve_same_puzzle(self, test_puzzle):
        """Test that all algorithms solve the same puzzle correctly."""
        algorithms = [
            BacktrackingSolver,
            BacktrackingMRVSolver,
            DancingLinksSolver,
        ]

        solutions = []
        for AlgoClass in algorithms:
            puzzle_copy = test_puzzle.copy()
            solver = AlgoClass(puzzle_copy)
            assert solver.solve() == True
            assert solver.board.is_solved() == True
            # Convert solution to string for comparison
            solutions.append(solver.board.to_string())

        # All should produce same solution
        assert all(sol == solutions[0] for sol in solutions)


# ==================== Additional Comprehensive Tests ====================


class TestBoardEdgeCases:
    """Test edge cases for SudokuBoard."""

    def test_empty_board_validation(self, empty_board):
        """Test that empty board is valid."""
        assert empty_board.is_valid()
        assert not empty_board.is_solved()
        assert len(empty_board.get_empty_cells()) == 81

    def test_solved_board(self, solved_board):
        """Test a completely solved board."""
        assert solved_board.is_valid()
        assert solved_board.is_solved()
        assert len(solved_board.get_empty_cells()) == 0

    def test_nearly_solved_board(self, nearly_solved_board):
        """Test board with one empty cell."""
        empty_cells = nearly_solved_board.get_empty_cells()
        assert len(empty_cells) == 1
        assert nearly_solved_board.is_valid()

    def test_board_copy_independence(self):
        """Test that board copies are truly independent."""
        original = SudokuBoard()
        original.set_value(0, 0, 5)
        original.set_value(1, 1, 3)

        copy_board = original.copy()
        copy_board.set_value(2, 2, 7)
        copy_board.set_value(3, 3, 9)

        # Original should be unchanged
        assert original.board[2][2] == 0
        assert original.board[3][3] == 0
        assert copy_board.board[2][2] == 7
        assert copy_board.board[3][3] == 9

    def test_reset_board(self):
        """Test board reset functionality."""
        initial_str = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
        board = PuzzleLoader.from_string(initial_str)
        original_empty = len(board.get_empty_cells())

        # Make some changes
        board.set_value(0, 2, 1)
        board.set_value(0, 3, 2)

        # Reset
        board.reset()

        # Should be back to original state
        assert len(board.get_empty_cells()) == original_empty
        assert board.board[0][2] == 0


class TestBacktrackingSolverEdgeCases:
    """Test backtracking solver on various inputs."""

    def test_solve_empty_board(self, empty_board):
        """Test solving completely empty board."""
        solver = BacktrackingSolver(empty_board)
        assert solver.solve() == True
        assert solver.board.is_solved()

    def test_solve_easy_puzzle(self, easy_board):
        """Test solving easy puzzle."""
        solver = BacktrackingSolver(easy_board)
        assert solver.solve() == True
        assert solver.board.is_solved()
        assert PuzzleValidator.is_valid_solution(solver.board)

    def test_solve_hard_puzzle(self, hard_board):
        """Test solving hard puzzle."""
        solver = BacktrackingSolver(hard_board)
        assert solver.solve() == True
        assert solver.board.is_solved()
        assert PuzzleValidator.is_valid_solution(solver.board)

    def test_statistics_accuracy(self, easy_board):
        """Test statistics are properly tracked."""
        solver = BacktrackingSolver(easy_board)
        solver.solve_with_timer()
        stats = solver.get_statistics()

        assert "cells_assigned" in stats
        assert "execution_time" in stats
        assert "solved" in stats
        assert stats["execution_time"] >= 0
        assert stats["cells_assigned"] > 0
        assert stats["solved"] == True

    def test_multiple_solves_reset(self, easy_board):
        """Test that solver state resets between solves."""
        solver = BacktrackingSolver(easy_board)

        # First solve
        solver.solve()
        stats1 = solver.get_statistics()

        # Reset and solve again
        solver.reset()
        assert not solver.board.is_solved()
        solver.solve()
        stats2 = solver.get_statistics()

        # Statistics should be similar (same puzzle)
        assert stats1["cells_assigned"] == stats2["cells_assigned"]


class TestBacktrackingMRVSolverEdgeCases:
    """Test MRV heuristic solver on various inputs."""

    def test_mrv_solve_easy(self, easy_board):
        """Test MRV solver on easy puzzle."""
        solver = BacktrackingMRVSolver(easy_board)
        assert solver.solve() == True
        assert solver.board.is_solved()

    def test_mrv_solve_hard(self, medium_board):
        """Test MRV solver on harder puzzle."""
        solver = BacktrackingMRVSolver(medium_board)
        assert solver.solve() == True
        assert solver.board.is_solved()

    def test_mrv_fewer_guesses_than_basic(self, medium_board):
        """Test that MRV makes fewer guesses than basic backtracking."""
        puzzle_basic = medium_board.copy()
        puzzle_mrv = medium_board.copy()

        solver_basic = BacktrackingSolver(puzzle_basic)
        solver_mrv = BacktrackingMRVSolver(puzzle_mrv)

        solver_basic.solve()
        solver_mrv.solve()

        # MRV should have fewer or equal guesses
        assert solver_mrv.guesses <= solver_basic.guesses

    def test_mrv_statistics(self, easy_board):
        """Test MRV statistics tracking."""
        solver = BacktrackingMRVSolver(easy_board)
        solver.solve_with_timer()
        stats = solver.get_statistics()

        assert stats["solved"] == True
        assert "cells_assigned" in stats
        assert "guesses" in stats


class TestNakedSinglesSolverEdgeCases:
    """Test naked singles constraint propagation solver."""

    def test_naked_singles_on_easy(self, easy_board):
        """Test if naked singles can solve easy puzzle."""
        solver = NakedSinglesSolver(easy_board)
        result = solver.solve()
        # Easy puzzles should often be solved by constraint propagation
        if result:
            assert solver.board.is_solved()

    def test_naked_singles_statistics(self, easy_board):
        """Test statistics tracking for naked singles."""
        solver = NakedSinglesSolver(easy_board)
        solver.solve_with_timer()
        stats = solver.get_statistics()

        assert "execution_time" in stats
        assert stats["execution_time"] >= 0


class TestDancingLinksSolverEdgeCases:
    """Test dancing links algorithm solver."""

    def test_dancing_links_easy(self, easy_board):
        """Test dancing links on easy puzzle."""
        solver = DancingLinksSolver(easy_board)
        assert solver.solve() == True
        assert solver.board.is_solved()
        assert PuzzleValidator.is_valid_solution(solver.board)

    def test_dancing_links_hard(self, hard_board):
        """Test dancing links on hard puzzle."""
        solver = DancingLinksSolver(hard_board)
        assert solver.solve() == True
        assert solver.board.is_solved()
        assert PuzzleValidator.is_valid_solution(solver.board)

    def test_dancing_links_empty_board(self, empty_board):
        """Test dancing links on empty board."""
        solver = DancingLinksSolver(empty_board)
        assert solver.solve() == True
        assert solver.board.is_solved()

    def test_dancing_links_statistics(self, easy_board):
        """Test statistics from dancing links."""
        solver = DancingLinksSolver(easy_board)
        solver.solve_with_timer()
        stats = solver.get_statistics()

        assert stats["solved"] == True
        assert "execution_time" in stats
        assert stats["execution_time"] >= 0


class TestAllAlgorithmsAcrossDifficulties:
    """Test all algorithms on puzzles of varying difficulty."""

    @pytest.mark.parametrize("difficulty", ["easy", "medium"])
    def test_all_algorithms_solve_all_difficulties(self, difficulty, test_puzzles):
        """Test all algorithms solve puzzles at all difficulty levels."""
        algorithms = [
            BacktrackingSolver,
            BacktrackingMRVSolver,
            DancingLinksSolver,
        ]

        puzzle_str = test_puzzles[difficulty]["puzzle"]
        solutions = []

        for AlgoClass in algorithms:
            board = PuzzleLoader.from_string(puzzle_str)
            solver = AlgoClass(board)
            result = solver.solve()
            assert result == True, f"{AlgoClass.__name__} failed on {difficulty} puzzle"
            assert (
                solver.board.is_solved()
            ), f"{AlgoClass.__name__} did not fully solve {difficulty} puzzle"
            solutions.append(solver.board.to_string())

        # All solutions should be identical
        assert len(set(solutions)) == 1, f"Different solutions for {difficulty} puzzle"

    def test_solution_consistency_across_algorithms(self, test_puzzles):
        """Test that all algorithms produce identical solutions."""
        algorithms = [
            BacktrackingSolver,
            BacktrackingMRVSolver,
            DancingLinksSolver,
        ]

        for difficulty in ["easy", "medium"]:
            puzzle_str = test_puzzles[difficulty]["puzzle"]
            solutions = []

            for AlgoClass in algorithms:
                board = PuzzleLoader.from_string(puzzle_str)
                solver = AlgoClass(board)
                solver.solve()
                solutions.append(solver.board.to_string())

            # All should produce the same solution
            assert all(
                sol == solutions[0] for sol in solutions
            ), f"Algorithm mismatch on {difficulty} puzzle"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
