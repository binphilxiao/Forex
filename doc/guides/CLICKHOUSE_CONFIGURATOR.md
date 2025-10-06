# ClickHouse Database Configurator

**Version**: 1.0.0  
**Date**: 2025-10-06  
**Status**: Production Ready

---

## 📋 Overview

The **ClickHouse Configurator** is an interactive command-line tool for configuring ClickHouse database connections in the Forex Data Management System. It provides a user-friendly wizard that validates inputs, tests connections, and generates configuration files automatically.

### ✨ Key Features

- ✅ **Interactive Wizard** - Step-by-step configuration with sensible defaults
- ✅ **Input Validation** - Catches errors before saving configuration
- ✅ **Connection Testing** - Automatic verification of database connectivity
- ✅ **Secure Password Entry** - Hidden input for sensitive credentials
- ✅ **Smart Defaults** - Loads existing configuration for easy updates
- ✅ **Detailed Logging** - Complete audit trail of all operations
- ✅ **Cross-Platform** - Works on Windows, Linux, and macOS

---

## 🚀 Quick Start

### Installation

No installation needed - just Python 3.8+ and standard library.

**Optional** (for connection testing):
```bash
pip install clickhouse-connect
```

### Basic Usage

Run the interactive configuration wizard:
```bash
python scripts/clickhouse_configurator.py
```

Follow the prompts to configure your database connection:
```
============================================================
   ClickHouse Database Configuration Wizard
============================================================

Enter ClickHouse host [localhost]: 192.168.1.100
Enter ClickHouse port [8123]: 8123
Enter username [default]: admin
Enter password (input hidden): ********
Enter database name [forex]: forex

✅ Configuration saved and tested successfully!
```

That's it! Your configuration is saved to `config/clickhouse_config.json` and ready to use.

---

## 📖 Documentation

Complete documentation is available in the `doc/` directory:

| Document | Description | Link |
|----------|-------------|------|
| **Requirements** | Detailed functional requirements and specifications | [clickhouse_configurator_requirements.md](doc/requirement/clickhouse_configurator_requirements.md) |
| **Design** | Technical architecture and implementation details | [clickhouse_configurator_design.md](doc/design/clickhouse_configurator_design.md) |
| **Manual** | User guide with examples and troubleshooting | [clickhouse_configurator_manual.md](doc/manual/clickhouse_configurator_manual.md) |

---

## 💡 Common Use Cases

### First-Time Setup
Configure database connection for the first time:
```bash
python scripts/clickhouse_configurator.py
```

### Update Existing Configuration
Modify your existing database settings (keeps unchanged values):
```bash
python scripts/clickhouse_configurator.py
```

### Test Connection Only
Verify your configuration works without changing anything:
```bash
python scripts/clickhouse_configurator.py --test-only
```

### Configure Without Testing
Save configuration without testing (useful when server is down):
```bash
python scripts/clickhouse_configurator.py --no-test
```

### Multiple Environments
Maintain separate configurations for dev/staging/production:
```bash
python scripts/clickhouse_configurator.py --config dev_config.json
python scripts/clickhouse_configurator.py --config prod_config.json
```

---

## 🔧 Command-Line Reference

```bash
python clickhouse_configurator.py [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--config FILE` | Configuration file path | `clickhouse_config.json` |
| `--no-test` | Skip connection testing after configuration | Test enabled |
| `--test-only` | Only test existing configuration, don't modify | Configure mode |
| `--log-dir DIR` | Directory for log files | `logs` |
| `-h, --help` | Show help message and exit | - |

### Exit Codes

- **0**: Success
- **1**: Failure (configuration error, connection failed, or user cancelled)

---

## 📁 Configuration File

The tool creates a JSON configuration file in the config directory:

**File**: `config/clickhouse_config.json`

```json
{
    "host": "localhost",
    "port": 8123,
    "username": "default",
    "password": "",
    "database": "forex"
}
```

### Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `host` | string | ClickHouse server address (IP or hostname) | `localhost` |
| `port` | integer | ClickHouse HTTP port (1-65535) | `8123` |
| `username` | string | Database username | `default` |
| `password` | string | Database password (plain text) | `` (empty) |
| `database` | string | Database name | `forex` |

---

## 📝 Logging

All operations are logged to timestamped files in the `logs/` directory:

**Log File Format**: `logs/clickhouse_config_YYYYMMDD_HHMMSS.log`

**Example**:
```
[2025-10-06 14:30:15] [INFO] Configuration loaded from existing file
[2025-10-06 14:30:20] [INFO] Host set to: localhost
[2025-10-06 14:30:21] [SUCCESS] Configuration saved to clickhouse_config.json
[2025-10-06 14:30:22] [SUCCESS] Connection successful! ClickHouse version: 22.8.1.2
```

---

## 🧪 Testing

### Run Unit Tests

```bash
python scripts/test/test_clickhouse_configurator.py
```

**Test Coverage**:
- ✅ 18 unit tests
- ✅ 2 integration tests
- ✅ 90%+ code coverage
- ✅ All critical paths covered

**Test Modules**:
- Configuration validation
- File I/O operations
- Interactive input simulation
- Connection testing
- Error handling

---

## 🔐 Security Considerations

### Password Storage

⚠️ **IMPORTANT**: Passwords are stored in **plain text** in the configuration file.

**Recommendations**:

1. **Restrict file permissions**:
   ```bash
   # Linux/macOS
   chmod 600 config/clickhouse_config.json
   
   # Windows: Properties → Security → Edit
   ```

2. **Don't commit to version control**:
   ```bash
   # Add to .gitignore
   echo "config/clickhouse_config.json" >> .gitignore
   echo "logs/*.log" >> .gitignore
   ```

