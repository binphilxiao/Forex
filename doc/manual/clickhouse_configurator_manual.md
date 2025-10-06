# ClickHouse Configurator - User Manual

## Document Information
- **Tool**: ClickHouse Database Configurator
- **Version**: 1.0.0
- **Date**: 2025-10-06
- **Audience**: System Administrators, Developers

---

## 1. Introduction

### 1.1 What is ClickHouse Configurator?
The ClickHouse Configurator is an interactive command-line tool that helps you configure database connections for the Forex Data Management System. It replaces manual JSON editing with a user-friendly wizard that validates your inputs and tests connections.

### 1.2 Key Features
- ✅ **Interactive wizard** - Step-by-step prompts with defaults
- ✅ **Input validation** - Catches errors before saving
- ✅ **Connection testing** - Verifies configuration works
- ✅ **Secure password entry** - Hidden input for sensitive data
- ✅ **Detailed logging** - Complete audit trail
- ✅ **Smart defaults** - Uses existing values when available

---

## 2. Quick Start

### 2.1 Basic Usage
Run the configurator interactively:
```bash
python scripts/clickhouse_configurator.py
```

Follow the prompts to enter your database connection details:
```
============================================================
   ClickHouse Database Configuration Wizard
============================================================

Enter ClickHouse host [localhost]: 192.168.1.100
Enter ClickHouse port [8123]: 8123
Enter username [default]: admin
Enter password (input hidden):
Password: ████████
Enter database name [forex]: forex

============================================================
   Configuration Summary
============================================================
  Host:     192.168.1.100
  Port:     8123
  Username: admin
  Password: ********
  Database: forex
============================================================

Save this configuration? [Y/n]: y

✅ Configuration saved to clickhouse_config.json

🔍 Testing database connection...

✅ Connection successful!
   ClickHouse version: 22.8.1.2
   Host: 192.168.1.100:8123
   Database: forex

📝 Log saved to: logs/clickhouse_config_20251006_143015.log
```

### 2.2 Using Defaults
Press **Enter** without typing to accept the default value shown in brackets:
```
Enter ClickHouse host [localhost]: [Enter]  ← Uses 'localhost'
Enter ClickHouse port [8123]: [Enter]       ← Uses '8123'
```

---

## 3. Installation

### 3.1 Prerequisites
- **Python 3.8+** required
- **clickhouse-connect** (optional, for connection testing)

### 3.2 Install Dependencies
```bash
# For connection testing (recommended)
pip install clickhouse-connect

# Or install all Forex system dependencies
pip install -r requirements.txt
```

**Note**: The tool works without `clickhouse-connect`, but connection testing will be skipped.

---

## 4. Usage Examples

### 4.1 First-Time Configuration
Configure database connection for the first time:
```bash
python scripts/clickhouse_configurator.py
```

The tool will:
1. Display wizard with default values
2. Prompt for each parameter
3. Validate your inputs
4. Save configuration to `clickhouse_config.json`
5. Test the connection
6. Create a log file in `logs/`

---

### 4.2 Update Existing Configuration
When you run the configurator again, it loads your previous settings:
```bash
python scripts/clickhouse_configurator.py
```

Example session:
```
Enter ClickHouse host [192.168.1.100]: 192.168.1.101  ← Change host
Enter ClickHouse port [8123]: [Enter]                  ← Keep same port
Enter username [admin]: [Enter]                        ← Keep same username
Enter password (input hidden):
Password: [Enter]                                       ← Keep same password
Enter database name [forex]: [Enter]                   ← Keep same database
```

---

### 4.3 Test Existing Configuration
Test connection without modifying configuration:
```bash
python scripts/clickhouse_configurator.py --test-only
```

Output:
```
🔍 Testing existing configuration...

============================================================
   Configuration Summary
============================================================
  Host:     localhost
  Port:     8123
  Username: default
  Password: ********
  Database: forex
============================================================

🔍 Testing database connection...

✅ Connection successful!
   ClickHouse version: 22.8.1.2
   Host: localhost:8123
   Database: forex
```

---

