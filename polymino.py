"""Polymino functions

Attributes:
    COLOURS (TYPE): Description
    DOMINOES (TYPE): Description
    PENTOMINOES (TYPE): Description
    TETROMINOES (TYPE): Description
    TROMINOES (TYPE): Description
"""

from collections import defaultdict
from copy import deepcopy
from itertools import product
from svgwrite import Drawing

# polyminoes drawn in ascii
DOMINOES = """
I
I
"""

TROMINOES = """
I L 
I LL  
I
"""

TETROMINOES = """
I L  OO ZZ
I L  OO  ZZ
I LL
I
"""

# PENTOMINOES = """
#     I
#     I  L   N                         Y
#  FF I  L   N PP TTT       V   W  X  YY ZZ
# FF  I  L  NN PP  T  U U   V  WW XXX  Y  Z
#  F  I  LL N  P   T  UUU VVV WW   X   Y  ZZ
# """

PENTOMINOES = """   
 F I   LL N N P  TT   
FF I   LL NNN PP  T 
 F III  L      P  T 
 F             P  T
"""

class Polymino:
    """Polymino piece

    Attributes:
        coord (list of tuples): Polymino coordinates.
        name (Str): Name of the polymino piece.
    """

    def __init__(self, name, coord):
        """init method

        Args:
            name (Str): Name of the polymino piece.
            coord (list of tuples): Polymino coordinates.
        """
        self.name = name
        self.coord = sorted(coord)
        # get boundaries
        self.min_i, self.min_j = map(min, *coord)
        self.max_i, self.max_j = map(max, *coord)

    @classmethod
    def from_list(cls, lst):
        """Polymino ame and coordinates from list

        Args:
            lst (list): List with polymino coordinates, and name

        Returns:
            Polymino instance

        Raises:
            ValueError: If name and/or coordinates missing from list.
        """
        coord = []
        name = ''

        for i in lst:
            if isinstance(i, tuple):
                coord.append(i)
            elif isinstance(i, str):
                name = i

        if not coord:
            raise ValueError("No coordinates in list")
        if name == '':
            raise ValueError("No name in list")

        return cls(name, coord)

    @property
    def limit(self):
        """Get boundaries

        Returns:
            list of boundaries
        """
        return [self.min_i, self.max_i, self.min_j, self.max_j]

    @property
    def size(self):
        """Get size of polymino

        Returns:
            List of size in i and j coordinate.
        """
        return [self.max_i-self.min_i+1, self.max_j-self.min_j+1]

    @property
    def aslist(self):
        """Convert Polymino instance to list

        Returns:
            List with polymino name and coordinates
        """
        return [self.name] + self.coord

    def relative_shift(self, delta_i, delta_j):
        """Shift the coordinates of the Polymino relative to its current
        position.

        Args:
            delta_i (int): Shift of i coordinate
            delta_j (int): Shift of j coordinate
        """
        self.min_i += delta_i
        self.max_i += delta_i
        self.min_j += delta_j
        self.max_j += delta_j

        self.coord = [(i+delta_i, j+delta_j) for i, j in self.coord]

    def absolute_shift(self, i_0, j_0):
        """Shift the coordinates of the Polymino to an absolute position.

        Args:
            i_0 (int): i coordinate value of the upper left corner.
            j_0 (int): j coordinate velue of the upper left corner.
        """
        self.coord = [(i-self.min_i+i_0, j-self.min_j+j_0) for i, j in self.coord]

        self.max_i += i_0 - self.min_i
        self.max_j += j_0 - self.min_j
        self.min_i = i_0
        self.min_j = j_0

    def flip(self, ftype='vertical', reset=True):
        """Flip the polymino around the vertical or horizontal axes.

        The flips are always relative to the origin (0, 0).

        Args:
            ftype (str, optional): Flip around vertical or horizontal axis.
            (Default: vertical)
            reset (bool, optional): Reset the coordinates of the upper left
            corner to the original value after the flip (Default: True).

        Raises:
            ValueError: If ftype is not 'vertical' or 'horizontal'.
        """
        old_min_i, _, old_min_j, _ = self.limit

        if ftype == 'vertical':
            self.coord = sorted([(i, -j) for i, j in self.coord])
            self.min_j, self.max_j = -self.max_j, -self.min_j
        elif ftype == 'horizontal':
            self.coord = sorted([(-i, j) for i, j in self.coord])
            self.min_i, self.max_i = -self.max_i, -self.min_i
        else:
            raise ValueError("ftype must be either horizontal or vertical")

        if reset:
            self.absolute_shift(old_min_i, old_min_j)

    def rotate(self, reset=True):
        """Rotate Polymino 90 degree counter clockvise around (0, 0)

        Args:
            reset (bool, optional): Reset the coordinates of the upper left
            corner to the original value after the flip (Default: True).
        """
        old_min_i, _, old_min_j, _ = self.limit

        self.coord = sorted([(-j, i) for i, j in self.coord])

        self.min_i, self.max_i, self.min_j, self.max_j = \
        -self.max_j, -self.min_j, self.min_i, self.max_i

        if reset:
            self.absolute_shift(old_min_i, old_min_j)

    def ascii(self, empty=' '):
        """Print an ascii drawing of the polymino.

        Args:
            empty (str, optional): Ascii character to use for holes in the grid.

        Returns:
            Str
        """
        height, width = self.size

        grid = []
        for i in range(height):
            grid.append([empty for j in range(width)])

        for i, j in self.coord:
            grid[i-self.min_i][j-self.min_j] = self.name

        return '\n'.join([''.join(row) for row in grid])

    def __str__(self):
        return self.ascii()

    def __hash__(self):
        return hash(tuple(self.aslist))

    def __eq__(self, other):
        if isinstance(other, Polymino):
            return (self.name, self.coord) == (other.name, other.coord)
        return False

