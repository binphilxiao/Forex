# ClickHouse Configurator - Design Document

## Document Information
- **Project**: Forex Data Management System
- **Component**: ClickHouse Database Configurator
- **Version**: 1.0.0
- **Date**: 2025-10-06
- **Author**: Development Team

---

## 1. Architecture Overview

### 1.1 System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Command-Line Interface (argparse)                    │   │
│  │  - Interactive prompts                                │   │
│  │  - Command-line arguments                             │   │
│  │  - Help text and examples                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ClickHouseConfigurator Class                         │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ Configuration Management                        │  │   │
│  │  │ - load_existing_config()                        │  │   │
│  │  │ - save_config()                                 │  │   │
│  │  │ - interactive_configure()                       │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ Validation                                      │  │   │
│  │  │ - validate_host()                               │  │   │
│  │  │ - validate_port()                               │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ Connection Testing                              │  │   │
│  │  │ - test_connection()                             │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ Logging                                         │  │   │
│  │  │ - log()                                         │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Data Persistence Layer                     │
│  ┌─────────────────┐  ┌──────────────────┐                  │
│  │ Configuration   │  │  Log Files       │                  │
│  │ File (JSON)     │  │  (*.log)         │                  │
│  └─────────────────┘  └──────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   External Systems                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ClickHouse Database Server                           │   │
│  │  (Connection testing via clickhouse-connect)          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Design Principles
1. **Single Responsibility**: Each method has one clear purpose
2. **Separation of Concerns**: UI, business logic, and data persistence are separated
3. **Fail-Safe**: Graceful degradation when optional dependencies missing
4. **User-Friendly**: Clear prompts, helpful errors, visual indicators
5. **Testability**: All logic is unit-testable

---

## 2. Class Design

### 2.1 ClickHouseConfigurator Class

#### 2.1.1 Class Overview
```python
class ClickHouseConfigurator:
    """
    Main class for database configuration management.
    Handles user interaction, validation, file I/O, and connection testing.
    """
```

#### 2.1.2 Class Attributes
```python
DEFAULT_CONFIG = {
    'host': 'localhost',
    'port': 8123,
    'username': 'default',
    'password': '',
    'database': 'forex'
}
```

**Purpose**: Provides sensible defaults for first-time configuration

#### 2.1.3 Instance Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `config_file` | str | Path to configuration JSON file |
| `log_dir` | Path | Directory for log files |
| `log_file` | Path | Current log file path (timestamped) |

---

## 3. Method Design

### 3.1 Initialization

#### `__init__(config_file, log_dir)`
**Purpose**: Initialize configurator with file paths

**Parameters**:
- `config_file` (str): Path to configuration file
- `log_dir` (str): Directory for logs

**Logic**:
1. Store configuration file path
2. Create log directory if needed
3. Generate timestamped log file path

**Returns**: None

---

### 3.2 Logging

#### `log(message, level='INFO')`
**Purpose**: Write log entries to file and console

**Parameters**:
- `message` (str): Log message content
- `level` (str): Log level (INFO, WARNING, ERROR, SUCCESS)

**Logic**:
1. Generate timestamp
2. Format log entry with timestamp and level
3. Append to log file
4. Print to console with appropriate emoji/color

**Output Formatting**:
```python
File:    [2025-10-06 14:30:15] [INFO] Configuration saved
Console: ℹ️  Configuration saved  (for INFO)
Console: ✅ Configuration saved  (for SUCCESS)
Console: ❌ Configuration saved  (for ERROR)
Console: ⚠️  Configuration saved  (for WARNING)
```

**Returns**: None

---

### 3.3 Configuration Management

#### `load_existing_config()`
**Purpose**: Load configuration from file or return defaults

**Logic**:
```python
if file exists:
    try:
        load JSON from file
        log success
        return config
    except:
        log warning
        return DEFAULT_CONFIG
else:
    log "no config found"
    return DEFAULT_CONFIG
```

**Error Handling**:
- File not found: Return defaults
- Invalid JSON: Return defaults
- Permission error: Return defaults

**Returns**: dict (configuration)

---

#### `save_config(config)`
**Purpose**: Save configuration to JSON file

**Parameters**:
- `config` (dict): Configuration to save

**Logic**:
```python
try:
    write JSON to file with indent=4
    log success
    return True
except:
    log error
    return False
```

**JSON Format**:
```json
{
    "host": "localhost",
    "port": 8123,
    "username": "default",
    "password": "",
    "database": "forex"
}
```

**Returns**: bool (success/failure)

---

#### `interactive_configure()`
**Purpose**: Run interactive configuration wizard

