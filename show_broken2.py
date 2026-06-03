from sys import modules

# Lazy loading.
print("Lazy load of skimage2 module")
import like_skimage2.morphology

# Initially, nothing is defined in the skimage2 module __dict__, because of the
# lazy_loading.
print('skimage2.morphology has max_tree in dict?',
      'max_tree' in modules['like_skimage2.morphology'].__dict__)

print("__init__.py load of skimage module")
import like_skimage.morphology

# Now max_tree is defined in skimage2 module __dict__, because the skimage
# import triggered the load.
print('max_tree in skimage2.morphology.__dict__ is:',
      type(modules['like_skimage2.morphology'].__dict__["max_tree"]))

# However, skimage.morphology has loaded max_tree as a function.
print(
    "like_skimage.morphology.max_tree is",
    type(like_skimage.morphology.max_tree),
)

# Accessing `skiamge2.morphology.max_tree doesn't trigger lazy_loading
# because it is defined in the module dict.
print(
    "like_skimage2.morphology.max_tree is",
    type(like_skimage2.morphology.max_tree),  # No getattr, uses __doct__
)
