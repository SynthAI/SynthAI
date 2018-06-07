from fuzzywuzzy import fuzz
from contextlib import closing
import heapq
import messages
import commands
import sqlite3


def match(query, key):
    return fuzz.token_sort_ratio(query, key)


def best_matches(query, keys, n=5):
    vs = {}

    def sort_key(k):
        if k not in vs: vs[k] = match(query, k)
        return vs[k]

    return sorted(heapq.nlargest(n,
                                 keys,
                                 key=sort_key),
                  key=sort_key,
                  reverse=True)


def best_dict_values(query, d, deduplicate=True, n=5, filter=lambda x: True):
    keys = best_matches(query, d.keys(), n=3 * n)
    result = []
    for k in keys:
        v = d[k]
        if len(result) < n and v not in result and filter(v):
            result.append(v)
    return result


class Suggester(object):
    def __init__(self, kind, num_suggestions=5, num_shortcuts=5):
        self.db = sqlite3.connect("memoize.db")
        self.kind = kind
        self.cursor = self.db.cursor()
        self.cache = self.load_cache()
        self.num_suggestions = num_suggestions
        self.num_shortcuts = num_shortcuts

    def load_cache(self):
        self.cursor.execute("SELECT * FROM responses WHERE kind = ?",
                            (self.kind, ))
        return {obs: resp for obs, resp, source, kind in self.cursor}

    def delete_cached_response(self, obs):
        if obs in self.cache: del self.cache[obs]
        self.cursor.execute(
            "DELETE FROM responses WHERE input = ? AND kind = ?",
            (obs, self.kind))
        self.db.commit()

    def get_cached_response(self, obs):
        if obs in self.cache:
            return self.cache[obs]
        else:
            return None

    def set_cached_response(self, obs, response, src):
        self.cache[obs] = response
        self.cursor.execute("INSERT INTO responses VALUES (?, ?, ?, ?)",
                            (obs, response, src, self.kind))
        self.db.commit()

    def close(self):
        self.db.close()

    def make_suggestions_and_shortcuts(self,
                                       env,
                                       obs,
                                       num_suggestions=None,
                                       num_shortcuts=None):
        if num_suggestions is None:
            num_suggestions = self.num_suggestions
        if num_shortcuts is None:
            num_shortcuts = self.num_shortcuts
        cache = self.cache
        shortcuts = []

        def add_shortcut(m):
            h = m.format_with(["#"] * m.size)
            if useful_shortcut(h) and len(
                    shortcuts) < num_shortcuts and h not in shortcuts:
                shortcuts.append(h)

        def useful_shortcut(h):
            return len(h) > 8

        for register in env.registers:
            for m in register.contents:
                for h in messages.submessages(messages.strip_prefix(m),
                                              include_root=True):
                    add_shortcut(h)

        def useful_suggestion(h):
            c = commands.parse_command(h)
            m = commands.parse_message(h)
            try:
                if c is not None:
                    for m in c.messages():
                        m.instantiate(env.args)
                elif m is not None:
                    m.instantiate(env.args)
                return True
            except messages.BadInstantiation:
                return False

        suggestions = best_dict_values(obs,
                                       cache,
                                       filter=useful_suggestion,
                                       n=num_suggestions)
        for h in suggestions:
            c = commands.parse_command(h)
            m = commands.parse_message(h)
            if c is not None:
                for m in c.messages():
                    for sub_m in messages.submessages(m, include_root=True):
                        add_shortcut(sub_m)
            elif m is not None:
                for sub_m in messages.submessages(m, include_root=True):
                    add_shortcut(sub_m)
        return suggestions, shortcuts


def get_database_size():
    with closing(sqlite3.connect("memoize.db")) as conn:
        c = conn.cursor()
        from collections import Counter
        results = Counter()
        tables = [t[0] for t in c.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")]
        for table in tables:
            for _ in c.execute("SELECT * FROM {}".format(table)):
                results[table] += 1
        return results
