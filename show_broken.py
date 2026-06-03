# Import chain for the first max_tree (like_skimage.morphology.max_tree):
#
#   like_skimage.morphology.__init__.py
#     → from .max_tree import max_tree
#   like_skimage.morphology.max_tree  (shim module)
#     → from like_skimage2.morphology.max_tree import *
#   like_skimage2.morphology.max_tree  (implementation submodule)
#     → defines max_tree(image) and area_opening
#
# The star import copies the function into the shim namespace; __init__.py then
# binds that name on like_skimage.morphology. Result: a function.
print('Importing shim')

import like_skimage.morphology

print(
    "like_skimage.morphology.max_tree is",
    type(like_skimage.morphology.max_tree),
)

# As a resul of this import, there is now a `like_skimage2.morphology` module,
# with `max_tree` defined in its __dict__.
import sys

print(
    "sys.modules['like_skimage2.morphology'].__dict__['max_tree'] is:",
    sys.modules['like_skimage2.morphology'].__dict__['max_tree'],
)

# This import only loads the lazy parent package (__init__.py + lazy_loader stub).
# It does not remove the submodule from __dict__.
print('Importing implementation')

import like_skimage2.morphology

print(
    "sys.modules['like_skimage2.morphology'].__dict__['max_tree'] is:",
    sys.modules['like_skimage2.morphology'].__dict__['max_tree'],
)

# Attribute lookup: "max_tree" is already in like_skimage2.morphology.__dict__,
# so Python returns the cached submodule and never calls __getattr__.
#
# lazy_loader would otherwise follow __init__.pyi:
#   from .max_tree import max_tree
# and re-export the function — but that path is blocked once the submodule
# occupies the name. Result: a module, not the function.
print(
    "like_skimage2.morphology.max_tree is",
    type(like_skimage2.morphology.max_tree),
)
