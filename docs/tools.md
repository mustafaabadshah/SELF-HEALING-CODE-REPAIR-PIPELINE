# Native Tool Specifications

The pipeline uses **Native Groq Function Calling** rather than raw text regex parsing. The models output structured function calls that match validated schemas and execute in the backend tool layer.

---

## Tool Catalog

### 1. `read_file`
- **Description**: Reads the text content of a file within the repair workspace.
- **Parameters**:
  - `path` (string, required): Relative path of the workspace file to read.
- **Security**: Path traversal blocked. Non-workspace paths rejected.

### 2. `list_files`
- **Description**: Lists all files in the repair workspace.
- **Parameters**:
  - `directory` (string, optional, default: `.`): Subdirectory to inspect.
- **Returns**: Array of relative file paths.

### 3. `get_file_metadata`
- **Description**: Retrieves metadata for a workspace file.
- **Parameters**:
  - `path` (string, required): Relative path.
- **Returns**: File size in bytes, language, modification timestamp, SHA-256 hash.

### 4. `apply_patch`
- **Description**: Applies unified diff or search-and-replace block to modify code.
- **Parameters**:
  - `path` (string, required): File to modify.
  - `patch` (string, required): Unified diff or `<<<<<<< SEARCH ... ======= ... >>>>>>> REPLACE` format.
- **Validation**: AST syntax validation for `.py` files. Rejects modifying test suites.
- **Returns**: `success`, `diff`, `lines_added`, `lines_removed`, `files_changed`.

### 5. `write_file`
- **Description**: Writes or overwrites entire contents of a workspace file.
- **Parameters**:
  - `path` (string, required): Relative file path.
  - `content` (string, required): Full text content.
- **Security**: Modifying test files is restricted to prevent agents from bypassing tests.

### 6. `get_diff`
- **Description**: Computes the unified git diff between initial state and current state.
- **Parameters**: None.
- **Returns**: Unified diff string.

### 7. `run_target_test`
- **Description**: Executes the target failing pytest test inside the isolated sandbox.
- **Parameters**:
  - `test_path` (string, optional): Specific test file or `file::test_name` spec.
- **Returns**: Structured result containing `passed`, `exit_code`, `duration_ms`, `stdout`, `stderr`, `failure_type`.

### 8. `run_regression_tests`
- **Description**: Executes the existing regression test suites inside the sandbox.
- **Parameters**: None.
- **Returns**: `passed`, `total`, `passed_tests`, `failed_tests`, `failed_names`, `stdout`, `stderr`.

### 9. `create_checkpoint`
- **Description**: Creates a Git commit checkpoint of the workspace state.
- **Parameters**: None.
- **Returns**: Checkpoint ID string.

### 10. `rollback`
- **Description**: Rolls back workspace to a previously created checkpoint.
- **Parameters**:
  - `checkpoint_id` (string, required): Checkpoint ID.
- **Returns**: `success`, `checkpoint_id`.

### 11. `get_test_summary`
- **Description**: Returns compact test summary for agents.
- **Parameters**: None.
- **Returns**: Object with latest target and regression results.
