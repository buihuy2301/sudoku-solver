"""Integration tests for Sudoku solver components"""

import pytest

from sudoku_solver.algorithms.backtracking import BacktrackingSolver
from sudoku_solver.algorithms.backtracking_mrv import BacktrackingMRVSolver
from sudoku_solver.algorithms.dancing_links import DancingLinksSolver
from sudoku_solver.algorithms.naked_singles import NakedSinglesSolver
from sudoku_solver.core.sudoku import SudokuBoard
from sudoku_solver.utils.puzzle_loader import PuzzleLoader
from sudoku_solver.utils.validators import Validators

from .conftest import PuzzleValidator


class TestAlgorithmIntegration:
    """Test integration of all algorithm components."""

    def test_all_algorithms_available(self):
        """Test that all algorithm classes can be imported and instantiated."""
        algorithms = [
            BacktrackingSolver,
            BacktrackingMRVSolver,
            NakedSinglesSolver,
            DancingLinksSolver,
        ]

        board = SudokuBoard()
        for AlgoClass in algorithms:
            solver = AlgoClass(board.copy())
            assert solver is not None
            assert hasattr(solver, "solve")
            assert hasattr(solver, "get_statistics")


class TestPuzzleLoaderIntegration:
    """Test puzzle loader integration with solvers."""

    def test_load_and_solve_workflow(self, test_puzzles):
        """Test complete workflow: load puzzle -> solve -> validate."""
        puzzle_str = test_puzzles["easy"]["puzzle"]

        # Load
        board = PuzzleLoader.from_string(puzzle_str)
        assert board is not None

        # Solve
        solver = DancingLinksSolver(board)
        assert solver.solve() == True

        # Validate
        assert PuzzleValidator.is_valid_solution(solver.board)

    def test_exemplar_puzzles_all_solvable(self):
        """Test that all exemplar puzzles can be solved."""
        exemplars = PuzzleLoader.exemplars()

        for difficulty, puzzle_str in exemplars.items():
            # Clean up the puzzle string (remove dots)
            puzzle_str = puzzle_str.replace(".", "0")

            board = PuzzleLoader.from_string(puzzle_str)
            solver = DancingLinksSolver(board)
            assert solver.solve() == True, f"Failed to solve {difficulty} puzzle"


class TestValidatorIntegration:
    """Test validators work with solved boards."""

    def test_validation_after_solving(self, easy_board):
        """Test that solutions pass validation."""
        solver = DancingLinksSolver(easy_board)
        solver.solve()

        is_valid, msg = Validators.is_valid_puzzle(solver.board)
        assert is_valid == True

        # Custom validation
        assert PuzzleValidator.rows_valid(solver.board)
        assert PuzzleValidator.cols_valid(solver.board)
        assert PuzzleValidator.boxes_valid(solver.board)

    def test_invalid_solution_detection(self):
        """Test that invalid solutions are detected."""
        # Create a board with duplicate values
        grid = [[0] * 9 for _ in range(9)]
        board = SudokuBoard(grid)

        # Force invalid state
        board.board[0] = [1, 2, 3, 4, 5, 6, 7, 8, 1]  # Duplicate 1

        is_valid = PuzzleValidator.rows_valid(board)
        assert is_valid == False


class TestMultipleSolvesSequential:
    """Test solving multiple puzzles sequentially."""

    def test_solve_multiple_puzzles(self, test_puzzles):
        """Test solving multiple puzzles in sequence."""
        difficulties = ["easy", "medium"]
        solver_class = DancingLinksSolver

        for difficulty in difficulties:
            puzzle_str = test_puzzles[difficulty]["puzzle"]
            board = PuzzleLoader.from_string(puzzle_str)
            solver = solver_class(board)

            assert solver.solve() == True
            assert solver.board.is_solved()
            assert PuzzleValidator.is_valid_solution(solver.board)

    def test_solve_same_puzzle_with_different_algorithms(self, easy_board):
        """Test solving same puzzle with different algorithms."""
        algorithms = [
            BacktrackingSolver,
            BacktrackingMRVSolver,
            DancingLinksSolver,
        ]

        solutions = []

        for AlgoClass in algorithms:
            board_copy = easy_board.copy()
            solver = AlgoClass(board_copy)

            assert solver.solve() == True
            assert solver.board.is_solved()
            solutions.append(solver.board.to_string())

        # All should produce identical solutions
        assert all(sol == solutions[0] for sol in solutions)


