from deta import Deta

DETA_KEY = "c050exny_sE1wzsJo16sN4NJEq1uwxLkDa7kAZAxV"

deta = Deta(DETA_KEY)

db = deta.Base("quiz_results")


def fetch_db():
    res = db.fetch()
    return res.items