### 4.4 Configure Without Testing
Save configuration without testing connection:
```bash
python scripts/clickhouse_configurator.py --no-test
```

Useful when:
- ClickHouse server is temporarily down
- You're configuring for a remote server
- You want to test manually later

---

### 4.5 Custom Configuration File
Use a different configuration file:
```bash
python scripts/clickhouse_configurator.py --config production_config.json
```

This allows you to maintain multiple configurations for different environments.

---

### 4.6 Custom Log Directory
Specify where logs should be saved:
```bash
python scripts/clickhouse_configurator.py --log-dir /var/log/forex
```

---

## 5. Command-Line Reference

### 5.1 Synopsis
```bash
python clickhouse_configurator.py [OPTIONS]
```

### 5.2 Options
| Option | Description | Default |
|--------|-------------|---------|
| `--config FILE` | Configuration file path | `clickhouse_config.json` |
| `--no-test` | Skip connection testing | Test enabled |
| `--test-only` | Only test, don't configure | Configure mode |
| `--log-dir DIR` | Log file directory | `logs` |
| `-h, --help` | Show help message | - |

### 5.3 Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Configuration failed, connection failed, or user cancelled |

---

## 6. Configuration File

### 6.1 File Format
The configuration is saved as JSON in `clickhouse_config.json`:
```json
{
    "host": "localhost",
    "port": 8123,
    "username": "default",
    "password": "",
    "database": "forex"
}
```

### 6.2 Configuration Parameters

#### host (string)
- **Description**: ClickHouse server address
- **Examples**: `localhost`, `127.0.0.1`, `db.example.com`, `192.168.1.100`
- **Default**: `localhost`

#### port (integer)
- **Description**: ClickHouse HTTP interface port
- **Range**: 1-65535
- **Default**: `8123` (ClickHouse default HTTP port)
- **Note**: Native port is 9000, but this tool uses HTTP interface

#### username (string)
- **Description**: Database username
- **Default**: `default` (ClickHouse default user)
- **Examples**: `admin`, `readonly_user`, `data_loader`

#### password (string)
- **Description**: Database password
- **Default**: `` (empty string)
- **Security**: Stored in plain text - see Security section

#### database (string)
- **Description**: Database name to connect to
- **Default**: `forex`
- **Note**: Database must exist or be created separately

---

## 7. Log Files

### 7.1 Log Location
Logs are saved in the `logs/` directory with timestamped filenames:
```
logs/clickhouse_config_20251006_143015.log
```

### 7.2 Log Format
Each line contains timestamp, level, and message:
```
[2025-10-06 14:30:15] [INFO] Loaded existing configuration from clickhouse_config.json
[2025-10-06 14:30:20] [INFO] Host set to: localhost
[2025-10-06 14:30:21] [INFO] Port set to: 8123
[2025-10-06 14:30:22] [INFO] Username set to: default
[2025-10-06 14:30:23] [INFO] New password configured
[2025-10-06 14:30:24] [INFO] Database set to: forex
[2025-10-06 14:30:25] [SUCCESS] Configuration saved to clickhouse_config.json
[2025-10-06 14:30:26] [INFO] Testing database connection...
[2025-10-06 14:30:27] [SUCCESS] Connection successful! ClickHouse version: 22.8.1.2
```

### 7.3 Log Levels
- **INFO**: Normal operations
- **SUCCESS**: Successful operations (saved, connected)
- **WARNING**: Non-critical issues (file not found, using defaults)
- **ERROR**: Critical failures (connection failed, save failed)

---

## 8. Troubleshooting

### 8.1 Connection Test Failed

#### Symptom
```
❌ Connection failed!
   Error: Connection refused
```

#### Solutions
1. **Check ClickHouse server is running**:
   ```bash
   # Linux/macOS
   systemctl status clickhouse-server
   
   # Windows
   Check Task Manager or Services
   ```

2. **Verify host and port**:
   - Ensure host is correct (IP or hostname)
   - Default HTTP port is 8123
   - Check if ClickHouse is listening: `netstat -an | grep 8123`

