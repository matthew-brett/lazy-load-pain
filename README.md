# Module shadows function (megamove import clash)

Minimal demo of why `max_tree.py` / `lookfor.py` had to become `_max_tree.py` /
`_lookfor.py` after the megamove.

## Layout

- `broken/` — `impl_broken.morphology.max_tree` (module name = function name)
- `fixed/` — `impl_fixed.morphology._max_tree` (private implementation module)

Both use a lazy parent package (`lazy_loader.attach_stub` + `__init__.pyi`), like
`_skimage2.morphology` after the megamove.

A compatibility shim (`compat_*/morphology/max_tree.py`) imports the implementation
submodule by path — as the megamove `skimage` shims do. (`compat_*` stands in for
`skimage` so the demo does not collide with an installed scikit-image.)

## Run

```bash
python3 demo.py
```

`demo.py` prints a step-by-step trace of imports and namespace state.

Expected: **broken** shows `impl_broken.morphology.max_tree` as a **module** after
the shim loads; **fixed** leaves `max_tree` out of the parent `__dict__` until
lazy export resolves the **function**.

Requires `lazy_loader` (`pip install lazy_loader`).