class TestSolverReset:
    """Test solver resets work correctly."""

    def test_reset_state_between_solves(self, easy_board):
        """Test that solver can be reset and solved again."""
        solver = DancingLinksSolver(easy_board)

        # First solve
        assert solver.solve() == True
        first_solution = solver.board.to_string()

        # Reset
        solver.reset()
        assert not solver.board.is_solved()

        # Solve again
        assert solver.solve() == True
        second_solution = solver.board.to_string()

        # Solutions should be identical
        assert first_solution == second_solution

    def test_reset_statistics(self, easy_board):
        """Test that statistics are reset properly."""
        solver = DancingLinksSolver(easy_board)

        solver.solve_with_timer()
        stats1 = solver.get_statistics()

        solver.reset()
        solver.solve_with_timer()
        stats2 = solver.get_statistics()

        # Both solves should have similar stats
        assert stats1["cells_assigned"] == stats2["cells_assigned"]


class TestCandidateTracking:
    """Test candidate tracking across solves."""

    def test_candidates_initialized(self, easy_board):
        """Test that candidates are properly initialized."""
        assert easy_board.candidates is not None
        assert len(easy_board.candidates) == 9
        assert all(len(row) == 9 for row in easy_board.candidates)

    def test_candidates_reduce_after_assignment(self):
        """Test that candidates reduce when values are assigned."""
        board = SudokuBoard()

        # Get candidates for empty cell
        candidates_before = len(board.candidates[0][1])
        assert candidates_before == 9  # All values possible

        # Set a value
        board.set_value(0, 0, 5)

        # Cell in same row should have 5 removed
        candidates_after = len(board.candidates[0][1])
        assert candidates_after == 8  # One value removed


class TestStatisticsCollection:
    """Test statistics collection across all solvers."""

    @pytest.mark.parametrize(
        "solver_class",
        [
            BacktrackingSolver,
            BacktrackingMRVSolver,
            DancingLinksSolver,
        ],
    )
    def test_statistics_structure(self, solver_class, easy_board):
        """Test that all solvers return consistent statistics."""
        board = easy_board.copy()
        solver = solver_class(board)
        solver.solve_with_timer()
        stats = solver.get_statistics()

        # Check structure
        assert isinstance(stats, dict)
        assert "solved" in stats
        assert "execution_time" in stats

        # Check values
        assert stats["solved"] == True
        assert stats["execution_time"] >= 0
        assert isinstance(stats["execution_time"], (int, float))

    def test_execution_time_consistency(self, easy_board):
        """Test that execution times are consistent across solves."""
        solver = DancingLinksSolver(easy_board)

        times = []
        for _ in range(3):
            solver.reset()
            solver.solve_with_timer()
            stats = solver.get_statistics()
            times.append(stats["execution_time"])

        # Times should be in reasonable range (dancing links is fast)
        assert all(0 <= t < 10 for t in times)


class TestBoardStateConsistency:
    """Test board state remains consistent throughout operations."""

    def test_initial_board_preserved(self, easy_board):
        """Test that initial board state is preserved."""
        # Copy original board state
        original_empty = set(easy_board.get_empty_cells())
        original_values = {}
        for r in range(9):
            for c in range(9):
                if easy_board.board[r][c] != 0:
                    original_values[(r, c)] = easy_board.board[r][c]

        # Solve
        solver = DancingLinksSolver(easy_board)
        solver.solve()

        # Check initial values are preserved
        for (r, c), value in original_values.items():
            assert easy_board.board[r][c] == value

    def test_solution_contains_no_zeros(self, easy_board):
        """Test that solutions contain no empty cells."""
        solver = DancingLinksSolver(easy_board)
        solver.solve()

        empty_cells = 0
        for row in solver.board.board:
            empty_cells += row.count(0)

        assert empty_cells == 0


class TestAlgorithmCorrectness:
    """Test algorithm correctness on various inputs."""

    def test_solutions_are_unique(self, easy_board):
        """Test that solutions don't have duplicates."""
        solver = DancingLinksSolver(easy_board)
        solver.solve()

        # Check rows
        for row in solver.board.board:
            unique_values = set(row)
            non_zero = [x for x in row if x != 0]
            assert len(non_zero) == len(set(non_zero))

        # Check columns
        for col in range(9):
            column = [solver.board.board[row][col] for row in range(9)]
            non_zero = [x for x in column if x != 0]
            assert len(non_zero) == len(set(non_zero))

        # Check boxes
        for box_r in range(3):
            for box_c in range(3):
                box = []
                for r in range(box_r * 3, box_r * 3 + 3):
                    for c in range(box_c * 3, box_c * 3 + 3):
                        box.append(solver.board.board[r][c])
                non_zero = [x for x in box if x != 0]
                assert len(non_zero) == len(set(non_zero))

    def test_solution_satisfies_constraints(self, hard_board):
        """Test that hard puzzle solutions satisfy all Sudoku constraints."""
        solver = DancingLinksSolver(hard_board)
        solver.solve()

        # All cells should be filled
        empty_count = 0
        for r in range(9):
            for c in range(9):
                if solver.board.board[r][c] == 0:
                    empty_count += 1
        assert empty_count == 0

        # All values should be 1-9
        for r in range(9):
            for c in range(9):
                val = solver.board.board[r][c]
                assert 1 <= val <= 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
