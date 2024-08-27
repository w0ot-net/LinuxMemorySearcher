import os
import re
import sys
import argparse

def get_process_name(pid):
    try:
        with open('/proc/{}/comm'.format(pid), 'r') as f:
            return f.read().strip()
    except IOError:
        return "Unknown"

def highlight_match(data, search_string, use_colors):
    if use_colors:
        red_start = "\033[91m"
        red_end = "\033[0m"
        return data.replace(search_string, red_start + search_string + red_end)
    else:
        return data

def should_search_process(pid, process_name, search_pids, ignore_names):
    if search_pids and pid not in search_pids:
        return False
    if process_name in ignore_names:
        return False
    return True

def search_memory_for_string(search_string, search_pids=None, ignore_pids=None, ignore_names=None, context_lines=0, debug=False, use_colors=True):
    search_bytes = search_string
    chunk_size = 1024 * 1024  # 1MB chunks
    max_address = 0x7FFFFFFFFFFF  # Limit to avoid high memory addresses causing overflow

    current_pid = str(os.getpid())
    if ignore_pids is None:
        ignore_pids = []
    ignore_pids.append(current_pid)

    if debug:
        print("Starting memory search for '{}'".format(search_string))
        print("Ignoring PIDs: {}".format(", ".join(ignore_pids)))
        if search_pids:
            print("Searching only these PIDs: {}".format(", ".join(search_pids)))
        if ignore_names:
            print("Ignoring processes with these names: {}".format(", ".join(ignore_names)))

    for pid in os.listdir('/proc'):
        if pid.isdigit() and pid not in ignore_pids:
            process_name = get_process_name(pid)
            if not should_search_process(pid, process_name, search_pids, ignore_names):
                continue

            if debug:
                print("Checking process with PID: {} ({})".format(pid, process_name))
            mem_path = '/proc/{}/mem'.format(pid)
            maps_path = '/proc/{}/maps'.format(pid)

            try:
                with open(maps_path, 'r') as maps_file:
                    if debug:
                        print("  Opened maps file: {}".format(maps_path))
                    for line in maps_file:
                        if debug:
                            print("    Processing line: {}".format(line.strip()))
                        m = re.match(r'([0-9a-fA-F]+)-([0-9a-fA-F]+) ', line)
                        if m:
                            start = int(m.group(1), 16)
                            end = int(m.group(2), 16)
                            size = end - start

                            if start > max_address:
                                if debug:
                                    print("    Skipping large address region: {}-{}".format(hex(start), hex(end)))
                                continue

                            if debug:
                                print("    Memory region: {}-{} (size: {})".format(hex(start), hex(end), size))

                            try:
                                with open(mem_path, 'rb') as mem_file:
                                    if debug:
                                        print("    Opened mem file: {}".format(mem_path))
                                    current_offset = 0
                                    mem_file.seek(start)
                                    if debug:
                                        print("    Seeking to start address: {}".format(hex(start)))

                                    while current_offset < size:
                                        read_size = min(chunk_size, size - current_offset)
                                        if debug:
                                            print("    Reading chunk: offset={} size={}".format(current_offset, read_size))
                                        chunk = mem_file.read(read_size)

                                        if search_bytes in chunk:
                                            match_index = chunk.find(search_bytes)
                                            match_start = start + current_offset + match_index
                                            match_end = match_start + len(search_bytes)
                                            print("FOUND '{}' in process {} ({}) at address range {}-{}".format(
                                                highlight_match(search_string, search_string, use_colors), pid, process_name, hex(match_start), hex(match_end)
                                            ))

                                            if context_lines > 0:
                                                context_start = max(0, match_index - context_lines)
                                                context_end = min(len(chunk), match_index + len(search_bytes) + context_lines)
                                                context_data = chunk[context_start:context_end]
                                                print("Context ({} bytes before and after match):".format(context_lines))
                                                print(highlight_match(context_data, search_string, use_colors))

                                        current_offset += read_size
                                        if debug:
                                            print("    Moving to next chunk, new offset: {}".format(current_offset))

                            except (OSError, IOError) as e:
                                if debug:
                                    print("    Failed to open/read memory file for PID {}: {}".format(pid, e))
                                continue
            except (OSError, IOError) as e:
                if debug:
                    print("  Failed to open maps file for PID {}: {}".format(pid, e))
                continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for a string in the memory of running processes.")
    parser.add_argument("search_string", help="The string to search for in process memory.")
    parser.add_argument("--context", "-C", type=int, default=0, help="Show this many bytes of context around the match.")
    parser.add_argument("--ignore-pids", "-I", help="Comma-separated list of PIDs to ignore.")
    parser.add_argument("--search-pids", "-S", help="Comma-separated list of PIDs to search (only these PIDs will be searched).")
    parser.add_argument("--ignore-names", "-N", help="Comma-separated list of process names to ignore.")
    parser.add_argument("--debug", action="store_true", help="Enable debug output.")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output.")

    args = parser.parse_args()
    
    ignore_pids = args.ignore_pids.split(',') if args.ignore_pids else []
    search_pids = args.search_pids.split(',') if args.search_pids else []
    ignore_names = args.ignore_names.split(',') if args.ignore_names else []
    use_colors = not args.no_color

    search_memory_for_string(args.search_string, search_pids=search_pids, ignore_pids=ignore_pids, ignore_names=ignore_names, context_lines=args.context, debug=args.debug, use_colors=use_colors)