class Grid:
    """Grid on which to place polyminoes

    Attributes:
        coord (list of tuples): Grid coordinates.
        polyminoes (List of Polymino objects): Polyminoes on the grid.
        size (tuple): Size of the grid
    """

    def __init__(self, size, i_0=0, j_0=0, polyminoes=None, holes=None):
        """init method

        Args:
            size (tuple): Size of grid (n_i, n_j).
            i_0 (int, optional): i coordinate value at upper left corner
            j_0 (int, optional): j coordinate value at upper left corner
            polyminoes (None, optional): Polyminoes on the grid
            holes (None, optional): Coordinates of "holes" in the grid.
        """
        n_i, n_j = size
        holes = [] if holes is None else holes
        polyminoes = [] if polyminoes is None else polyminoes

        self.size = size
        self.coord = []
        self.polyminoes = []
        self.min_i, self.max_i = i_0, i_0+n_i-1
        self.min_j, self.max_j = j_0, j_0+n_j-1

        # build self.grid with (i, j) coordinates for each gridpoint
        for i in range(n_i):
            for j in range(n_j):
                # only include the grid point if not part of a "hole"
                if (i, j) not in holes:
                    self.coord.append((i, j))

        # check that all polyminoes are in a valid position
        for polymino in polyminoes:
            self.add(polymino)

    @classmethod
    def from_DLX(cls, solution):
        """Generate grid from DLX solution

        Args:
            solution: solution as returned from the DLX class

        Returns:
            Instance of Grid class
        """

        polyminoes = [Polymino.from_list(polymino) for polymino in solution]

        # get boundaries for the grid
        min_i = min([polymino.min_i for polymino in polyminoes])
        max_i = max([polymino.max_i for polymino in polyminoes])
        min_j = min([polymino.min_j for polymino in polyminoes])
        max_j = max([polymino.max_j for polymino in polyminoes])

        # size of the grid from boundaries
        size = (max_i-min_i+1, max_j-min_j+1)

        # Holes in the grid. Assumed to be grid points within the boundary,
        # not coevered by a polymino
        holes = []
        for i in range(min_i, max_i+1):
            for j in range(min_j, max_j+1):
                holes.append((i, j))

        holes = set(holes)
        for polymino in polyminoes:
            holes = holes - set(polymino.coord)

        holes = list(holes)

        return cls(size, min_i, min_j, polyminoes, holes)

    @property
    def limit(self):
        """Get boundaries

        Returns:
            list of boundaries
        """
        return [self.min_i, self.max_i, self.min_j, self.max_j]

    def valid_position(self, polymino):
        """Test to see if a polymino is in a valid position.

        A valid position is on the grid, and without overlapping any other
        polymino

        Args:
            polymino: Polymino instance.

        Returns:
            bool
        """
        set_polymino = set(polymino.coord)

        for poly in self.polyminoes:
            if set_polymino.intersection(poly.coord):
                return False

        if set_polymino.intersection(self.coord) != set_polymino:
            return False

        return True

    def add(self, polymino):
        """Add a polymino to the grid.

        Args:
            polymino: Polymino instance.

        Raises:
            ValueError: If a polymino is outside the grid or covers another
            polymino.
        """
        if self.valid_position(polymino):
            self.polyminoes.append(deepcopy(polymino))
        else:
            raise ValueError("Polymino not in a valid grid position")

    def relative_shift(self, delta_i, delta_j):
        """Shift the coordinates of the Grid relative to its current position.

        Args:
            delta_i (int): Shift of i coordinate
            delta_j (int): Shift of j coordinate
        """
        self.min_i += delta_i
        self.max_i += delta_i
        self.min_j += delta_j
        self.max_j += delta_j

        _ = [p.relative_shift(delta_i, delta_j) for p in self.polyminoes]

    def absolute_shift(self, i_0, j_0):
        """Shift the coordinates of the Grid to an absolute position.

        Args:
            i_0 (int): i coordinate value of the upper left corner.
            j_0 (int): j coordinate velue of the upper left corner.
        """

        delta_i, delta_j = i_0-self.min_i, j_0-self.min_j

        self.relative_shift(delta_i, delta_j)

    def flip(self, ftype='vertical', reset=True):
        """Flip the Grid around the vertical or horizontal axes.

        The flips are always relative to the origin (0, 0).

        Args:
            ftype (str, optional): Flip around vertical or horizontal axis.
            (Default: vertical)
            reset (bool, optional): Reset the coordinates of the upper left
            corner to the original value after the flip (Default: True).

        Raises:
            ValueError: If ftype is not 'vertical' or 'horizontal'.
        """
        old_min_i, _, old_min_j, _ = self.limit

        if ftype == 'vertical':
            self.min_j, self.max_j = -self.max_j, -self.min_j
        elif ftype == 'horizontal':
            self.min_i, self.max_i = -self.max_i, -self.min_i
        else:
            raise ValueError("ftype must be either horizontal or vertical")

        _ = [p.flip(ftype, reset=False) for p in self.polyminoes]

        if reset:
            self.absolute_shift(old_min_i, old_min_j)

    def rotate(self, reset=True):
        """Rotate Grid 90 degree counter clockvise around (0, 0)

        Args:
            reset (bool, optional): Reset the coordinates of the upper left
            corner to the original value after the flip (Default: True).
        """
        old_min_i, _, old_min_j, _ = self.limit

        _ = [p.rotate(reset=False) for p in self.polyminoes]

        self.min_i, self.max_i, self.min_j, self.max_j = \
        -self.max_j, -self.min_j, self.min_i, self.max_i

        if reset:
            self.absolute_shift(old_min_i, old_min_j)

    def ascii(self, empty=' ', gridpoint='+'):
        """Print an ascii drawing of the grid with the polyminoes.

        Args:
            empty (str, optional): Ascii character to use for holes in the grid.
            gridpoint (str, optional): Ascii character to use for grid points
            not covered by a polymino.

        Returns:
            Str
        """
        height, width = self.size

        grid = []
        for i in range(height):
            grid.append([empty for j in range(width)])

        for i, j in self.coord:
            grid[i-self.min_i][j-self.min_j] = gridpoint

        for polymino in self.polyminoes:
            for i, j in polymino.coord:
                grid[i-self.min_i][j-self.min_j] = polymino.name

        return '\n'.join([''.join(row) for row in grid])

    def __str__(self):
        return self.ascii()

    def __eq__(self, other):
        if not isinstance(other, Grid):
            return False
        if self.coord != other.coord:
            return False
        for polymino in self.polyminoes:
            if polymino not in other.polyminoes:
                return False
        return True

