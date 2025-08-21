"""
╔════╗╔═══╗╔═══╗╔═══╗    ╔═══╗╔═══╗╔═╗ ╔╗╔═══╗╔═══╗╔═══╗╔════╗╔═══╗╔═══╗
║╔╗╔╗║║╔═╗║║╔══╝║╔══╝    ║╔═╗║║╔══╝║║╚╗║║║╔══╝║╔═╗║║╔═╗║║╔╗╔╗║║╔═╗║║╔═╗║
╚╝║║╚╝║╚═╝║║╚══╗║╚══╗    ║║ ╚╝║╚══╗║╔╗╚╝║║╚══╗║╚═╝║║║ ║║╚╝║║╚╝║║ ║║║╚═╝║
  ║║  ║╔╗╔╝║╔══╝║╔══╝    ║║╔═╗║╔══╝║║╚╗║║║╔══╝║╔╗╔╝║╚═╝║  ║║  ║║ ║║║╔╗╔╝
 ╔╝╚╗ ║║║╚╗║╚══╗║╚══╗    ║╚╩═║║╚══╗║║ ║║║║╚══╗║║║╚╗║╔═╗║ ╔╝╚╗ ║╚═╝║║║║╚╗
 ╚══╝ ╚╝╚═╝╚═══╝╚═══╝    ╚═══╝╚═══╝╚╝ ╚═╝╚═══╝╚╝╚═╝╚╝ ╚╝ ╚══╝ ╚═══╝╚╝╚═╝

A simple Python script to generate a folder structure tree in Markdown format.
It can be used for README files, documentation, or just for fun!

"""

import os, json

def load_mapping():
    """Load icon mapping from JSON file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mapping_file = os.path.join(script_dir, "icon_mapping.json")
    with open(mapping_file, "r") as f:
        return json.load(f)

def ask_bool(prompt):
    """Ask a yes/no question and return True/False."""
    while True:
        ans = input(f"{prompt} (y/n): ").strip().lower()
        if ans in ("y", "yes"): return True
        if ans in ("n", "no"): return False
        print("Please enter 'y' or 'n'.")

def ask_depth(prompt):
    """Ask for a maximum depth and return it as an integer, or None for unlimited."""
    ans = input(f"{prompt} (enter number, blank for unlimited): ").strip()
    if ans == "": return None
    try: return int(ans)
    except ValueError: return None

def ask_style():
    """Ask for the output style and return 'callout' or 'tree'."""
    while True:
        ans = input("Output style? (1 = callout '>', 2 = tree '├──'): ").strip()
        if ans == "1": return "callout"
        if ans == "2": return "tree"
        print("Please enter 1 or 2.")

def generate_tree(path, mapping, use_links, use_backticks, ignored_folders, max_depth, use_placeholders, style):
    """Generate a folder structure tree as a string."""

    tree_lines = []

    def escape_markdown(name: str) -> str:
        """Escape underscores in names for Markdown."""
        return name.replace("_", "\\_") if style == "callout" else name

    def format_name(entry, rel_path, is_dir):
        """Format the entry name for display."""
        name = escape_markdown(entry)
        if style == "tree":
            display = name
        else:
            if use_backticks:
                name = f"`{name}`"
            if use_links and not is_dir:
                display = f"[{name}]({rel_path})"
            elif use_links and is_dir:
                display = f"[{name}]({rel_path})/"
            else:
                display = name
        if use_placeholders:
            display = f"{display} — *Place description here*"
        return display

    def get_icon(name, is_dir=False):
        """Get the icon for a file or folder based on its name."""
        if is_dir:
            if name.startswith(".git"): return "⚙️"
            return mapping.get("folder", "📁")
        if name in mapping: return mapping[name]
        ext = os.path.splitext(name)[1]
        if ext in mapping: return mapping[ext]
        return mapping.get("default", "📄")

    def walk(dir_path, prefix="", depth=0):
        """Recursively walk through the directory and build the tree."""
        if max_depth is not None and depth >= max_depth: return
        entries = [e for e in sorted(os.listdir(dir_path)) if e not in ignored_folders]
        count = len(entries)
        for i, entry in enumerate(entries):
            full_path = os.path.join(dir_path, entry)
            rel_path = os.path.relpath(full_path, start=path)
            connector = "└── " if i == count - 1 else "├── "
            if os.path.isdir(full_path):
                display = format_name(entry, rel_path, True)
                if style == "tree":
                    tree_lines.append(f"{prefix}{connector}{get_icon(entry, True)} {display}")
                    new_prefix = prefix + ("    " if i == count - 1 else "│   ")
                    walk(full_path, new_prefix, depth + 1)
                else:
                    tree_lines.append(f"> {prefix}- {get_icon(entry, True)} {display}")
                    walk(full_path, prefix + "  ", depth + 1)
            else:
                display = format_name(entry, rel_path, False)
                icon = get_icon(entry)
                if style == "tree":
                    tree_lines.append(f"{prefix}{connector}{icon} {display}")
                else:
                    tree_lines.append(f"> {prefix}- {icon} {display}")

    root_name = os.path.basename(os.path.abspath(path))
    if style == "tree":
        tree_lines.append(f"{root_name}/")
        walk(path, "", 0)
        return "```text\n" + "\n".join(tree_lines) + "\n```"
    else:
        tree_lines.append(f"> 📂 **[{root_name}](.)/**")
        walk(path, "", 0)
        return "\n".join(tree_lines)

if __name__ == "__main__":
    print("""