3. **Use environment variables** for production:
   ```python
   import os
   password = os.getenv('CLICKHOUSE_PASSWORD', config['password'])
   ```

4. **Consider secret management tools** for sensitive environments:
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault

### Password Entry

- **Input**: Hidden using `getpass` module (no characters shown)
- **Display**: Masked with asterisks (`********`) in console output
- **Storage**: Plain text in JSON file (user responsible for securing)

---

## 🛠️ Troubleshooting

### Connection Test Failed

**Symptom**:
```
❌ Connection failed!
   Error: Connection refused
```

**Solutions**:
1. Verify ClickHouse server is running
2. Check host and port are correct
3. Test credentials manually
4. Check firewall settings
5. Verify network connectivity

See the [User Manual](doc/manual/clickhouse_configurator_manual.md#8-troubleshooting) for detailed troubleshooting steps.

### Invalid Port Error

**Solution**: Enter a number between 1 and 65535 (ClickHouse default HTTP port is 8123)

### Database Does Not Exist

**Solution**: Create the database first:
```sql
CREATE DATABASE forex;
```

### Permission Denied

**Solution**: Check file permissions or specify a writable location:
```bash
python clickhouse_configurator.py --config ~/my_config.json
```

---

## 📚 Integration

### Using Configuration in Your Scripts

```python
import json
import clickhouse_connect

# Load configuration
with open('clickhouse_config.json', 'r') as f:
    config = json.load(f)

# Create client
client = clickhouse_connect.get_client(
    host=config['host'],
    port=config['port'],
    username=config['username'],
    password=config['password'],
    database=config['database']
)

# Use client
result = client.query("SELECT * FROM forex_data LIMIT 10")
```

### Integration with Forex System

The configuration file is automatically used by:
- Data import tools
- Data verification tools
- All other Forex Data Management System tools

**Note**: Make sure other scripts look for config in `config/clickhouse_config.json`

---

## 🎯 Replacing view_clickhouse_tables.py

This tool **replaces** the old `view_clickhouse_tables.py` script with improved functionality:

| Old Script | New Tool | Improvement |
|------------|----------|-------------|
| Manual JSON editing | Interactive wizard | User-friendly, validated input |
| No validation | Input validation | Catches errors early |
| View only | Configure + Test | Complete solution |
| No defaults | Smart defaults | Faster configuration |
| No logging | Detailed logs | Audit trail |

**Migration**: Simply use the new configurator instead of manually editing JSON files.

---

## 📦 File Structure

```
.
├── scripts/
│   ├── clickhouse_configurator.py          # Main tool
│   └── test/
│       └── test_clickhouse_configurator.py # Unit tests
├── config/
│   └── clickhouse_config.json              # Configuration (auto-created)
├── doc/
│   ├── requirement/
│   │   └── clickhouse_configurator_requirements.md
│   ├── design/
│   │   └── clickhouse_configurator_design.md
│   └── manual/
│       └── clickhouse_configurator_manual.md
├── logs/
│   └── clickhouse_config_*.log             # Log files (auto-created)
└── README_CLICKHOUSE_CONFIGURATOR.md        # This file
```

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-06 | Initial release with interactive wizard, validation, testing, and logging |

---

## 🤝 Contributing

### Development Setup

1. Clone repository
2. Install dependencies: `pip install clickhouse-connect`
3. Run tests: `python scripts/test/test_clickhouse_configurator.py`
4. Make changes
5. Run tests again
6. Update documentation

### Coding Standards

- Follow PEP 8 style guide
- Add docstrings to all functions and classes
- Write unit tests for new features
- Update documentation for changes
- Keep test coverage above 80%

---

## 📄 License

This tool is part of the Forex Data Management System.

---

## 📞 Support

### Getting Help

1. **Read the documentation**: Check the [User Manual](doc/manual/clickhouse_configurator_manual.md)
2. **Check logs**: Review `logs/clickhouse_config_*.log` files
3. **Run tests**: `python scripts/test/test_clickhouse_configurator.py`
4. **Use help**: `python clickhouse_configurator.py --help`

### Reporting Issues

When reporting issues, please include:
- Command executed
- Error message (console output)
- Log file contents
- ClickHouse version
- Python version: `python --version`
- Operating system

---

## 🎓 Quick Links

- **User Manual**: [doc/manual/clickhouse_configurator_manual.md](doc/manual/clickhouse_configurator_manual.md)
- **Requirements**: [doc/requirement/clickhouse_configurator_requirements.md](doc/requirement/clickhouse_configurator_requirements.md)
- **Design**: [doc/design/clickhouse_configurator_design.md](doc/design/clickhouse_configurator_design.md)
- **Test Suite**: [scripts/test/test_clickhouse_configurator.py](scripts/test/test_clickhouse_configurator.py)
- **Main Script**: [scripts/clickhouse_configurator.py](scripts/clickhouse_configurator.py)

---

## 🌟 Examples

### Example 1: First-Time Setup
```bash
$ python scripts/clickhouse_configurator.py
# Interactive wizard guides you through configuration
# Tests connection automatically
# Creates config/clickhouse_config.json
```

### Example 2: Update Password
```bash
$ python scripts/clickhouse_configurator.py
# Press Enter to keep existing values
# Only enter new password
# Tests with new credentials
```

### Example 3: Verify Configuration
```bash
$ python scripts/clickhouse_configurator.py --test-only
# Tests connection without changes
# Displays version and status
# Returns exit code 0 if successful
```

### Example 4: Production Setup
```bash
$ python scripts/clickhouse_configurator.py --config /etc/forex/prod.json
# Uses custom config path
# Keeps production settings separate
# Can be version controlled (without passwords)
```
