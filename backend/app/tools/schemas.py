from typing import List, Optional
from pydantic import BaseModel, Field

# Native tool schemas in OpenAI / Groq standard JSON schema format
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the text contents of a file within the repair workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path of the workspace file to read (e.g. 'buggy_module.py')."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files in the repair workspace directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Subdirectory to inspect (defaults to root '.').",
                        "default": "."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_metadata",
            "description": "Retrieve file metadata including size, language, modification time, and SHA-256 hash.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path of the workspace file."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "apply_patch",
            "description": "Apply a unified diff or search/replace patch to a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path of the target file to modify."
                    },
                    "patch": {
                        "type": "string",
                        "description": "Unified diff patch string OR search-and-replace block with <<<<<<< SEARCH ... ======= ... >>>>>>> REPLACE"
                    }
                },
                "required": ["path", "patch"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite full contents of a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path of the workspace file to write."
                    },
                    "content": {
                        "type": "string",
                        "description": "Complete text content to write."
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_diff",
            "description": "Inspect the current unified git diff of all modifications made so far in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_target_test",
            "description": "Execute the failing target pytest test inside the isolated sandbox and get structured results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_path": {
                        "type": "string",
                        "description": "Relative path to target test file or spec (e.g. 'test_target.py' or 'test_target.py::test_case')."
                    }
                },
                "required": ["test_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_regression_tests",
            "description": "Execute the full existing regression test suite inside the isolated sandbox to detect regressions.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_checkpoint",
            "description": "Create a rollback checkpoint of the workspace state before attempting changes.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rollback",
            "description": "Rollback the workspace to a previously saved checkpoint.",
            "parameters": {
                "type": "object",
                "properties": {
                    "checkpoint_id": {
                        "type": "string",
                        "description": "The checkpoint identifier returned by create_checkpoint."
                    }
                },
                "required": ["checkpoint_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_test_summary",
            "description": "Get a compact structured summary of recent test runs in the current attempt.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


# Pydantic parameter models for validation
class ReadFileParams(BaseModel):
    path: str


class ListFilesParams(BaseModel):
    directory: str = "."


class GetFileMetadataParams(BaseModel):
    path: str


class ApplyPatchParams(BaseModel):
    path: str
    patch: str


class WriteFileParams(BaseModel):
    path: str
    content: str


class RunTargetTestParams(BaseModel):
    test_path: str


class RollbackParams(BaseModel):
    checkpoint_id: str
