"""tasks.py: four tasks, same text for both stacks, HTTP behavior only."""

TASKS = {
"t1": "Each item in GET /items responses must also carry \"name_length\", the number of characters in its name.",
"t2": "GET /items must accept an optional min_len query parameter: only items whose name has at least that many characters are returned. It combines with the author filter.",
"t3": "Requests without a valid token get {\"error\":\"unauthorized\"} today; the 401 response must also carry the header WWW-Authenticate: Bearer, and the JSON body must additionally include \"status\": 401.",
"t4": "Filtering by author matches any author that merely starts with the given value: author=al returns alice's items. Author filtering must be exact.",
}

DEFECTS = {
("plain", "t4"): [("App.java",
    'SELECT id, author, name FROM items WHERE author = ? ORDER BY id',
    "SELECT id, author, name FROM items WHERE author LIKE (? || '%') ORDER BY id")],
("spring", "t4"): [
    ("src/main/java/demo/ItemRepository.java",
     "List<Item> findByAuthorOrderById(String author);",
     "List<Item> findByAuthorStartingWithOrderById(String author);"),
    ("src/main/java/demo/ItemController.java",
     "items.findByAuthorOrderById(author);",
     "items.findByAuthorStartingWithOrderById(author);")],
}

SEED = [(1, "alice", "teapot"), (2, "bob", "kettle"), (3, "alice", "cup"),
        (4, "carol", "saucer"), (5, "alice", "spoon")]

def base(rows):   return [{"id": i, "author": a, "name": n} for i, a, n in rows]
def with_len(rows): return [{"id": i, "author": a, "name": n, "name_length": len(n)}
                            for i, a, n in rows]

# each check: (path, token, expected_status, expected_body, required_headers)
def CHECKS(task):
    A = [r for r in SEED if r[1] == "alice"]
    if task == "t1":
        return [("/items", "t-alice", 200, with_len(SEED), {}),
                ("/items?author=alice", "t-alice", 200, with_len(A), {}),
                ("/items", None, 401, {"error": "unauthorized"}, {})]
    if task == "t2":
        m5 = [r for r in SEED if len(r[2]) >= 5]
        a5 = [r for r in A if len(r[2]) >= 5]
        return [("/items?min_len=5", "t-alice", 200, base(m5), {}),
                ("/items?author=alice&min_len=5", "t-alice", 200, base(a5), {}),
                ("/items", "t-alice", 200, base(SEED), {}),
                ("/items?author=alice", "t-alice", 200, base(A), {})]
    if task == "t3":
        return [("/items", None, 401,
                 {"error": "unauthorized", "status": 401},
                 {"WWW-Authenticate": "Bearer"}),
                ("/items", "bad", 401,
                 {"error": "unauthorized", "status": 401},
                 {"WWW-Authenticate": "Bearer"}),
                ("/items?author=alice", "t-alice", 200, base(A), {})]
    if task == "t4":
        return [("/items?author=al", "t-alice", 200, [], {}),
                ("/items?author=alice", "t-alice", 200, base(A), {}),
                ("/items", "t-alice", 200, base(SEED), {}),
                ("/items", None, 401, {"error": "unauthorized"}, {})]