**Logic Flow**:
```
1. Display wizard header
2. Load existing config for defaults
3. For each parameter:
   a. Display prompt with default value
   b. Get user input
   c. If empty, use default
   d. Validate input
   e. If invalid, repeat
   f. Store in config dict
4. Return completed config
```

**User Interaction**:
```
Enter ClickHouse host [localhost]: █
Enter ClickHouse port [8123]: █
Enter username [default]: █
Enter password (input hidden):
Password: ████
Enter database name [forex]: █
```

**Returns**: dict (configuration)

---

### 3.4 Validation

#### `validate_host(host)`
**Purpose**: Validate host address

**Parameters**:
- `host` (str): Host address to validate

**Validation Rules**:
- Not None
- Not empty string
- Not only whitespace

**Logic**:
```python
if not host or not host.strip():
    return False
return True
```

**Returns**: bool (valid/invalid)

---

#### `validate_port(port)`
**Purpose**: Validate port number

**Parameters**:
- `port` (int|str): Port number to validate

**Validation Rules**:
- Can be converted to integer
- Between 1 and 65535 (inclusive)

**Logic**:
```python
try:
    port_int = int(port)
    return 1 <= port_int <= 65535
except ValueError:
    return False
```

**Returns**: bool (valid/invalid)

---

### 3.5 Connection Testing

#### `test_connection(config)`
**Purpose**: Test database connection with provided configuration

**Parameters**:
- `config` (dict): Configuration to test

**Logic Flow**:
```
1. Check if clickhouse-connect available
   - If not, warn and return False
2. Display "Testing connection..." message
3. Try to connect:
   a. Create client with config parameters
   b. Query version: SELECT version()
   c. Extract version string
   d. Query database existence
   e. Display success with details
   f. Close client
   g. Return True
4. If exception:
   a. Log error
   b. Display failure message
   c. Display troubleshooting tips
   d. Return False
```

**Success Output**:
```
✅ Connection successful!
   ClickHouse version: 22.8.1.2
   Host: localhost:8123
   Database: forex
```

**Failure Output**:
```
❌ Connection failed!
   Error: Connection refused

   Please check:
   1. ClickHouse server is running
   2. Host and port are correct
   3. Username and password are valid
   4. Firewall allows connection
```

**Returns**: bool (success/failure)

---

### 3.6 Display

#### `display_config(config)`
**Purpose**: Display configuration summary

**Parameters**:
- `config` (dict): Configuration to display

**Output Format**:
```
============================================================
   Configuration Summary
============================================================
  Host:     localhost
  Port:     8123
  Username: default
  Password: ********
  Database: forex
============================================================
```

**Password Masking**:
- If password exists: Display asterisks (length = password length)
- If empty: Display "(empty)"

**Returns**: None

---

### 3.7 Main Workflow

#### `run(auto_test=True)`
**Purpose**: Execute complete configuration workflow

**Parameters**:
- `auto_test` (bool): Whether to test connection after saving

**Logic Flow**:
```
1. Run interactive_configure()
2. Display configuration summary
3. Ask for confirmation
4. If confirmed:
   a. Save configuration
   b. If auto_test:
      - Test connection
      - Display results
   c. Display log file location
   d. Return True
5. If cancelled:
   a. Log cancellation
   b. Return False
```

**Exception Handling**:
- KeyboardInterrupt: Graceful exit message
- Other exceptions: Log error, display message

**Returns**: bool (success/failure)

---

## 4. Data Structures

### 4.1 Configuration Dictionary
```python
{
    'host': str,        # Host address (IP or hostname)
    'port': int,        # Port number (1-65535)
    'username': str,    # Database username
    'password': str,    # Database password (plain text)
    'database': str     # Database name
}
```

### 4.2 Log Entry Format
```
[TIMESTAMP] [LEVEL] MESSAGE

Example:
[2025-10-06 14:30:15] [INFO] Configuration loaded
[2025-10-06 14:30:20] [SUCCESS] Connection successful
[2025-10-06 14:30:25] [ERROR] Failed to save config
```

---

## 5. File Structure

### 5.1 Configuration File
**Path**: `clickhouse_config.json` (default)  
**Format**: JSON  
**Encoding**: UTF-8  
**Permissions**: User-readable (contains password)

### 5.2 Log Files
**Path**: `logs/clickhouse_config_YYYYMMDD_HHMMSS.log`  
**Format**: Plain text  
**Encoding**: UTF-8  
**Naming**: Timestamp-based to prevent conflicts

---

## 6. Command-Line Interface

### 6.1 Argument Parser Design
```python
parser = argparse.ArgumentParser(
    description='ClickHouse Database Configuration Tool',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=EXAMPLES_TEXT
)

Arguments:
- --config: Custom config file path (default: clickhouse_config.json)
- --no-test: Skip connection testing
- --test-only: Test existing config without modification
- --log-dir: Custom log directory (default: logs)
```

