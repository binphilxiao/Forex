# ClickHouse Configurator - Requirements Document

## Document Information
- **Project**: Forex Data Management System
- **Component**: ClickHouse Database Configurator
- **Version**: 1.0.0
- **Date**: 2025-10-06
- **Author**: Development Team

---

## 1. Overview

### 1.1 Purpose
The ClickHouse Configurator is a command-line tool designed to simplify the configuration of ClickHouse database connections for the Forex Data Management System. It replaces the previous `view_clickhouse_tables.py` script with a more user-friendly, interactive configuration wizard.

### 1.2 Scope
This tool handles:
- Interactive database connection configuration
- Configuration file generation and management
- Connection validation and testing
- Secure credential handling
- Detailed logging of configuration activities

---

## 2. Functional Requirements

### 2.1 Interactive Configuration (FR-001)
**Priority**: CRITICAL

**Description**: The tool must provide an interactive command-line interface for configuring database connection parameters.

**Requirements**:
- FR-001.1: Prompt user for host address (IP or hostname)
- FR-001.2: Prompt user for port number (1-65535)
- FR-001.3: Prompt user for username
- FR-001.4: Prompt user for password (with hidden input)
- FR-001.5: Prompt user for database name
- FR-001.6: Display default values from existing configuration
- FR-001.7: Allow accepting defaults by pressing Enter
- FR-001.8: Display configuration summary before saving
- FR-001.9: Request confirmation before saving

**Acceptance Criteria**:
- User can configure all connection parameters interactively
- Default values are shown in prompts
- Password input is hidden for security
- Configuration summary is clear and readable

---

### 2.2 Configuration File Management (FR-002)
**Priority**: CRITICAL

**Description**: The tool must save configuration to a JSON file and load existing configurations.

**Requirements**:
- FR-002.1: Save configuration to `clickhouse_config.json` by default
- FR-002.2: Support custom configuration file paths via command-line argument
- FR-002.3: Load existing configuration and use as defaults
- FR-002.4: Handle missing configuration file gracefully
- FR-002.5: Handle corrupted configuration file gracefully
- FR-002.6: Use UTF-8 encoding for configuration files
- FR-002.7: Format JSON with proper indentation (4 spaces)

**Configuration File Structure**:
```json
{
    "host": "localhost",
    "port": 8123,
    "username": "default",
    "password": "",
    "database": "forex"
}
```

**Acceptance Criteria**:
- Configuration is saved as valid JSON
- Existing configuration is loaded correctly
- Custom file paths work as expected
- Errors are handled without crashes

---

### 2.3 Input Validation (FR-003)
**Priority**: HIGH

**Description**: The tool must validate all user inputs to ensure valid configuration.

**Requirements**:
- FR-003.1: Validate host is not empty
- FR-003.2: Validate port is numeric and in range 1-65535
- FR-003.3: Re-prompt on invalid input
- FR-003.4: Display clear error messages for invalid inputs
- FR-003.5: Accept valid IP addresses and hostnames
- FR-003.6: Allow empty password (some servers allow this)

**Validation Rules**:
- **Host**: Non-empty string, can be IP or hostname
- **Port**: Integer between 1 and 65535
- **Username**: Any non-empty string
- **Password**: Any string (including empty)
- **Database**: Any non-empty string

**Acceptance Criteria**:
- Invalid inputs are rejected with clear messages
- Valid inputs are accepted without errors
- User can retry after validation failure

---

### 2.4 Connection Testing (FR-004)
**Priority**: HIGH

**Description**: The tool must test database connectivity with configured parameters.

**Requirements**:
- FR-004.1: Test connection after configuration by default
- FR-004.2: Support `--no-test` flag to skip testing
- FR-004.3: Support `--test-only` flag to test existing configuration
- FR-004.4: Query ClickHouse version on successful connection
- FR-004.5: Check if configured database exists
- FR-004.6: Display connection details on success
- FR-004.7: Display helpful error messages on failure
- FR-004.8: Suggest troubleshooting steps on connection failure
- FR-004.9: Handle missing `clickhouse-connect` library gracefully