def generate_polyminoes(ascii_drawing):
    """Generate polymino coordinates from ascii drawing

    Args:
        ascii_drawing (str): An ascii drawing of the polyminoes to be
        generated. Polyminoes must be drawn using ascii characters, where the
        polymino gets named after the ascii character.

    Yields:
        List of Polymino class instances.
    """

    # get coordinates for each polymino in the ascii drawing
    polydic = defaultdict(list)
    for i, row in enumerate(ascii_drawing.split('\n')):
        for j, name in enumerate(row):
            if name != ' ':
                polydic[name].append((i, j))

    # yield Polymino objects with each polymino shifted to (0, 0)
    for key in sorted(polydic.keys()):
        polymino = Polymino(key, polydic[key])
        polymino.absolute_shift(0, 0)
        yield polymino

def generate_polymino_orientations(polyminoes):
    """Generate all orientations (flips and rotations) of a polymino.

    Args:
        polyminoes: List of polyminoes to generate orientations of.

    Yields:
        Polymino instance.
    """
    polyminoes = [polyminoes] if isinstance(polyminoes, Polymino) else polyminoes

    for polymino in polyminoes:

        for _ in range(4):
            yield deepcopy(polymino)
            polymino.rotate()

        polymino.flip()

        for _ in range(4):
            yield deepcopy(polymino)
            polymino.rotate()

def generate_polymino_positions(polyminoes, grid):
    """Place polyminoes on all valid positions in the grid

    Args:
        polyminoes: List of polyminoes to place on grid
        grid: Grid instance.

    Yields:
        Polymino instance.
    """
    polyminoes = [polyminoes] if isinstance(polyminoes, Polymino) else polyminoes

    for polymino in polyminoes:
        for i in range(grid.min_i, grid.min_i+grid.size[0]):
            for j in range(grid.min_j, grid.min_j+grid.size[1]):
                polymino.absolute_shift(i, j)
                if grid.valid_position(polymino):
                    yield deepcopy(polymino)

