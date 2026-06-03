# Module shadows function (megamove import clash)

**Code written by Cursor / Composer 2.5**

Minimal demo of why `max_tree.py` / `lookfor.py` had to become `_max_tree.py` /
`_lookfor.py` after the megamove.

## Layout

- `broken/` — `like_skimage2.morphology.max_tree` (module name = function name)
- `fixed/` — `like_skimage2.morphology._max_tree` (private implementation module)

Both use a lazy parent package (`lazy_loader.attach_stub` + `__init__.pyi`), like
`_skimage2.morphology` after the megamove.

A compatibility shim (`like_skimage/morphology/max_tree.py`) imports the implementation
submodule by path — as the megamove `skimage` shims do. (Each scenario lives under
`broken/` or `fixed/` on `sys.path` so the demo does not collide with an installed
scikit-image.)

## Run

```bash
python3 demo.py
```

`demo.py` prints a step-by-step trace of imports and namespace state.

Expected: **broken** shows `like_skimage2.morphology.max_tree` as a **module** after
the shim loads; **fixed** leaves `max_tree` out of the parent `__dict__` until
lazy export resolves the **function**.

Requires `lazy_loader` (`pip install lazy_loader`).