**Success Indicators**:
- ClickHouse server version
- Host and port confirmed
- Database existence status
- Green checkmark visual indicator

**Failure Indicators**:
- Clear error message
- Troubleshooting checklist
- Red X visual indicator

**Acceptance Criteria**:
- Connection success is clearly indicated
- Connection failures provide actionable feedback
- Tool works even if driver not installed (warns user)

---

### 2.5 Logging (FR-005)
**Priority**: MEDIUM

**Description**: The tool must log all configuration activities to files in the logs directory.

**Requirements**:
- FR-005.1: Create logs directory if it doesn't exist
- FR-005.2: Generate timestamped log files
- FR-005.3: Log file format: `clickhouse_config_YYYYMMDD_HHMMSS.log`
- FR-005.4: Log to both file and console
- FR-005.5: Include timestamp in each log entry
- FR-005.6: Support log levels: INFO, WARNING, ERROR, SUCCESS
- FR-005.7: Use UTF-8 encoding for log files
- FR-005.8: Display log file path at completion

**Log Entry Format**:
```
[2025-10-06 14:30:15] [INFO] Host set to: localhost
[2025-10-06 14:30:16] [SUCCESS] Configuration saved to clickhouse_config.json
```

**Acceptance Criteria**:
- Log files are created in logs/ directory
- All activities are logged with timestamps
- Log levels are correctly indicated
- Logs are readable and informative

---

### 2.6 Security (FR-006)
**Priority**: HIGH

**Description**: The tool must handle sensitive information securely.

**Requirements**:
- FR-006.1: Hide password input during entry (use `getpass`)
- FR-006.2: Mask password in configuration summary display
- FR-006.3: Store password in plain text in config file (user responsible for file permissions)
- FR-006.4: Warn user about password storage in documentation
- FR-006.5: Support empty password for development environments
- FR-006.6: Allow using existing password without re-entering