def generate_all(ascii_drawing, grid):
    """Generate all polyminoes, orientations and grid positions.

    Only unique polyminoes are returned.

    Args:
        ascii_drawing (Str): An ascii drawing of the polyminoes to be
        generated. Polyminoes must be drawn using ascii characters, where the
        polymino gets named after the ascii character.
        grid (TYPE): Grid instance

    Returns:
        List of polymino instances.
    """
    polyminoes = []
    for polymino in generate_polyminoes(ascii_drawing):
        for orientation in generate_polymino_orientations(polymino):
            for position in generate_polymino_positions(orientation, grid):
                if position not in polyminoes:
                    polyminoes.append(position)
    return polyminoes

def generate_grid_orientations(grids):
    """Generate all orientations (flips and rotations) of a grid.

    Args:
        grids: List of grids to generate orientations of.

    Yields:
        Grid instance.
    """

    grids = [grids] if isinstance(grids, Grid) else grids

    for grid in grids:
        for _ in range(4):
            yield deepcopy(grid)
            grid.rotate()

        grid.flip()

        for _ in range(4):
            yield deepcopy(grid)
            grid.rotate()

# def unique_grids(grids):
#     grids = list(grids)
#     print(grids)
#     unique = [grids[0]]
#     print(unique)
#     for grid in grids[1:]:
#         is_unique = True
#         for orientation in generate_grid_orientations(grid):
#             if orientation in unique:
#                 is_unique = False
#                 break
#         if is_unique:
#             unique.append(grid)

#     return unique
def unique_grids(grids):
    unique = []
    if grids:
        unique.append(grids[0])

    for grid in grids[1:]:
        is_unique = True
        try:
            for orientation in generate_grid_orientations(grid):
                if orientation in unique:
                    is_unique = False
                    break
        except Exception as e:
            print("Error occurred:", e)
            continue

        if is_unique:
            unique.append(grid)

    return unique


def solutions_svg(solutions, filename, columns=1, size=25, padding=5,
                  colour=lambda _: "white", stroke_colour="black",
                  stroke_width=3, empty=' '):
    """Format polyomino tilings as an SVG image.

    Args:
        solutions (list): Grid instance with polymino solution.
        filename (str): Filename.
        columns (int, optional): Columns in image (Default: 1).
        size (int, optional): width and height of each tile (default: 25).
        padding (int, optional): padding around the image (default: 5)
        colour (TYPE, optional): function taking a piece name and returning its c
            olour (Default: a function returning white for each piece).
        stroke_colour (str, optional): stroke colour (default: black).
        stroke_width (int, optional): width of strokes between pieces (default: 3).
        empty (str, optional): String for empty grid point.
    """
    solutions = list(solutions)

    height, width = solutions[0].size

    rows = (len(solutions) + columns - 1) // columns

    drawing_size = (2 * padding + (columns * (width + 1) - 1) * size,
                    2 * padding + (rows    * (height + 1) - 1) * size)

    drawing = Drawing(debug=False, filename=filename, size=drawing_size)
    for i, solution in enumerate(solutions):
        y, x = divmod(i, columns)
        oj = padding + (x * (width + 1)) * size
        oi = padding + (y * (height + 1)) * size
        group = drawing.g(stroke=stroke_colour, stroke_linecap="round",
                          stroke_width=0.25)
        drawing.add(group)

        grid = [[empty] * width for _ in range(height)]
        for polymino in solution.polyminoes:
            piece = drawing.g(fill=colour(polymino.name))
            group.add(piece)
            for i, j in polymino.coord:
                grid[i][j] = polymino.name
                piece.add(drawing.rect((j * size + oj, i * size + oi),
                                       (size, size)))

        # put in "empty" pieces
        for i, j in solution.coord:
            if grid[i][j] == empty:
                piece = drawing.g(fill='white')
                group.add(piece)
                piece.add(drawing.rect((j * size + oj, i * size + oi),
                                       (size, size)))

        edges = drawing.path(stroke_width=stroke_width)
        group.add(edges)
        for i, j in product(range(height + 1), range(width)):
            if ((empty if i == 0 else grid[i-1][j])
                != (empty if i == height else grid[i][j])):
                edges.push(['M', j * size + oj, i * size + oi, 'l', size, 0])
        for i, j in product(range(height), range(width + 1)):
            if ((empty if j == 0 else grid[i][j-1])
                != (empty if j == width else grid[i][j])):
                edges.push(['M', j * size + oj, i * size + oi, 'l', 0, size])
    drawing.save()

if __name__ == '__main__':
    GRID = Grid((5, 7), holes=[(4, 0), (4, 1), (4, 2), (4, 3), (0, 4)])
    POLYMINOES = generate_all(PENTOMINOES, GRID)
    print("Actual number: {}".format(len(POLYMINOES)))
