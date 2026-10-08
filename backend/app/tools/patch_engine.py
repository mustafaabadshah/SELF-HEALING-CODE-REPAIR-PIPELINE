import ast
import difflib
import re
from typing import Tuple, Dict, Any


class PatchError(Exception):
    pass


def parse_and_validate_syntax(code: str, filename: str = "<patch>") -> None:
    """Validates that modified Python code parses without syntax errors."""
    try:
        ast.parse(code, filename=filename)
    except SyntaxError as e:
        raise PatchError(f"Syntax error introduced: {e.msg} on line {e.lineno}")


def apply_search_replace(original: str, search_block: str, replace_block: str) -> str:
    """Applies search-and-replace block matching."""
    search_clean = search_block.strip("\r\n")
    replace_clean = replace_block.strip("\r\n")

    if search_clean in original:
        return original.replace(search_clean, replace_clean, 1)

    # Normalize whitespace/indentation fallback
    orig_lines = original.splitlines()
    search_lines = search_clean.splitlines()

    # Search window
    n = len(search_lines)
    for i in range(len(orig_lines) - n + 1):
        window = orig_lines[i : i + n]
        if [l.strip() for l in window] == [l.strip() for l in search_lines]:
            # Found matching lines ignoring minor indentation differences
            new_lines = orig_lines[:i] + replace_clean.splitlines() + orig_lines[i + n :]
            return "\n".join(new_lines)

    raise PatchError("Search block could not be located in original file.")


def apply_unified_diff(original: str, diff_text: str) -> str:
    """Applies unified diff patch to original text."""
    orig_lines = original.splitlines(keepends=True)
    diff_lines = diff_text.splitlines(keepends=True)

    # Try applying hunk by hunk
    hunks = []
    current_hunk = []
    for line in diff_lines:
        if line.startswith("@@"):
            if current_hunk:
                hunks.append(current_hunk)
            current_hunk = [line]
        elif current_hunk:
            current_hunk.append(line)
    if current_hunk:
        hunks.append(current_hunk)

    if not hunks:
        # Check if diff is actually a search/replace
        if "<<<<<<< SEARCH" in diff_text and "=======" in diff_text:
            pattern = re.compile(r"<<<<<<< SEARCH\s*\n(.*?)\n=======\s*\n(.*?)\n>>>>>>> REPLACE", re.DOTALL)
            match = pattern.search(diff_text)
            if match:
                return apply_search_replace(original, match.group(1), match.group(2))
        raise PatchError("No valid diff hunks or search/replace blocks found in patch.")

    # Reconstruct text using unified diff
    result_lines = []
    orig_idx = 0

    for hunk in hunks:
        # Parse @@ -start,len +start,len @@
        header = hunk[0]
        match = re.match(r"^@@\s*-(\d+)(?:,(\d+))?\s*\+(\d+)(?:,(\d+))?\s*@@", header)
        if not match:
            continue
        old_start = int(match.group(1)) - 1
        
        # Copy lines before hunk
        while orig_idx < old_start and orig_idx < len(orig_lines):
            result_lines.append(orig_lines[orig_idx])
            orig_idx += 1

        for line in hunk[1:]:
            if line.startswith("-"):
                # Remove from original
                orig_idx += 1
            elif line.startswith("+"):
                # Add to result
                result_lines.append(line[1:])
            elif line.startswith(" "):
                # Context line
                if orig_idx < len(orig_lines):
                    result_lines.append(orig_lines[orig_idx])
                    orig_idx += 1
                else:
                    result_lines.append(line[1:])

    # Copy remaining lines
    while orig_idx < len(orig_lines):
        result_lines.append(orig_lines[orig_idx])
        orig_idx += 1

    return "".join(result_lines)


def apply_patch_to_text(original: str, patch_text: str, filename: str = "module.py") -> Tuple[str, Dict[str, Any]]:
    """
    Main entry point for patch application.
    Supports both unified diff and SEARCH/REPLACE blocks.
    Validates Python AST before returning.
    """
    patch_clean = patch_text.strip()
    new_text = original

    if "<<<<<<< SEARCH" in patch_clean and "=======" in patch_clean:
        pattern = re.compile(r"<<<<<<< SEARCH\s*\n(.*?)\n=======\s*\n(.*?)\n>>>>>>> REPLACE", re.DOTALL)
        matches = list(pattern.finditer(patch_clean))
        if not matches:
            raise PatchError("Malformed SEARCH/REPLACE block.")
        for match in matches:
            new_text = apply_search_replace(new_text, match.group(1), match.group(2))
    elif "@@" in patch_clean or patch_clean.startswith("---"):
        new_text = apply_unified_diff(original, patch_clean)
    else:
        # If the patch is full new code content
        if "def " in patch_clean or "class " in patch_clean or "import " in patch_clean:
            new_text = patch_clean
        else:
            raise PatchError("Unrecognized patch format. Provide unified diff or <<<<<<< SEARCH ... ======= ... >>>>>>> REPLACE")

    # Validate Python syntax if file is .py
    if filename.endswith(".py"):
        parse_and_validate_syntax(new_text, filename=filename)

    # Compute diff stats
    orig_lines = original.splitlines()
    new_lines = new_text.splitlines()
    diff = list(difflib.unified_diff(orig_lines, new_lines, fromfile=f"a/{filename}", tofile=f"b/{filename}", lineterm=""))

    lines_added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    lines_removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))

    return new_text, {
        "success": True,
        "diff": "\n".join(diff),
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "files_changed": [filename],
    }
