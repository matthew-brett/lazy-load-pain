# Module shadows function (megamove import clash)

**Code written by Cursor / Composer 2.5, edited by MB**

Minimal demo of name resolution with lazy loading, where function name shadows
module name.

The `_skimage2` type packages has a function name `max_tree` that shadows the identically named `max_tree` module.  See: `like_skimage2.morphology`.

A compatibility shim (`like_skimage/morphology/max_tree.py`) imports the
implementation submodule by path — as the megamove `skimage` shims do.

## Run

```bash
python -c 'import like_skimage2.morphology; print(type(like_skimage2.morphology.max_tree))'
python -c 'from like_skimage2.morphology import *; print(type(max_tree))'
python -c 'from like_skimage2.morphology import max_tree; print(type(max_tree))'
```

You should see "function" for the first, "module" for the second and "function"
for the third.

Next try:

```bash
python show_broken.py
```

and

```bash
python show_broken.py
```

`show_broken.py` prints a step-by-step trace of imports and namespace state.

Expected: shows `like_skimage2.morphology.max_tree` as a **module** after
first loading the shim in `like_skimage.morphology`.

`show_not_broken.py` shows import `like_skimage2.morphology` first leads to
correct resolution to the function in both cases.

`show_broken2.py` is a somewhat less verbose script, showing the same problem.

Requires `lazy_loader` (`pip install lazy_loader`).
