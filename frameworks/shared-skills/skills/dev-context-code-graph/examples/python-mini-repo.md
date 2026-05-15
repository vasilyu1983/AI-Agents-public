# Python Mini Repo Example

Input repo:

- `app.py` defines `helper()`
- `service.py` imports `helper()` and defines `Service.run()`
- `test_service.py` calls `Service.run()`

Expected outputs:

- one `repo` node
- three `file` nodes
- `function`, `class`, `method`, and `test` nodes
- `imports`, `calls`, and `tests` edges
- impact query from `service.py` reaches `Service.run` and `test_service.py`
