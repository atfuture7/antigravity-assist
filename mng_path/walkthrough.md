# Path Management Script Walkthrough

I have created a script `manage_path.sh` to help you manage your `$PATH` variable.

## Features
- **Add Directory**: Adds a directory to your PATH if it's not already there.
- **Remove Directory**: Removes a directory from your PATH.
- **Export Option**: Generates the `export` command for you to run or save.

## Usage Examples

### 1. Add a Directory
To see what the PATH would look like after adding a directory:
```bash
./manage_path.sh add /opt/my-app/bin
```

### 2. Remove a Directory
To see what the PATH would look like after removing a directory:
```bash
./manage_path.sh remove /usr/local/games
```

### 3. Apply Changes (Export)
Since a script cannot modify your current shell's environment directly, use the `--export` flag with `eval`:
```bash
eval $(./manage_path.sh add /opt/my-app/bin --export)
```
Or append it to your `.bashrc`:
```bash
./manage_path.sh add /opt/my-app/bin --export >> ~/.bashrc
```

## Verification Results
I ran the following tests to verify functionality:

1.  **Add new directory**:
    - Command: `./manage_path.sh add /tmp/test_dir`
    - Result: `/tmp/test_dir` was appended to the PATH.

2.  **Remove existing directory**:
    - Command: `./manage_path.sh remove /usr/bin`
    - Result: `/usr/bin` was removed from the PATH.

3.  **Export output**:
    - Command: `./manage_path.sh add /tmp/test_dir --export`
    - Result: Printed `export PATH="..."` correctly.

4.  **Idempotency**:
    - Command: `./manage_path.sh add /usr/bin` (already exists)
    - Result: PATH remained unchanged.
