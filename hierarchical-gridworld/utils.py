def areinstances(xs, t):
    return isinstance(xs, tuple) and all(isinstance(x, t) for x in xs)


def interleave(*xss):
    result = []
    indices = [0 for xs in xss]
    lens = [len(xs) for xs in xss]
    n = 0
    while True:
        if indices[n] >= lens[n]:
            break
        result.append(xss[n][indices[n]])
        indices[n] += 1
        n = (n + 1) % (len(xss))
    assert indices == lens
    return result


def unweave(xs):
    result = ([], [])
    for i, x in enumerate(xs):
        result[i % 2].append(x)
    return tuple(result[0]), tuple(result[1])


def clear_screen():
    print("\x1b[2J\x1b[H")


def elicit_input(observations, actions):
    clear_screen()
    lines = interleave(observations, [">>> {}".format(action)
                                      for action in actions])
    print("\n\n".join(lines))
    return raw_input("\n>>> ")


def starts_with(p, s):
    return len(s) >= len(p) and s[:len(p)] == p


def pad_to(s, k):
    return s + " " * (k - len(s))


def matched_paren(s, k):
    delim = s[k]
    if delim == "(":
        d = 1
        closer = ")"
    elif delim == ")":
        d = -1
        closer = "("
    else:
        raise ValueError
    open_delims = 0
    k = k
    while True:
        if s[k] == delim:
            open_delims += 1
        elif s[k] == closer:
            open_delims -= 1
        if open_delims == 0:
            return k
        k += d
        if k < 0 or k >= len(s):
            return None


class Copyable(object):
    def copy(self, **kwargs):
        for k in self.arg_names:
            if k not in kwargs: kwargs[k] = self.__dict__[k]
        return self.__class__(**kwargs)

    @property
    def arg_names(self):
        raise NotImplemented()

def is_power_of_ten(x):
    if x == 10 or x == float('inf'):
        return True
    elif x % 10 != 0:
        return False
    else:
        return is_power_of_ten(x // 10)
