import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from config import PROTECTED_SYSTEM_DIRS, PROTECTED_EXACT_ROOTS
from services.history_service import log_operation

LOCATIONS = {
    "desktop": os.path.expanduser("~/Desktop"),
    "downloads": os.path.expanduser("~/Downloads"),
    "documents": os.path.expanduser("~/Documents"),
    "pictures": os.path.expanduser("~/Pictures"),
    "music": os.path.expanduser("~/Music"),
}


def resolve_path(location_or_path: str) -> str:
    """Resolve standard location aliases (desktop, downloads, etc.) or arbitrary paths."""
    if not location_or_path:
        return ""
    
    loc_key = location_or_path.strip().lower()
    if loc_key in LOCATIONS:
        primary_path = LOCATIONS[loc_key]
        # In case OneDrive folder backup is in use on Windows
        if not os.path.exists(primary_path):
            onedrive_folder = os.path.join(os.path.expanduser("~"), "OneDrive", location_or_path.strip().capitalize())
            if os.path.exists(onedrive_folder):
                return str(Path(onedrive_folder).resolve())
        return str(Path(primary_path).resolve())

    # Check if string starts with a location alias followed by slash (e.g. "desktop/myfile.txt")
    for key, base_dir in LOCATIONS.items():
        if loc_key.startswith(f"{key}/") or loc_key.startswith(f"{key}\\"):
            relative_part = location_or_path.strip()[len(key) + 1:]
            base = resolve_path(key)
            return str((Path(base) / relative_part).resolve())

    return str(Path(os.path.expanduser(location_or_path)).resolve())


def is_safe_to_delete(file_path: str) -> tuple[bool, str]:
    """
    Ensure the path is NOT a system file or protected operating system folder.
    Returns (is_safe, reason).
    """
    try:
        resolved = Path(file_path).resolve()
    except Exception as e:
        return False, f"Invalid path syntax: {e}"

    # 1. Block root of drives (e.g. C:\, D:\)
    if resolved == Path(resolved.anchor):
        return False, "Cannot delete drive root."

    # 2. Block exact root folders like C:\Users or C:\Users\username directly
    for exact_root in PROTECTED_EXACT_ROOTS:
        if resolved == exact_root:
            return False, f"Cannot delete root directory '{resolved}'."

    # 3. Block system protected root directories and anything inside them
    for protected in PROTECTED_SYSTEM_DIRS:
        try:
            if resolved == protected or protected in resolved.parents:
                return False, f"Access denied: '{resolved}' is inside a protected system folder ({protected})."
        except Exception:
            continue

    # 4. Block critical Windows system files
    blocked_filenames = {
        "bootmgr", "bootnxt", "ntldr", "pagefile.sys", "swapfile.sys", 
        "hiberfil.sys", "dumpstack.log.tmp", "autoexec.bat", "config.sys"
    }
    if resolved.name.lower() in blocked_filenames:
        return False, f"Cannot delete critical system file '{resolved.name}'."

    return True, ""


def create_file(name: str, location: str, content: str = "") -> Dict[str, Any]:
    """Create a new file with specified content in the given location."""
    folder_path = resolve_path(location)
    os.makedirs(folder_path, exist_ok=True)
    
    full_path = Path(folder_path) / name
    
    # Write content
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content or "")

    stat = full_path.stat()
    result = {
        "name": full_path.name,
        "path": str(full_path),
        "size": stat.st_size,
        "created": True
    }
    log_operation("create_file", {"name": name, "location": location, "content_length": len(content or "")}, "success", data=result)
    return result


def delete_file(path: str) -> Dict[str, Any]:
    """Safely delete a file or directory with system safety protection."""
    resolved = resolve_path(path)
    p = Path(resolved)

    if not p.exists():
        err = f"File or path not found: {resolved}"
        log_operation("delete_file", {"path": path, "resolved": resolved}, "error", error=err)
        raise FileNotFoundError(err)

    safe, reason = is_safe_to_delete(resolved)
    if not safe:
        log_operation("delete_file", {"path": path, "resolved": resolved}, "error", error=reason)
        raise PermissionError(reason)

    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()

    result = {"path": str(p), "deleted": True}
    log_operation("delete_file", {"path": path, "resolved": resolved}, "success", data=result)
    return result


def move_file(source: str, destination: str) -> Dict[str, Any]:
    """Move a file or folder to a new destination."""
    src_resolved = resolve_path(source)
    dst_resolved = resolve_path(destination)
    
    src_p = Path(src_resolved)
    if not src_p.exists():
        err = f"Source not found: {src_resolved}"
        log_operation("move_file", {"source": source, "destination": destination}, "error", error=err)
        raise FileNotFoundError(err)

    dst_p = Path(dst_resolved)
    
    # If destination is a directory, move into it
    if dst_p.is_dir():
        final_dest = dst_p / src_p.name
    else:
        # Destination specifies directory or new file name; ensure parent dir exists
        dst_p.parent.mkdir(parents=True, exist_ok=True)
        final_dest = dst_p

    moved_path = shutil.move(str(src_p), str(final_dest))
    result = {"source": str(src_p), "destination": str(moved_path)}
    log_operation("move_file", {"source": source, "destination": destination}, "success", data=result)
    return result