╔════╗╔═══╗╔═══╗╔═══╗    ╔═══╗╔═══╗╔═╗ ╔╗╔═══╗╔═══╗╔═══╗╔════╗╔═══╗╔═══╗
║╔╗╔╗║║╔═╗║║╔══╝║╔══╝    ║╔═╗║║╔══╝║║╚╗║║║╔══╝║╔═╗║║╔═╗║║╔╗╔╗║║╔═╗║║╔═╗║
╚╝║║╚╝║╚═╝║║╚══╗║╚══╗    ║║ ╚╝║╚══╗║╔╗╚╝║║╚══╗║╚═╝║║║ ║║╚╝║║╚╝║║ ║║║╚═╝║
  ║║  ║╔╗╔╝║╔══╝║╔══╝    ║║╔═╗║╔══╝║║╚╗║║║╔══╝║╔╗╔╝║╚═╝║  ║║  ║║ ║║║╔╗╔╝
 ╔╝╚╗ ║║║╚╗║╚══╗║╚══╗    ║╚╩═║║╚══╗║║ ║║║║╚══╗║║║╚╗║╔═╗║ ╔╝╚╗ ║╚═╝║║║║╚╗
 ╚══╝ ╚╝╚═╝╚═══╝╚═══╝    ╚═══╝╚═══╝╚╝ ╚═╝╚═══╝╚╝╚═╝╚╝ ╚╝ ╚══╝ ╚═══╝╚╝╚═╝
Welcome to the Folder Structure Generator!
========================================================================""")
    folder = input("Enter folder path: ").strip()
    mapping = load_mapping()
    style = ask_style()

    if style == "callout":
        use_links = ask_bool("Use Markdown links? (e.g. [filename.py](filename.py))")
        use_backticks = ask_bool("Wrap filenames in backticks? (e.g. `filename.py`)")
        use_placeholders = ask_bool("Add placeholder descriptions to entries?")
    else:  # tree
        use_links = use_backticks = False
        use_placeholders = ask_bool("Add placeholder descriptions to entries?")

    max_depth = ask_depth("How many folder levels deep to include?")
    ignored_folders = set()
    if ask_bool("Ignore .git folder?"): ignored_folders.add(".git")
    if ask_bool("Ignore other folders?"):
        others = input("Enter folder names to ignore (comma separated): ").strip()
        if others: ignored_folders.update([f.strip() for f in others.split(",")])

    output = generate_tree(folder, mapping, use_links, use_backticks, ignored_folders, max_depth, use_placeholders, style)
    print("========================================================================")
    print(output)

    # Save to file
    if ask_bool("Save output to file?"):
        save_path = input("Enter file path (leave blank for same folder as script): ").strip()
        if not save_path:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ext = ".txt" if style == "tree" else ".md"
            save_path = os.path.join(script_dir, f"tree_output{ext}")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Saved to {save_path}")
