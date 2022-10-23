def human_readable_size(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(int(num)) < 1024.0:
            return f"{num:3.2f}{unit}{suffix}"
        num /= 1024.0
    return num