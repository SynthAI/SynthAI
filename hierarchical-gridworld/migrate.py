import sqlite3
from utils import starts_with

def standardize_response(r):
    subs = {
            "A:":"reply",
            "A ":"reply ",
            "return":"reply",
            "Q:":"ask",
            "Q ":"ask ",
            "say":"note",
            "ask@":"resume ",
            "reply:":"reply",
            "ask:":"ask",
        }
    for i in range(8):
        subs["reply {}".format(i)] = "resume {}".format(i)
        subs["Q{} ".format(10**i)] = "ask{} ".format(10**i)
    for k, v in subs.items():
        if starts_with(k, r):
            return v + r[len(k):]
    return r

def standardize_all_responses():
    try:
        db = sqlite3.connect("memoize.db")
        cursor = db.cursor()
        z = cursor.execute("SELECT * FROM responses")
        for obs, response, src, kind in list(z):
            new_response = standardize_response(response)
            print("{} -> {}".format(response, new_response))
            cursor.execute(
                "UPDATE responses SET output = ? WHERE input = ? AND kind = ? AND source = ?",
                (new_response, obs, kind, src)
            )
        db.commit()
    finally:
        db.close()
