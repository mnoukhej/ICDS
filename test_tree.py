import os

def generate_tree(path=".", prefix=""):
    tree = []
    files = sorted(os.listdir(path))
    for index, name in enumerate(files):
        if name.startswith(".") or name in ["__pycache__", "build", "dist", ".git"]:
            continue  # skip hidden and unwanted folders
        full_path = os.path.join(path, name)
        connector = "└── " if index == len(files) - 1 else "├── "
        tree.append(f"{prefix}{connector}{name}")
        if os.path.isdir(full_path):
            extension = "    " if index == len(files) - 1 else "│   "
            tree.extend(generate_tree(full_path, prefix + extension))
    return tree

tree = "\n".join(generate_tree("."))
print(tree)