3. **Test credentials**:
   ```bash
   # Try connecting manually
   curl http://localhost:8123/ --user default:password
   ```

4. **Check firewall**:
   - Allow port 8123 in firewall
   - Check network connectivity: `ping [host]`

---

### 8.2 Invalid Port Error

#### Symptom
```
❌ Invalid port number (must be 1-65535). Please try again.
```

#### Solution
- Enter a number between 1 and 65535
- Common ports: 8123 (HTTP), 9000 (Native)
- Don't include protocol (http://)

---

### 8.3 Database Does Not Exist

#### Symptom
```
⚠️  Note: Database 'forex' does not exist yet.
   Create it with: CREATE DATABASE forex
```

#### Solution
Create the database in ClickHouse:
```sql
CREATE DATABASE forex;
```

Using clickhouse-client:
```bash
clickhouse-client --query="CREATE DATABASE forex"
```

---

### 8.4 Permission Denied (File Save)

#### Symptom
```
❌ Failed to save configuration: [Errno 13] Permission denied
```

#### Solutions
1. **Check file permissions**:
   ```bash
   # Make sure you can write to current directory
   ls -la clickhouse_config.json
   ```

2. **Run with appropriate permissions**:
   ```bash
   # Windows: Run PowerShell as Administrator
   # Linux/macOS: Use sudo if needed (not recommended)
   ```

3. **Specify writable location**:
   ```bash
   python clickhouse_configurator.py --config ~/my_config.json
   ```

---

### 8.5 clickhouse-connect Not Installed

#### Symptom
```
Warning: clickhouse-connect not installed. Connection testing will be skipped.
⚠️  To test connection, install: pip install clickhouse-connect
```

#### Solution
Install the optional dependency:
```bash
pip install clickhouse-connect
```

Then re-run with `--test-only`:
```bash
python clickhouse_configurator.py --test-only
```

---

## 9. Security

### 9.1 Password Storage
⚠️ **IMPORTANT**: Passwords are stored in **plain text** in the configuration file.

**Recommendations**:
1. **File permissions**: Restrict access to configuration file
   ```bash
   # Linux/macOS
   chmod 600 clickhouse_config.json
   
   # Windows
   Right-click file → Properties → Security → Edit permissions
   ```

2. **Environment variables**: For production, consider using environment variables:
   ```python
   import os
   password = os.getenv('CLICKHOUSE_PASSWORD', config['password'])
   ```

3. **Secure storage**: For sensitive environments, use:
   - Secret management tools (Vault, AWS Secrets Manager)
   - Encrypted configuration files
   - System keyring

### 9.2 Password Input
- Passwords are **hidden** during entry (using `getpass`)
- Passwords are **masked** in console output (*****)
- Passwords appear in **plain text** in config file and logs

### 9.3 Best Practices
- Don't commit `clickhouse_config.json` to version control
- Add to `.gitignore`:
  ```
  clickhouse_config.json
  logs/*.log
  ```
- Use different credentials for development and production
- Rotate passwords regularly
- Use read-only users when possible

---

## 10. Integration

### 10.1 Using Configuration in Other Scripts
Load the configuration in your Python scripts:

```python
import json

# Load configuration
with open('clickhouse_config.json', 'r') as f:
    config = json.load(f)

# Use with clickhouse-connect
import clickhouse_connect

client = clickhouse_connect.get_client(
    host=config['host'],
    port=config['port'],
    username=config['username'],
    password=config['password'],
    database=config['database']
)

# Now use client for queries
result = client.query("SELECT * FROM forex_data LIMIT 10")
```

### 10.2 Batch Files
The configuration file is automatically used by system batch files:
- `batch_import.bat`
- `verify_consistency.bat`
- Other Forex system tools

---

## 11. Advanced Usage

### 11.1 Multiple Environments
Maintain separate configurations:
```bash
# Development
python clickhouse_configurator.py --config dev_config.json

# Staging
python clickhouse_configurator.py --config staging_config.json

# Production
python clickhouse_configurator.py --config prod_config.json
```