def copy_file(source: str, destination: str) -> Dict[str, Any]:
    """Copy a file or directory to a destination."""
    src_resolved = resolve_path(source)
    dst_resolved = resolve_path(destination)

    src_p = Path(src_resolved)
    if not src_p.exists():
        err = f"Source not found: {src_resolved}"
        log_operation("copy_file", {"source": source, "destination": destination}, "error", error=err)
        raise FileNotFoundError(err)

    dst_p = Path(dst_resolved)

    if dst_p.is_dir():
        final_dest = dst_p / src_p.name
    else:
        dst_p.parent.mkdir(parents=True, exist_ok=True)
        final_dest = dst_p

    if src_p.is_dir():
        shutil.copytree(str(src_p), str(final_dest), dirs_exist_ok=True)
        copied_path = str(final_dest)
    else:
        copied_path = shutil.copy2(str(src_p), str(final_dest))

    result = {"source": str(src_p), "destination": str(copied_path)}
    log_operation("copy_file", {"source": source, "destination": destination}, "success", data=result)
    return result


def create_folder(name: str, location: str) -> Dict[str, Any]:
    """Create a new folder in the specified location."""
    parent_path = resolve_path(location)
    folder_path = Path(parent_path) / name
    folder_path.mkdir(parents=True, exist_ok=True)

    result = {"name": name, "path": str(folder_path), "created": True}
    log_operation("create_folder", {"name": name, "location": location}, "success", data=result)
    return result


def list_files(location: str, extension: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all files and folders in a location, optionally filtered by extension."""
    folder_path = resolve_path(location)
    p = Path(folder_path)

    if not p.exists() or not p.is_dir():
        err = f"Directory not found: {folder_path}"
        log_operation("list_files", {"location": location, "extension": extension}, "error", error=err)
        raise FileNotFoundError(err)

    ext_filter = extension.lower().strip() if extension else None
    if ext_filter and not ext_filter.startswith("."):
        ext_filter = f".{ext_filter}"

    items = []
    try:
        for entry in p.iterdir():
            # Filter by extension if requested (only filters files, keeps directories or filters as desired)
            if ext_filter:
                if entry.is_file() and entry.suffix.lower() != ext_filter:
                    continue

            stat = entry.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
            items.append({
                "name": entry.name,
                "path": str(entry.resolve()),
                "is_dir": entry.is_dir(),
                "size": stat.st_size if entry.is_file() else 0,
                "modified_time": mod_time,
                "extension": entry.suffix.lower() if entry.is_file() else None,
            })
    except Exception as e:
        log_operation("list_files", {"location": location, "extension": extension}, "error", error=str(e))
        raise

    log_operation("list_files", {"location": location, "extension": extension}, "success", data={"count": len(items)})
    return items


def open_file(path: str) -> Dict[str, Any]:
    """Open a file with the system default application."""
    resolved = resolve_path(path)
    p = Path(resolved)

    if not p.exists():
        err = f"File not found: {resolved}"
        log_operation("open_file", {"path": path, "resolved": resolved}, "error", error=err)
        raise FileNotFoundError(err)

    try:
        # On Windows, os.startfile launches the file in its default registered application
        os.startfile(str(p))
    except Exception as e:
        log_operation("open_file", {"path": path, "resolved": resolved}, "error", error=str(e))
        raise

    result = {"path": str(p), "opened": True}
    log_operation("open_file", {"path": path, "resolved": resolved}, "success", data=result)
    return result


def search_files(query: str, location: str, max_results: int = 100) -> List[Dict[str, Any]]:
    """Search for files matching the query keyword in a location recursively."""
    folder_path = resolve_path(location)
    p = Path(folder_path)

    if not p.exists() or not p.is_dir():
        err = f"Directory not found: {folder_path}"
        log_operation("search_files", {"query": query, "location": location}, "error", error=err)
        raise FileNotFoundError(err)

    query_lower = query.lower().strip()
    results = []

    try:
        for root, dirs, files in os.walk(str(p)):
            # Search in files
            for file_name in files:
                if query_lower in file_name.lower():
                    full_file = Path(root) / file_name
                    try:
                        stat = full_file.stat()
                        results.append({
                            "name": file_name,
                            "path": str(full_file.resolve()),
                            "is_dir": False,
                            "size": stat.st_size,
                            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "extension": full_file.suffix.lower(),
                        })
                    except Exception:
                        continue
                if len(results) >= max_results:
                    break

            # Search in directories
            for dir_name in dirs:
                if query_lower in dir_name.lower():
                    full_dir = Path(root) / dir_name
                    try:
                        stat = full_dir.stat()
                        results.append({
                            "name": dir_name,
                            "path": str(full_dir.resolve()),
                            "is_dir": True,
                            "size": 0,
                            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "extension": None,
                        })
                    except Exception:
                        continue
                if len(results) >= max_results:
                    break

            if len(results) >= max_results:
                break
    except Exception as e:
        log_operation("search_files", {"query": query, "location": location}, "error", error=str(e))
        raise

    log_operation("search_files", {"query": query, "location": location}, "success", data={"total_found": len(results)})
    return results
