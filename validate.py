#!/usr/bin/env python3
"""Quick validation tests"""

import sys

from sudoku_solver.algorithms import BacktrackingSolver, DancingLinksSolver
from sudoku_solver.core import SudokuBoard
from sudoku_solver.utils import PuzzleLoader

sys.path.insert(0, "/Users/huybq/Documents/dev-dir/sudoku-solver")

# Test puzzle string
TEST_PUZZLE = (
    "530070000600195000098000060800060003400803001700020006"
    "060000280000419005000080079"
)

print("=" * 60)
print("Implementation Validation")
print("=" * 60)

# Test 1: SudokuBoard
print("\n[1] Testing SudokuBoard...")
try:
    board = SudokuBoard()
    board.set_value(0, 0, 5)
    assert board.board[0][0] == 5
    assert board.is_valid()
    print("✓ SudokuBoard: OK")
except Exception as e:
    print(f"✗ SudokuBoard: FAILED - {e}")
    sys.exit(1)

# Test 2: PuzzleLoader
print("[2] Testing PuzzleLoader...")
try:
    puzzle_str = TEST_PUZZLE
    board = PuzzleLoader.from_string(puzzle_str)
    assert board.board[0][0] == 5
    assert board.board[0][2] == 0
    exemplars = PuzzleLoader.exemplars()
    assert "easy" in exemplars
    print("✓ PuzzleLoader: OK")
except Exception as e:
    print(f"✗ PuzzleLoader: FAILED - {e}")
    sys.exit(1)

# Test 3: Basic Backtracking Solver
print("[3] Testing BacktrackingSolver...")
try:
    puzzle_str = TEST_PUZZLE
    board = PuzzleLoader.from_string(puzzle_str)
    solver = BacktrackingSolver(board)
    print("  Solving puzzle...")
    result = solver.solve_with_timer()
    if result and solver.board.is_solved():
        stats = solver.get_statistics()
        print(f"  ✓ Solved in {stats['execution_time']:.4f}s")
        print(f"    - Cells assigned: {stats['cells_assigned']}")
        print(f"    - Guesses: {stats['guesses']}")
        print(f"    - Backtracks: {stats['backtracks']}")
        print("✓ BacktrackingSolver: OK")
    else:
        print("✗ BacktrackingSolver: Failed to solve")
        sys.exit(1)
except Exception as e:
    print(f"✗ BacktrackingSolver: FAILED - {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 4: Dancing Links Solver
print("[4] Testing DancingLinksSolver...")
try:
    puzzle_str = TEST_PUZZLE
    board = PuzzleLoader.from_string(puzzle_str)
    solver = DancingLinksSolver(board)
    print("  Solving puzzle...")
    result = solver.solve_with_timer()
    if result and solver.board.is_solved():
        stats = solver.get_statistics()
        print(f"  ✓ Solved in {stats['execution_time']:.4f}s")
        print(f"    - Cells assigned: {stats['cells_assigned']}")
        print("✓ DancingLinksSolver: OK")
    else:
        print("✗ DancingLinksSolver: Failed to solve")
        sys.exit(1)
except Exception as e:
    print(f"✗ DancingLinksSolver: FAILED - {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 5: Algorithm Comparison
print("[5] Testing Algorithm Comparison...")
try:
    puzzle_str = TEST_PUZZLE

    # Test backtracking
    board1 = PuzzleLoader.from_string(puzzle_str)
    solver1 = BacktrackingSolver(board1)
    solver1.solve_with_timer()
    sol1 = solver1.board.to_string()

    # Test dancing links
    board2 = PuzzleLoader.from_string(puzzle_str)
    solver2 = DancingLinksSolver(board2)
    solver2.solve_with_timer()
    sol2 = solver2.board.to_string()

    # Compare solutions
    if sol1 == sol2:
        print(f"  Backtracking: {solver1.get_statistics()['execution_time']:.6f}s")
        print(f"  Dancing Links: {solver2.get_statistics()['execution_time']:.6f}s")
        print("✓ All algorithms produce identical solutions: OK")
    else:
        print("✗ Algorithm solutions differ!")
        sys.exit(1)
except Exception as e:
    print(f"✗ Algorithm Comparison: FAILED - {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✓")
print("=" * 60)