**Password Display Rules**:
- **Input**: Hidden (no characters shown)
- **Summary**: Masked with asterisks (`****`)
- **Config File**: Plain text (user's responsibility to secure file)

**Acceptance Criteria**:
- Password is never displayed during input
- Password is masked in console output
- User is aware of security considerations

---

### 2.7 Command-Line Interface (FR-007)
**Priority**: MEDIUM

**Description**: The tool must support flexible command-line usage.

**Requirements**:
- FR-007.1: Support `--config` flag for custom config file path
- FR-007.2: Support `--no-test` flag to skip connection testing
- FR-007.3: Support `--test-only` flag to test without configuring
- FR-007.4: Support `--log-dir` flag for custom log directory
- FR-007.5: Display help with `-h` or `--help`
- FR-007.6: Show usage examples in help text
- FR-007.7: Exit with code 0 on success, 1 on failure
- FR-007.8: Handle Ctrl+C gracefully

**Command Examples**:
```bash
# Interactive configuration with testing
python clickhouse_configurator.py

# Configure without testing
python clickhouse_configurator.py --no-test

# Test existing configuration
python clickhouse_configurator.py --test-only

# Custom config file
python clickhouse_configurator.py --config custom.json
```

**Acceptance Criteria**:
- All flags work as documented
- Help text is clear and complete
- Exit codes are correct
- Keyboard interrupt is handled gracefully

---

## 3. Non-Functional Requirements

### 3.1 Usability (NFR-001)
- Interactive prompts must be clear and self-explanatory
- Error messages must be actionable
- Default values must simplify configuration
- Visual indicators (✅ ❌ ⚠️) must enhance readability

### 3.2 Reliability (NFR-002)
- Tool must handle all error conditions without crashing
- Corrupted config files must not cause failures
- Missing dependencies must be handled gracefully
- File system errors must be caught and reported

### 3.3 Performance (NFR-003)
- Configuration should complete in < 5 seconds (excluding user input time)
- Connection test should timeout after 30 seconds
- File operations should be atomic to prevent corruption

### 3.4 Maintainability (NFR-004)
- Code must follow PEP 8 style guidelines
- Functions must have clear docstrings
- Classes must be well-documented
- Test coverage must exceed 80%

### 3.5 Compatibility (NFR-005)
- Support Python 3.8+
- Work on Windows, Linux, and macOS
- Handle different terminal encodings
- Work with ClickHouse 20.x and later

### 3.6 Documentation (NFR-006)
- Comprehensive inline code documentation
- Complete requirements document
- Detailed design document
- User manual with examples
- Main README with quick start

---

## 4. Use Cases

### 4.1 First-Time Configuration
**Actor**: System Administrator  
**Preconditions**: Fresh installation, no config file exists  
**Flow**:
1. User runs `python clickhouse_configurator.py`
2. Tool displays wizard introduction
3. User enters host, port, username, password, database
4. Tool validates each input
5. Tool displays configuration summary
6. User confirms to save
7. Tool saves configuration to `clickhouse_config.json`
8. Tool tests connection
9. Tool displays success message and log location

**Postconditions**: Valid configuration file exists, connection confirmed

---

### 4.2 Update Existing Configuration
**Actor**: System Administrator  
**Preconditions**: Configuration file exists  
**Flow**:
1. User runs `python clickhouse_configurator.py`
2. Tool loads existing configuration
3. Tool displays current values as defaults
4. User updates desired fields (presses Enter to keep defaults)
5. User confirms changes
6. Tool saves updated configuration
7. Tool tests new connection
8. Tool reports results

**Postconditions**: Configuration updated, new connection validated

---

### 4.3 Test Existing Configuration
**Actor**: System Administrator  
**Preconditions**: Configuration file exists  
**Flow**:
1. User runs `python clickhouse_configurator.py --test-only`
2. Tool loads existing configuration
3. Tool displays configuration (password masked)
4. Tool attempts connection
5. Tool displays version and database status
6. Tool reports success or failure

**Postconditions**: Connection status known, no changes made

---

### 4.4 Migrate to New Server
**Actor**: System Administrator  
**Preconditions**: Existing config for old server  
**Flow**:
1. User runs `python clickhouse_configurator.py`
2. Tool shows old server settings as defaults
3. User updates host and port for new server
4. User keeps same credentials
5. Tool tests connection to new server
6. Tool confirms migration successful

**Postconditions**: Configuration points to new server

---

## 5. Dependencies

### 5.1 Required Dependencies
- **Python**: 3.8 or higher
- **Standard Library**: json, os, sys, argparse, datetime, getpass, pathlib

### 5.2 Optional Dependencies
- **clickhouse-connect**: For connection testing (gracefully degraded if missing)

---

## 6. Constraints

### 6.1 Technical Constraints
- Must work in console/terminal environment only
- Cannot use GUI libraries
- Must be single-file for easy deployment
- Must not require compilation

### 6.2 Business Constraints
- Must replace `view_clickhouse_tables.py` functionality
- Must integrate with existing Forex data pipeline
- Must use same configuration format as other tools

---

## 7. Future Enhancements

### 7.1 Potential Features (Out of Scope for v1.0)
- Encrypted password storage
- Multiple server profiles
- Configuration backup and restore
- Auto-discovery of ClickHouse servers
- SSH tunnel support
- Configuration validation against schema
- Import/export of configurations
- Web-based configuration UI

---

## 8. Success Metrics

### 8.1 Completion Criteria
- ✅ All critical (CRITICAL, HIGH) requirements implemented
- ✅ Test coverage > 80%
- ✅ All use cases validated
- ✅ Documentation complete
- ✅ Zero critical bugs

### 8.2 Quality Metrics
- Configuration success rate > 95%
- Connection test accuracy = 100%
- User error rate < 5%
- Average configuration time < 2 minutes

---

## 9. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-06 | Dev Team | Initial requirements document |

---

## 10. Approval

This requirements document defines the scope and specifications for the ClickHouse Configurator v1.0.0.

**Status**: APPROVED  
**Date**: 2025-10-06
