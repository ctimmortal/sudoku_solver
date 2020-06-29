from math import sqrt

from numpy.random import shuffle
import numpy as np


def get_blocks(grid):
    """Get the blocks for a grid.

    Returns a list of arrays of shape `(grid.size ** (1/4), grid.size ** (1/4))`
    """

    return np.asarray(
        [b.reshape((3, 3)) for rs in np.split(grid, 3) for b in np.split(rs, 3, 1)]
    )


class Grid(object):
    """Represent a sudoku grid.

    :param grid: a sudoku grid
    :type grid: numpy.ndarray or list or list-like
    :param int size: size of the grid (i.e. the length of its sides)
    :param int block_size: size of each block within the grid
    :param difficulty: difficulty setting to apply to the grid

    If `grid` is specified, `size` and `block_size` parameters are ignored. If neither
    `grid` nor `block_size` are specified, `size` will be used to determine the
    dimensions of the grid. `size` defaults to 9. If `grid` is not specified and
    `block_size` is specified, `size` parameter is ignored and `block_size` is used to
    determine the dimensions of the grid.
    Difficulty is optional and will:
        1. default to 2 if `grid` is not specified, or
        2. be assigned based on analysis of the state of `grid` at instantiation
    """

    _difficulty_levels = [
        'Easy', 'Medium', 'Hard', 'Really Hard', 'Really Really Hard', 'Impossible',
    ]
    _mutable = True
    _grid_difficulty = 2
    _grid_size = 9

    def __init__(self, grid = None, size = 9, block_size = None, difficulty = 2):
        """Construct a :class:`Grid` object.

        Please see `help(Grid)` for more info.
        """

        self.diffuculty = difficulty
        if not grid:
            if block_size:
                size = block_size ** 2
            self.grid = np.zeros((size, size), np.int32)
        else:
            self.grid = self.validate(grid)
            self._mutable = False

        self.pool = np.arange(1, size + 1, dtype=np.int32)

    @property
    def difficulty_level(self):
        """Return the grid's difficulty as a string."""

        return self._difficulty_levels[self.diffuculty - 1]

    @property
    def full(self):
        """Check whether :attr:`~self.grid` is filled with non-zero integers."""

        return self.grid.any() != 0

    @property
    def size(self):
        """Get the size of the grid."""

        return int(self.grid.size ** (1/2))

    @property
    def block_size(self):
        """Get the size of each block within the grid."""

        return int(self.grid.size ** (1/4))

    @property
    def difficulty(self):
        """Get the difficulty level of the grid as an integer."""

        return self._grid_difficulty

    @difficulty.setter
    def difficulty(self, value):
        """Set the difficulty level of the grid.

        Available difficulty settings:
            1: Easy
            2: Medium
            3: Hard
            4: Really Hard
            5: Really Really Hard
            6: Impossible

        :param value: desired difficulty setting; can be str or int
        :type value: str or int
        :raises AttributeError: if the grid is not mutable
        :raises ValueError: if the value is not one of the available levels
        :raises TypeError: if the value is not a str or int
        """

        if not self._mutable:
            raise AttributeError(f'{self} does not support changing the difficulty.')
        elif isinstance(value, int):
            if value < 1 or value > 6:
                raise ValueError('Difficulty must be between 1 and 6.')
            self._grid_difficulty = value
        elif isinstance(value, str):
            if value not in self._difficulty_levels:
                raise ValueError(
                    f'Difficulty must be one of {self._difficulty_levels}.'
                )
            self._grid_difficulty = self._difficulty_levels.index(value) + 1
        else:
            raise TypeError(f'Value must be {str} or {int}, not {type(value)}.')

    def validate(self, grid = None):
        """Validate a sudoku grid.

        Verify that the grid is a square (i.e. the number of columns equals the number of rows) :class:`~numpy.ndarray` with dtype :class:`numpy.int32`. Cast the grid to a :class:`~numpy.ndarray` if possible.

        If no input is provided, validates :attr:`~self.grid`.
        """

        grid = grid or self.grid

        if not isinstance(grid, np.ndarray):
            grid = np.asarray(grid, np.int32)

        if grid.size ** (1/2) != len(grid) or not (len(grid) ** (1/2)).is_integer():
            raise TypeError(f'Grid must be square! Grid has shape: {grid.shape}')
        elif grid.dtype != np.int32:
            raise TypeError(
                f'Grid must contain only integers! Grid has dtype: {grid.dtype}'
            )
        else:
            return grid

    @property
    def blocks(self):
        """Get the blocks for :attr:`~self.grid`.

        Returns a list of tuples of (ix, val) where `ix` is an array of the indeces at
        which a block occurs, and `val` is the values from `grid` that occur in that
        block.
        """

        ix = get_blocks(np.arange(self.grid.size).reshape((self.size, self.size)))
        vals = get_blocks(self.grid)
        return list(zip(ix, vals))

    def get_block(self, index):
        """Get the block that contains a particular index."""

        for i, v in self.blocks:
            if i.any() == index:
                return v

    def fill(self, grid=None):
        """Fill a grid with numbers."""

        if grid:
            grid = self.validate(grid)
        else:
            grid = self.grid

        pool = self.pool.copy()

        with np.nditer(grid, flags = ['multi_index'], op_flags = ['readwrite']) as it:
            for n in it:
                row, col = iterator.multi_index
                if n != 0:
                    break
                block = self.get_block(it.iterindex)
                shuffle(pool)
                for v in pool:
                    if v not in grid[row] and v not in grid[:, col] and v not in block:
                        n[...] = v
                        if self.full or self.fill():
                            return True
