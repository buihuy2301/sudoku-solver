"""Shared test fixtures and configuration for pytest."""

import pytest

from sudoku_solver.core.sudoku import SudokuBoard
from sudoku_solver.utils.puzzle_loader import PuzzleLoader


@pytest.fixture(scope="session")
def test_puzzles():
    """
    Fixture providing test puzzles of various difficulties.

    Returns:
        Dictionary with difficulty levels as keys and puzzle data as values.
    """
    return {
        "easy": {
            "puzzle": "530070000600195000098000060800060003400803001700020006060000280000419005000080079",
            "empty_cells": 51,
            "description": "Easy puzzle from exemplars - many singles",
        },
        "medium": {
            "puzzle": "003020600900305001001806400008102900700000008006708200002609500800203006005010300",
            "empty_cells": 45,
            "description": "Medium puzzle - requires some deduction",
        },
    }


@pytest.fixture(scope="session")
def edge_case_puzzles():
    """
    Fixture providing edge case puzzles for testing robustness.

    Returns:
        Dictionary with edge case puzzle data.
    """
    return {
        "empty_board": {
            "puzzle": "000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "empty_cells": 81,
            "description": "Completely empty board",
        },
        "nearly_solved": {
            "puzzle": "123456789456789123789123456234567891567891234891234567345678912678912345912345670",
            "empty_cells": 1,
            "description": "Almost completely solved - only one cell empty",
        },
        "already_solved": {
            "puzzle": "123456789456789123789123456234567891567891234891234567345678912678912345912345678",
            "empty_cells": 0,
            "description": "Already completely solved",
        },
        "single_empty": {
            "puzzle": "534678912672195348198342567859761423426853791713924856961537284287419635345286179",
            "empty_cells": 1,
            "description": "Valid puzzle with single empty cell",
        },
    }


@pytest.fixture
def easy_board(test_puzzles):
    """Fixture providing an easy puzzle board."""
    return PuzzleLoader.from_string(test_puzzles["easy"]["puzzle"])


@pytest.fixture
def medium_board(test_puzzles):
    """Fixture providing a medium puzzle board."""
    return PuzzleLoader.from_string(test_puzzles["medium"]["puzzle"])


@pytest.fixture
def hard_board():
    """Fixture providing a hard puzzle board."""
    from sudoku_solver.utils.puzzle_loader import PuzzleLoader

    exemplars = PuzzleLoader.exemplars()
    return PuzzleLoader.from_string(exemplars["hard"])


@pytest.fixture
def evil_board():
    """Fixture providing an evil/expert puzzle board."""
    from sudoku_solver.utils.puzzle_loader import PuzzleLoader

    exemplars = PuzzleLoader.exemplars()
    return PuzzleLoader.from_string(exemplars["expert"])


@pytest.fixture
def empty_board():
    """Fixture providing a completely empty board."""
    return SudokuBoard()


@pytest.fixture
def solved_board(test_puzzles):
    """Fixture providing a solved board."""
    solved_str = "534678912672195348198342567859761423426853791713924856961537284287419635345286179"
    return PuzzleLoader.from_string(solved_str)


@pytest.fixture
def nearly_solved_board(edge_case_puzzles):
    """Fixture providing a nearly solved board."""
    return PuzzleLoader.from_string(edge_case_puzzles["nearly_solved"]["puzzle"])


class PuzzleValidator:
    """Utility class for validating puzzle solutions."""

    @staticmethod
    def rows_valid(board: SudokuBoard) -> bool:
        """Check all rows contain valid values."""
        for row in board.board:
            non_zero = [x for x in row if x != 0]
            if len(non_zero) != len(set(non_zero)):
                return False
        return True

    @staticmethod
    def cols_valid(board: SudokuBoard) -> bool:
        """Check all columns contain valid values."""
        for col in range(9):
            column = [board.board[row][col] for row in range(9)]
            non_zero = [x for x in column if x != 0]
            if len(non_zero) != len(set(non_zero)):
                return False
        return True

    @staticmethod
    def boxes_valid(board: SudokuBoard) -> bool:
        """Check all 3x3 boxes contain valid values."""
        for box_row in range(3):
            for box_col in range(3):
                box = []
                for r in range(box_row * 3, box_row * 3 + 3):
                    for c in range(box_col * 3, box_col * 3 + 3):
                        box.append(board.board[r][c])
                non_zero = [x for x in box if x != 0]
                if len(non_zero) != len(set(non_zero)):
                    return False
        return True

    @staticmethod
    def is_valid_solution(board: SudokuBoard) -> bool:
        """Check if board is a valid complete solution."""
        return (
            PuzzleValidator.rows_valid(board)
            and PuzzleValidator.cols_valid(board)
            and PuzzleValidator.boxes_valid(board)
            and board.is_solved()
        )
