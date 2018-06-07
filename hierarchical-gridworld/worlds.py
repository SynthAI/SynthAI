from utils import clear_screen
import time
from random import random, randint

width = height = 11


class X(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return X(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return X(self.x - other.x, self.y - other.y)

    def in_direction(self, direction):
        dx, dy = directions[direction]
        return dx * self.x > 0 or dy * self.y > 0

    def move(self, direction):
        result = self + directions[direction]
        return result, result.is_valid()

    def is_valid(self):
        return self.x >= 0 and self.y >= 0 and self.x < height and self.y < width

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return "X({}, {})".format(self.x, self.y)


def update(grid, cell, f):
    return update_tuple(grid, cell.x, lambda t: update_tuple(t, cell.y, f))


def update_tuple(t, i, f):
    return t[:i] + (f(t[i]), ) + t[i + 1:]


def empty_grid():
    return (((), ) * width, ) * height


def articulate(s):
    if s[0] in "aeiou":
        return "an {}".format(s)
    else:
        return "a {}".format(s)


def render(xs):
    if xs is None:
        return "out of bounds"
    if len(xs) == 0:
        return "empty"
    else:
        return " and ".join(articulate(x) for x in xs)


def default_world():
    grid = empty_grid()

    def add_random(grid, item):
        while True:
            x, y = randint(0, height - 1), randint(0, width - 1)
            loc = X(x, y)
            contents = access(grid, loc)
            if "block" not in contents and "agent" not in contents and "wall" not in contents and not "goal" in contents:
                grid = add(grid, loc, item)
                return grid, loc

    grid, agent_xy = add_random(grid, "agent")
    grid, _ = add_random(grid, "goal")
    for i in range(int(0.1 * width * height)):
        grid, _ = add_random(grid, "block")
    for i in range(int(0.2 * width * height)):
        grid, _ = add_random(grid, "wall")
    return grid, agent_xy, None


def main():
    world = default_world()
    message = ""
    import term, termbox
    with term.Terminal() as t:
        while True:
            t.clear()
            print_world(world, t)
            if message: t.print_line(message)
            t.refresh()
            ch, key = t.poll()
            direction_name = {
                termbox.KEY_ARROW_LEFT: 'w',
                termbox.KEY_ARROW_RIGHT: 'e',
                termbox.KEY_ARROW_DOWN: 's',
                termbox.KEY_ARROW_UP: 'n',
            }.get(key, None)
            if direction_name is not None:
                direction = directions[direction_name]
                world, moved = move_person(world, direction)
            else:
                moved = False
            message = "" if moved else "!"


def render_small(xs):
    if "wall" in xs:
        return "#"
    if "agent" in xs:
        return "§" if "goal" in xs else "@"
    if "block" in xs:
        return "≣" if "goal" in xs else "="
    if "goal" in xs:
        return "_"
    return "."


def world_repr(world):
    grid, _, _ = world
    return "\n".join("".join(render_small(x) for x in r) for r in grid)


def print_world(world, t=None):
    if t is None:
        clear_screen()
    else:
        t.clear()
    lines = world_repr(world)
    for line in lines.split("\n"):
        if t is None:
            print(line)
        else:
            t.print_line(line)


def remove(grid, cell, x, ignore_absent=False):
    def f(xs):
        assert (x in xs) or ignore_absent
        return tuple(y for y in xs if y != x)

    return update(grid, cell, f)


def add(grid, cell, x):
    return update(grid, cell, lambda xs: xs + (x, ))


def const(x):
    return lambda *args, **kwargs: x


def is_pushable(grid, cell, direction):
    return passable(grid, cell + direction, direction)


def push_block(grid, cell, direction):
    grid = push(grid, cell + direction, direction)
    grid = remove(grid, cell, "block")
    grid = add(grid, cell + direction, "block")
    return grid


passable_test = {
    "agent": const(False),
    "wall": const(False),
    "goal": const(True),
    "block": is_pushable
}
pushers = {"block": push_block}
directions = {
    "north": X(-1, 0),
    "south": X(1, 0),
    "west": X(0, -1),
    "east": X(0, 1)
}
for k in list(directions.keys()):
    directions[k[0]] = directions[k]


def access(grid, cell):
    if cell.is_valid():
        return grid[cell.x][cell.y]
    else:
        return None


def passable(grid, cell, direction):
    if not in_bounds(grid, cell):
        return False
    return all(passable_test[x](grid, cell, direction)
               for x in access(grid, cell))


def in_bounds(grid, cell):
    i, j = cell
    N, M = len(grid), len(grid[0])
    return i >= 0 and i < N and j >= 0 and j < M


def push(grid, cell, direction):
    for x in access(grid, cell):
        if x in pushers:
            grid = pushers[x](grid, cell, direction)
    return grid


def move_person(world, direction):
    if isinstance(direction, str):
        direction = directions[direction]
    grid, agent_xy, previous = world
    target_xy = agent_xy + direction
    can_move = passable(grid, target_xy, direction)
    if can_move:
        grid = push(grid, target_xy, direction)
        grid = add(grid, target_xy, "agent")
        grid = remove(grid, agent_xy, "agent")
        return (grid, target_xy, world), True
    else:
        return world, False


def look(world, cell):
    grid, agent_xy, previous = world
    return render(access(grid, cell))


def display_history(world, fps=5):
    history = []
    while world is not None:
        history.append(world)
        world = world[2]
    for world in reversed(history):
        print_world(world)
        time.sleep(1 / fps)