### 6.2 Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Failure (configuration error, connection failed, user cancellation) |

---

## 7. Error Handling

### 7.1 Error Categories

#### File System Errors
- **Config file not found**: Use defaults, log warning
- **Log directory creation failed**: Try to create, fail if impossible
- **Permission denied**: Display error, exit with code 1

#### User Input Errors
- **Invalid host**: Re-prompt with error message
- **Invalid port**: Re-prompt with error message
- **Keyboard interrupt**: Display cancellation message, exit gracefully

#### Connection Errors
- **Library not available**: Warn, skip testing
- **Connection refused**: Display troubleshooting tips
- **Authentication failed**: Display error, suggest checking credentials
- **Timeout**: Display timeout message, suggest network check

### 7.2 Error Messages
All error messages should be:
- **Clear**: Explain what went wrong
- **Actionable**: Suggest how to fix it
- **User-friendly**: No technical jargon unless necessary

---

## 8. Security Considerations

### 8.1 Password Handling
```python
# Input: Use getpass for hidden input
from getpass import getpass
password = getpass("Password: ")

# Display: Mask with asterisks
display = '*' * len(password) if password else '(empty)'

# Storage: Plain text in JSON (user responsible for file permissions)
# WARNING: Documented in manual
```

### 8.2 Configuration File Security
- **Storage**: Plain text JSON
- **Permissions**: User's responsibility
- **Documentation**: Clear warning in manual
- **Alternatives**: Mention environment variables as alternative

---

## 9. Dependencies

### 9.1 Required (Standard Library)
```python
import json         # Configuration file parsing
import os          # File operations
import sys         # System operations
import argparse    # Command-line parsing
from datetime import datetime  # Timestamps
from getpass import getpass   # Secure password input
from pathlib import Path      # Path operations
```

### 9.2 Optional (External)
```python
import clickhouse_connect  # Connection testing
# Gracefully degraded if not available
```

---

## 10. Testing Strategy

### 10.1 Unit Tests
- **Validation tests**: Test all validation methods
- **File I/O tests**: Test save/load with temp files
- **Mock tests**: Mock user input for interactive tests
- **Connection tests**: Mock clickhouse_connect

### 10.2 Integration Tests
- **Full workflow**: Test complete configuration process
- **Error scenarios**: Test all error handling paths
- **Edge cases**: Empty inputs, special characters, etc.

### 10.3 Test Coverage Target
- **Minimum**: 80%
- **Target**: 90%+
- **Critical paths**: 100% (validation, file I/O, connection)

---

## 11. Performance Considerations

### 11.1 Time Complexity
- All operations: O(1) or O(n) where n is small (config keys)
- No complex algorithms
- File I/O is dominant factor

### 11.2 Expected Performance
- Configuration: < 1 second (excluding user input)
- File save: < 100ms
- Connection test: 1-5 seconds (network dependent)

---

## 12. Future Enhancements

### 12.1 Potential Improvements
1. **Encrypted password storage** using cryptography library
2. **Multiple profiles** for different environments
3. **Auto-discovery** of ClickHouse servers on network
4. **SSH tunneling** support for remote connections
5. **Configuration validation** against schema
6. **Backup/restore** of configurations
7. **Environment variable** support for CI/CD

### 12.2 Backward Compatibility
- Current JSON format must remain supported
- New features should be optional
- Migration tools for breaking changes

---

## 13. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-06 | Dev Team | Initial design document |

---

## 14. Diagrams

### 14.1 Configuration Flow
```
Start
  ↓
Load Existing Config (or defaults)
  ↓
Display Wizard Header
  ↓
┌─────────────────────────┐
│ For each parameter:     │
│  1. Show prompt         │
│  2. Get input           │
│  3. Validate            │
│  4. If invalid, retry   │
└─────────────────────────┘
  ↓
Display Summary
  ↓
Request Confirmation
  ↓
Confirmed? ──No──> Cancel (exit)
  │
  Yes
  ↓
Save to JSON
  ↓
Auto-test? ──No──> Complete
  │
  Yes
  ↓
Test Connection
  ↓
Display Results
  ↓
End
```

### 14.2 Connection Test Flow
```
Start Test
  ↓
Check if library available ──No──> Warn, skip test
  ↓
  Yes
  ↓
Create client with config
  ↓
Success? ──No──> Display error + tips
  │               Return False
  Yes
  ↓
Query version
  ↓
Query database existence
  ↓
Display success details
  ↓
Close client
  ↓
Return True
```

---

## 15. Approval

This design document describes the implementation architecture for ClickHouse Configurator v1.0.0.

**Status**: APPROVED  
**Date**: 2025-10-06
