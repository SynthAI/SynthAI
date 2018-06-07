import termbox
import time
import sys
import random
import utils

color = termbox.DEFAULT

shortcut_bindings = [
    ('a', termbox.KEY_CTRL_A),
    ('s', termbox.KEY_CTRL_S),
    ('d', termbox.KEY_CTRL_D),
    ('f', termbox.KEY_CTRL_F),
    ('t', termbox.KEY_CTRL_T),
]


def get_input(t, suggestions=[], shortcuts=[], prompt=None, **kwargs):
    """
    Prompt the user for input

    t: the Terminal to use for collecting input
    suggestions: defaults the user can select by pressing <down>
    shortcuts: templates the user can insert by ctrl+<key>
    """

    shortcut_dict = {}
    for (c, k), template in zip(shortcut_bindings, shortcuts):
        shortcut_dict[k] = template
    if prompt is not None: t.print_line(prompt)
    inputter = Input(t,
                     t.x,
                     t.y,
                     suggestions=suggestions,
                     shortcuts=shortcut_dict,
                     **
                     kwargs)
    if shortcuts or suggestions:
        for i in range(3):
            t.print_line("")
    for i, suggestion in enumerate(suggestions):
        t.print_line("{}. {}".format(i + 1, suggestion))
    if suggestions:
        t.print_line("")
    for (c, k), template in zip(shortcut_bindings, shortcuts):
        t.print_line("{}: {}".format(c, template))
    return inputter.elicit()


class Input(object):
    def __init__(self,
                 t,
                 x,
                 y,
                 suggestions=[],
                 pre_suggestions=[],
                 shortcuts={},
                 default=""):
        self.x = x
        self.y = y
        self.s = default
        self.cursor = len(self.s)
        self.high_water = len(self.s)
        self.t = t
        self.drafts = pre_suggestions + [None] + suggestions
        self.current_draft = len(pre_suggestions)
        self.initial_draft = len(pre_suggestions)
        self.shortcuts = shortcuts

    def move_to_draft(self, new_draft):
        cursor_to_end = len(self.s) - self.cursor
        if self.current_draft == self.initial_draft:
            self.drafts[self.current_draft] = self.s
        self.s = self.drafts[new_draft]
        self.current_draft = new_draft
        self.cursor = max(0, len(self.s) - cursor_to_end)
        self.high_water = max(self.high_water, len(self.s))

    def refresh(self):
        self.t.putchs(self.x, self.y, pad_to(self.high_water, self.s))
        x, y = self.t.advance(self.x, self.y, self.cursor)
        self.t.set_cursor(x, y)
        paren_loc = self.paren_to_highlight()
        if paren_loc is not None:
            other_paren = utils.matched_paren(self.s, paren_loc)
            if other_paren is not None:
                for p in [paren_loc, other_paren]:
                    x, y = self.t.advance(self.x, self.y, p)
                    self.t.putch(x, y, self.s[p], termbox.BLACK, termbox.CYAN)
        self.t.refresh()

    def insert_ch(self, ch, n=None):
        if n is None: n = self.cursor
        self.s = self.s[:n] + ch + self.s[n:]
        if n <= self.cursor:
            self.cursor += 1
        self.high_water = max(self.high_water, len(self.s))

    def remove_ch(self, n=None):
        if n is None: n = self.cursor
        self.s = self.s[:n - 1] + self.s[n:]
        if n <= self.cursor:
            self.cursor -= 1

    def paren_to_highlight(self):
        if self.cursor < len(self.s) and self.s[self.cursor] in "()":
            return self.cursor
        if self.cursor > 0 and self.s[self.cursor - 1] in "()":
            return self.cursor - 1
        return None

    def poll(self):
        ch, key = self.t.poll()
        if key in [termbox.KEY_BACKSPACE, termbox.KEY_BACKSPACE2
                   ] and self.cursor > 0:
            self.remove_ch()
        elif key == termbox.KEY_ARROW_LEFT and self.cursor > 0:
            self.cursor -= 1
        elif key == termbox.KEY_ARROW_RIGHT and self.cursor < len(self.s):
            self.cursor += 1
        elif key == termbox.KEY_ARROW_UP:
            if self.cursor > self.t.width:
                self.cursor -= self.t.width
            elif self.current_draft > 0:
                self.move_to_draft(self.current_draft - 1)
        elif key == termbox.KEY_ARROW_DOWN:
            if self.cursor < len(self.s) - self.t.width:
                self.cursor += self.t.width
            elif self.current_draft < len(self.drafts) - 1:
                self.move_to_draft(self.current_draft + 1)
        elif key == termbox.KEY_CTRL_U:
            self.s = ""
            self.cursor = 0
        elif key == termbox.KEY_CTRL_R:
            self.jump_to_arg(-1)
        elif key == termbox.KEY_CTRL_K:
            self.jump_to_arg(1)
        elif key == termbox.KEY_ENTER:
            return self.s
        elif key in self.shortcuts:
            for c in self.shortcuts[key]:
                self.insert_ch(c)
        elif ch != None:
            self.insert_ch(ch)
        self.refresh()
        return None

    def jump_to_arg(self, d):
        def to():
            return self.cursor + d

        stops = "()#"
        ready = False
        while to() <= len(self.s) and to() >= 0:
            if self.cursor > 0 and self.s[self.cursor - 1] == " ": ready = True
            self.cursor = to()
            if self.cursor == 0:
                return
            if self.s[self.cursor - 1] in stops and ready:
                return

    def elicit(self):
        self.refresh()
        while True:
            result = self.poll()
            if result is not None: return result


def pad_to(k, s):
    return s + " " * (k - len(s))


class Terminal(object):
    def __init__(self):
        self.closed = False
        pass

    def __enter__(self):
        self.t = termbox.Termbox()
        self.t.__enter__()
        self.x = 0
        self.y = 0
        self.width = min(self.t.width(), 80)
        self.clear()
        return self

    def __exit__(self, *args):
        self.closed = True
        self.t.__exit__(*args)

    def putch(self, x, y, ch, fg=termbox.DEFAULT, bg=termbox.DEFAULT):
        if ch == "\n":
            return (0, y + 1)
        else:
            self.t.change_cell(x, y, ord(ch), fg, bg)
            return self.advance(x, y)

    def print_ch(self, ch):
        self.x, self.y = self.putch(self.x, self.y, ch)

    def advance(self, x, y, n=1):
        x += n
        while x >= self.width:
            x -= self.width
            y += 1
        return x, y

    def putchs(self, x, y, chs):
        for ch in chs:
            x, y = self.putch(x, y, ch)
        return x, y

    def print_line(self, line="", new_line=True):
        if new_line:
            self.x = 0
            self.y += 1
        self.x, self.y = self.putchs(self.x, self.y, line)

    def clear(self):
        self.t.clear()
        self.x = 0
        self.y = 0

    def refresh(self):
        self.t.present()

    def poll(self):
        type, ch, key, mod, w, h, x, y = self.t.poll_event()
        if type == termbox.EVENT_KEY and key == termbox.KEY_CTRL_C:
            raise KeyboardInterrupt()
        if type == termbox.EVENT_KEY and key == termbox.KEY_CTRL_Q:
            raise ValueError()
        if key == 32:
            ch = " "
        return ch, key

    def set_cursor(self, x, y):
        self.t.set_cursor(x, y)
