# Linux Memory Searcher

This Python script allows you to search for a specific string within the memory of running processes on a Linux system. The script offers various options to filter which processes to search, display context around matches, and control output formatting.

## Features

- **Search Process Memory:** Find a specific string in the memory of all or selected running processes.
- **Context Display:** Show a specified number of bytes before and after the match, similar to `grep -C`.
- **Process Filtering:**
  - **Ignore PIDs:** Exclude specific PIDs from the search.
  - **Search Specific PIDs:** Only search the memory of certain PIDs.
  - **Ignore Process Names:** Skip processes with specific names (e.g., `python`, `bash`).
- **Match Highlighting:** The matching string is highlighted in red by default. You can disable color output if desired.
- **Debug Output:** Optionally enable debug output to trace the script's execution.

## Usage

```bash
sudo python2 search_memory.py <search_string> [options]
```

### Options

- `search_string`: The string to search for in process memory.

- `--context`, `-C`: Show this many bytes of context around the match. For example, `--context 20`.

- `--ignore-pids`, `-I`: Comma-separated list of PIDs to ignore. For example, `--ignore-pids 1234,5678`.

- `--search-pids`, `-S`: Comma-separated list of PIDs to search. Only these PIDs will be searched. For example, `--search-pids 1234,5678`.

- `--ignore-names`, `-N`: Comma-separated list of process names to ignore. For example, `--ignore-names bash,python`.

- `--debug`: Enable debug output to trace the script's execution.

- `--no-color`: Disable colored output (highlighting of matches in red).

## Examples

1. **Search for a string with highlighted matches:**

   ```bash
   sudo python2 search_memory.py weaeuvb2y
   ```

2. **Search only specific PIDs:**

   ```bash
   sudo python2 search_memory.py weaeuvb2y --search-pids 1234,5678
   ```

3. **Ignore specific process names:**

   ```bash
   sudo python2 search_memory.py weaeuvb2y --ignore-names bash,python
   ```

4. **Show context around matches:**

   ```bash
   sudo python2 search_memory.py weaeuvb2y --context 20
   ```

5. **Disable color output:**

   ```bash
   sudo python2 search_memory.py weaeuvb2y --no-color
   ```

6. **Enable debug output:**

   ```bash
   sudo python2 search_memory.py weaeuvb2y --debug
   ```

## Note

This script was generated with the assistance of ChatGPT, an AI language model developed by OpenAI. It is designed to provide a flexible and powerful way to search process memory on Linux systems.

## Requirements

- Python 2.7
- Root privileges (since accessing `/proc/[pid]/mem` requires root access)

## License

Feel free to use, modify, and distribute this script as needed.
