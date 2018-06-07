import utils
import six


class Referent(utils.Copyable):
    def instantiate(self, xs):
        raise NotImplemented()


class BadInstantiation(Exception):
    pass


class Message(Referent):
    """
    A Message consists of text interspersed with Referents
    """

    arg_names = ["text", "fields", "pending"]

    def __init__(self, text, *positional_fields, fields=(), pending=False):
        if isinstance(text, six.string_types):
            text = tuple(text.split("[]"))
        self.text = text
        self.fields = fields or positional_fields  #can either give fields as positional args, or fields=tuple
        assert positional_fields == () or fields == ()  #but can't do both
        self.pending = pending  #if pending, fields will be finalized later
        if not pending:
            assert self.well_formed()

    def finalize_fields(self, fields):
        assert self.pending
        self.fields = fields
        self.pending = False
        assert self.well_formed()

    def matches(self, text):
        target = tuple(text.split("[]"))
        return target == self.text

    def well_formed(self):
        return (
            utils.areinstances(self.text, six.string_types) and
            utils.areinstances(self.fields, Referent) and
            len(self.text) == len(self.fields) + 1)

    @property
    def size(self):
        return len(self.fields)

    def __add__(self, other):
        joined = self.text[-1] + other.text[0]
        return Message(
            text=self.text[:-1] + (joined, ) + other.text[1:],
            fields=self.fields + other.fields)

    def format_with(self, field_strings):
        return "".join(utils.interleave(self.text, field_strings))

    def __str__(self):
        def f(field):
            return "({})".format(field) if isinstance(field,
                                                      Message) else str(field)

        return self.format_with([f(field) for field in self.fields])

    def instantiate(self, args):
        """
        Instantiate all pointers by indexing into the list args.
        """
        return self.transform_fields_recursive(
            lambda field: field.instantiate(args))

    def transform_fields_recursive(self, f, cache=None):
        if cache is None: cache = {}
        if self in cache: return cache[self]
        result = Message(self.text, pending=True)
        cache[self] = result

        def sub(a):
            if isinstance(a, Message):
                return a.transform_fields_recursive(f, cache=cache)
            else:
                return f(a)

        result.finalize_fields(tuple(sub(a) for a in self.fields))
        return result

    def transform_fields(self, f):
        #don't use copy because subclasses should still create Messages
        return Message(text=self.text, fields=tuple(f(a) for a in self.fields))

    def get_leaves(m, seen=None):
        if seen is None: seen = set()
        seen.add(m)
        for field in m.fields:
            if isinstance(field, Message):
                yield from field.get_leaves(seen)
            else:
                yield field


class WorldMessage(Message):
    """
    A message representing a world.

    It provides some self-referential text, so that it remains
    usable if you view it.
    """

    arg_names = ["world"]

    def __init__(self, world):
        self.world = world
        self.fields = (self, )
        self.text = ("the gridworld grid ", "")

    def __str__(self):
        return "<<gridworld grid>>"


def get_world(m):
    if isinstance(m, WorldMessage):
        return m.world
    if m.matches("the gridworld grid []"):
        return get_world(m.fields[0])
    return None


class CellMessage(Message):
    """
    A message representing a cell.

    It provides some self-referential text, so that it remains
    usable if you view it.
    """

    arg_names = ["cell"]

    def __init__(self, cell):
        self.cell = cell
        self.fields = (self, )
        self.text = ("the gridworld cell ", "")

    def __str__(self):
        return "<<gridworld cell>>"


def get_cell(m):
    if isinstance(m, CellMessage):
        return m.cell
    if m.matches("the gridworld cell []"):
        return get_cell(m.fields[0])
    return None


def addressed_message(message,
                      implementer,
                      translator,
                      question=False,
                      budget=float('inf')):
    budget_str = "" if budget == float('inf') else ", budget {}".format(budget)
    channel = Channel(implementer=implementer, translator=translator)
    return Message("{} from []{}: ".format("Q" if question else "A",
                                           budget_str), channel) + message


def address_answer(A, sender):
    return Message("[]: ", sender) + A


def address_question(Q):
    return Message("Q: ") + Q


def strip_prefix(message, sep=": "):
    for i, t in enumerate(message.text):
        if sep in t:
            new_fields = message.fields[i:]
            new_t = sep.join(t.split(sep)[1:])
            new_text = (new_t, ) + message.text[i + 1:]
            return Message(text=new_text, fields=new_fields)
    return message


def submessages(ref, include_root=True, seen=None):
    if seen is None: seen = set()
    if isinstance(ref, Message) and ref not in seen:
        if include_root:
            seen.add(ref)
            yield ref
        for field in ref.fields:
            yield from submessages(field, seen=seen)


class Pointer(Referent):
    """
    A Pointer is an integer that indexes into a list of arguments
    """
    arg_names = ["n"]

    def __init__(self, n):
        self.n = n
        assert self.well_formed()

    def well_formed(self):
        return (isinstance(self.n, int))

    def instantiate(self, xs):
        if self.n < 0: raise BadInstantiation()
        try:
            return xs[self.n]
        except IndexError:
            raise BadInstantiation()

    def __str__(self):
        return "#{}".format(self.n)
