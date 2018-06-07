import json
import re
from abc import ABC

from threading import Lock


# A callback that only triggers exactly once, after being called N times
class CountDownCallback:
    def __init__(self, count, delegate):
        self._count = count
        self._delegate = delegate
        self._lock = Lock()

    def __call__(self, *args, **kwargs):
        self._lock.acquire()
        self._count -= 1
        if self._count == 0:
            self._delegate(*args, **kwargs)
        self._lock.release()


class Future(ABC):
    def result(self):
        pass

    def add_done_callback(self, fn):
        pass


class CompletedFuture(Future):
    def __init__(self, value):
        self._value = value

    def result(self):
        return self._value

    def add_done_callback(self, fn):
        fn(self)


class TransformingFuture(Future):
    def __init__(self, value, delegate):
        self._value = value
        self._delegate = delegate

    def result(self):
        self._delegate.result()
        return self._value

    def add_done_callback(self, fn):
        self._delegate.add_done_callback(lambda _: fn(self))


class AllCompletedFuture(Future):
    def __init__(self, futures):
        self._futures = futures

    def result(self):
        return [future.result() for future in self._futures]

    def add_done_callback(self, fn):
        callback = CountDownCallback(len(self._futures), lambda _: fn(self))
        for future in self._futures:
            future.add_done_callback(callback)


def selectors_to_hash(selectors):
    return json.dumps(selectors, sort_keys=True)


def get_groups_for_hash(asgs, selectors_hash):
    """
    returns a list of groups from asg that match the selectors
    """
    selectors = json.loads(selectors_hash)
    groups = []
    for asg in asgs:
        if asg.is_match_for_selectors(selectors):
            groups.append(asg)
    return groups


def get_group_for_node(asgs, node):
    for asg in asgs:
        if asg.contains(node):
            return asg
    return None


SI_suffix = {
    'y': 1e-24,  # yocto
    'z': 1e-21,  # zepto
    'a': 1e-18,  # atto
    'f': 1e-15,  # femto
    'p': 1e-12,  # pico
    'n': 1e-9,  # nano
    'u': 1e-6,  # micro
    'm': 1e-3,  # mili
    'c': 1e-2,  # centi
    'd': 1e-1,  # deci
    'k': 1e3,  # kilo
    'M': 1e6,  # mega
    'G': 1e9,  # giga
    'T': 1e12,  # tera
    'P': 1e15,  # peta
    'E': 1e18,  # exa
    'Z': 1e21,  # zetta
    'Y': 1e24,  # yotta
    # Kube also uses the power of 2 equivalent
    'Ki': 2**10,
    'Mi': 2**20,
    'Gi': 2**30,
    'Ti': 2**40,
    'Pi': 2**50,
    'Ei': 2**60,
}
SI_regex = re.compile(r"([0-9.]+)(%s)?$" % "|".join(SI_suffix.keys()))


def parse_SI(s):
    m = SI_regex.match(s)
    if m is None:
        raise ValueError("Unknown SI quantity: %s" % s)
    num_s, unit = m.groups()
    multiplier = SI_suffix[unit] if unit else 1.  # unitless
    return float(num_s) * multiplier


def parse_resource(resource):
    try:
        return float(resource)
    except ValueError:
        return parse_SI(resource)


def parse_bool_label(value):
    return str(value).lower() in ('1', 'true')


def get_relevant_selectors(node_selectors):
    selectors = dict((k, v) for (k, v) in node_selectors.items()
                     if k.startswith('aws/') or k.startswith('synthai/'))
    return selectors