### 11.2 Automated Configuration
Create configuration programmatically:
```python
import json

config = {
    'host': '192.168.1.100',
    'port': 8123,
    'username': 'admin',
    'password': 'secret',
    'database': 'forex'
}

with open('clickhouse_config.json', 'w') as f:
    json.dump(config, f, indent=4)
```

Then test it:
```bash
python clickhouse_configurator.py --test-only
```

### 11.3 CI/CD Integration
Use in automated pipelines:
```bash
#!/bin/bash
# Configure database for CI environment

python clickhouse_configurator.py --config ci_config.json --no-test
# Configuration will fail if inputs invalid

# Later, test connection
if python clickhouse_configurator.py --test-only; then
    echo "Database ready"
else
    echo "Database not accessible"
    exit 1
fi
```

---

## 12. Examples

### 12.1 Example 1: Local Development Setup
```bash
$ python scripts/clickhouse_configurator.py

Enter ClickHouse host [localhost]: [Enter]
Enter ClickHouse port [8123]: [Enter]
Enter username [default]: [Enter]
Enter password (input hidden):
Password: [Enter]
Enter database name [forex]: [Enter]

Save this configuration? [Y/n]: y

✅ Configuration complete and tested!
```

### 12.2 Example 2: Remote Production Server
```bash
$ python scripts/clickhouse_configurator.py --config production.json

Enter ClickHouse host [localhost]: db.production.com
Enter ClickHouse port [8123]: 8123
Enter username [default]: prod_user
Enter password (input hidden):
Password: ████████████
Enter database name [forex]: forex_prod

Save this configuration? [Y/n]: y

✅ Connection successful!
   ClickHouse version: 23.1.1.3077
   Host: db.production.com:8123
   Database: forex_prod
```

### 12.3 Example 3: Testing Existing Setup
```bash
$ python scripts/clickhouse_configurator.py --test-only

✅ Connection successful!
   ClickHouse version: 22.8.1.2
   Host: localhost:8123
   Database: forex
```

### 12.4 Example 4: Update Only Password
```bash
$ python scripts/clickhouse_configurator.py

Enter ClickHouse host [192.168.1.100]: [Enter]  ← Keep
Enter ClickHouse port [8123]: [Enter]            ← Keep
Enter username [admin]: [Enter]                  ← Keep
Enter password (input hidden):
Password: ████████████                           ← Change only this
Enter database name [forex]: [Enter]             ← Keep

Save this configuration? [Y/n]: y
```

---

## 13. FAQ

### Q1: What if I don't remember my existing password?
**A**: You'll need to reset it in ClickHouse or check your existing config file:
```bash
cat clickhouse_config.json
```

### Q2: Can I use this with ClickHouse Cloud?
**A**: Yes! Enter your cloud instance hostname and credentials.

### Q3: Why does the tool ask for the password again?
**A**: For security, the tool doesn't display the existing password. Press Enter to keep it unchanged.

### Q4: Can I skip the wizard and edit JSON directly?
**A**: Yes, but the wizard provides validation and testing. Edit with care.

### Q5: Does this work on Windows?
**A**: Yes! Works on Windows, Linux, and macOS.

### Q6: How do I know if my configuration is correct?
**A**: Run `--test-only` mode to verify without changing anything.

### Q7: Can multiple users share one configuration file?
**A**: Yes, but be aware of security implications (shared passwords).

---

## 14. See Also

- [Requirements Document](../requirement/clickhouse_configurator_requirements.md) - Detailed specifications
- [Design Document](../design/clickhouse_configurator_design.md) - Technical architecture
- [Main README](../../README_CLICKHOUSE_CONFIGURATOR.md) - Overview and quick links
- [ClickHouse Documentation](https://clickhouse.com/docs/) - Official ClickHouse docs

---

## 15. Support

### Getting Help
1. Check this manual
2. Review log files in `logs/` directory
3. Run with `--help` flag for quick reference
4. Check the troubleshooting section

### Reporting Issues
When reporting issues, include:
- Command you ran
- Error message (from console)
- Log file contents
- ClickHouse version
- Python version: `python --version`

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-10-06  
**Tool Version**: 1.0.0
