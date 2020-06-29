"""Tests for :class:`~sudoku_solver.Grid'."""

import numpy as np
import pytest


@pytest.fixture
def custom_grid():
    """Pytest fixture that provides a (9, 9) numpy grid of non-zero integers."""

    return np.arange(1, 82, dtype=np.int32).reshape((9, 9))


def test_create_default_grid():
    """Test creating a :class:`sudoku_solver.Grid` object."""

    from .. import Grid

    grid = Grid()
    assert grid.size == 9
    assert not grid.full
    assert grid.validate().all() == grid.grid.all()


def test_create_custom_grid(custom_grid):
    """Test creating a custom grid."""

    from .. import Grid

    grid = Grid(custom_grid)
    assert grid.grid.all() == custom_grid.all()


def test_default_grid_difficulty():
    """Test getting/setting difficulty for default grid."""

    from .. import Grid

    grid = Grid()
    assert grid.difficulty == 2
    assert grid.difficulty_level == 'Medium'
    grid.difficulty = 3
    assert grid.difficulty == 3
    assert grid.difficulty_level == 'Hard'
