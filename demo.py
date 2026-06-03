#!/usr/bin/env python3
"""Compare broken vs fixed package layouts (verbose)."""

from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SEP = "-" * 72


def _say(msg: str = "") -> None:
    print(msg)


def _heading(title: str) -> None:
    _say()
    _say(SEP)
    _say(title)
    _say(SEP)


def _step(n: int, msg: str) -> None:
    _say(f"\n  Step {n}. {msg}")


def _describe(name: str, obj: object) -> None:
    kind = type(obj).__name__
    extra = ""
    if isinstance(obj, types.ModuleType):
        extra = f"  (file: {getattr(obj, '__file__', '?')})"
    elif callable(obj):
        extra = "  (callable)"
    _say(f"       {name}: {kind}{extra}")


def _parent_slot(skimage2_morph: types.ModuleType, key: str = "max_tree") -> None:
    if key in skimage2_morph.__dict__:
        _describe(
            f"{skimage2_morph.__name__}.__dict__['{key}']",
            skimage2_morph.__dict__[key],
        )
        _say(
            f"       → '{key}' is already in the package __dict__; "
            "Python will not call __getattr__ for this name."
        )
    else:
        _say(f"       {skimage2_morph.__name__}.__dict__['{key}']: (absent)")
        has_lazy = (
            hasattr(skimage2_morph, "__getattr__")
            and skimage2_morph.__getattr__ is not None
        )
        _say(
            f"       → '{key}' is not cached on the package"
            + ("; lazy_loader.__getattr__ can export the function." if has_lazy else ".")
        )


def _purge(prefix: str, *names: str) -> None:
    for name in names:
        sys.modules.pop(name, None)
    while prefix in sys.path:
        sys.path.remove(prefix)


def _run(label: str, src: Path, skimage2_pkg: str, skimage_pkg: str) -> None:
    prefix = str(src)
    sys.path.insert(0, prefix)

    skimage_morph_name = f"{skimage_pkg}.morphology"
    skimage2_morph_name = f"{skimage2_pkg}.morphology"
    skimage2_submod = f"{skimage2_morph_name}.max_tree"
    skimage2_private_submod = f"{skimage2_morph_name}._max_tree"
    skimage_shim_mod = f"{skimage_morph_name}.max_tree"

    modules = [
        skimage_pkg,
        skimage_morph_name,
        skimage_shim_mod,
        skimage2_pkg,
        skimage2_morph_name,
        skimage2_submod,
        skimage2_private_submod,
    ]

    _heading(f"{label}  [{src.name}/]")

    skimage2_module_file = (
        "max_tree.py" if "broken" in label.lower() else "_max_tree.py"
    )
    shim_import = (
        f"from {skimage2_submod} import *"
        if "broken" in label.lower()
        else f"from {skimage2_private_submod} import *"
    )

    _say("  Layout (maps to megamove):")
    _say(f"    {skimage2_pkg}.morphology     — lazy package (__init__.py + __init__.pyi)")
    _say(f"    {skimage2_pkg}.morphology.{skimage2_module_file}  — implementation")
    _say(f"    {skimage_pkg}.morphology   — eager public API")
    _say(f"    {skimage_pkg}.morphology.max_tree.py — shim: {shim_import}")

    import importlib

    _step(1, f"Import lazy _skimage2 parent: {skimage2_morph_name}")
    skimage2_morph = importlib.import_module(skimage2_morph_name)
    _describe(skimage2_morph_name, skimage2_morph)
    _parent_slot(skimage2_morph)
    _say("       (Nothing has loaded the shim yet.)")

    _step(2, f"Import skimage package (eager API): {skimage_morph_name}")
    _say("       Runs: from .max_tree import max_tree, ...")
    _say(f"       That loads shim {skimage_shim_mod}, which runs:")
    _say(f"         {shim_import}")
    skimage_morph = importlib.import_module(skimage_morph_name)
    _describe(skimage_morph_name, skimage_morph)
    _describe(f"{skimage_morph_name}.max_tree", skimage_morph.max_tree)
    _say("       skimage still works: its __init__ bound max_tree to the function.")

    _step(3, "Re-check _skimage2 parent namespace (the clash)")
    skimage2_morph = sys.modules[skimage2_morph_name]
    _parent_slot(skimage2_morph)
    if "max_tree" in skimage2_morph.__dict__ and isinstance(
        skimage2_morph.__dict__["max_tree"], types.ModuleType
    ):
        _say(
            f"       Loading {skimage2_submod} registered the submodule on the parent."
        )
        _say(
            "       Code that does `from _skimage2.morphology import max_tree` or "
            "`_skimage2.morphology.max_tree(...)` now sees a module, not the function."
        )

    _step(4, f"Access {skimage2_morph_name}.max_tree the way library users do")
    bound = skimage2_morph.max_tree
    _describe(f"{skimage2_morph_name}.max_tree", bound)
    if isinstance(bound, types.ModuleType):
        _say("       BUG: expected a function, got a module.")
        fn = getattr(bound, "max_tree", None)
        if callable(fn):
            _say(
                f"       The function still exists inside the submodule as "
                f"{skimage2_submod}.max_tree (callable)."
            )
    elif callable(bound):
        _say("       OK: package namespace exposes the callable.")

    _step(5, "Why this matters for lazy_loader")
    _say(f"       {skimage2_morph_name}.__init__.pyi declares:")
    if "broken" in label.lower():
        _say("         from .max_tree import max_tree")
    else:
        _say("         from ._max_tree import max_tree")
    _say("       lazy_loader would import the private module and re-export the function,")
    _say("       but only if __getattr__ runs. A submodule already in __dict__ blocks that.")

    _step(6, "Summary")
    if "max_tree" in skimage2_morph.__dict__ and isinstance(
        skimage2_morph.__dict__["max_tree"], types.ModuleType
    ):
        _say("       Submodule import via shim polluted the parent namespace.")
        _say("       Fix: rename implementation file so the shim imports e.g. _max_tree,")
        _say("       leaving the name max_tree free for the public function.")
    else:
        _say("       Shim imported _max_tree only; parent __dict__ has no 'max_tree' entry.")
        _say("       lazy_loader.__getattr__ resolves max_tree → function.")

    _purge(prefix, *modules)


def main() -> None:
    try:
        import lazy_loader  # noqa: F401
    except ImportError:
        sys.exit("Install lazy_loader: pip install lazy_loader")

    _say("Module-vs-function shadowing (megamove import demo)")
    _say("Compares two layouts in current directory")

    _run(
        "BROKEN — implementation module named max_tree",
        ROOT / "broken",
        "_skimage2",
        "skimage",
    )
    _run(
        "FIXED — implementation module named _max_tree",
        ROOT / "fixed",
        "_skimage2",
        "skimage",
    )

    _heading("Takeaway")
    _say("  On main, eager `from .max_tree import max_tree` in __init__.py masked this.")
    _say("  After megamove, _skimage2 subpackages are lazy; skimage shims import by path.")
    _say("  If that path is morphology.max_tree, the parent keeps the submodule object.")
    _say("  Rename to morphology._max_tree so max_tree on the parent is only the function.")
    _say()


if __name__ == "__main__":
    main()
