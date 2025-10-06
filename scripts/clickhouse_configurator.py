"""
ClickHouse Database Configurator
=================================
Interactive command-line tool for configuring ClickHouse database connection.

Features:
- Interactive configuration via command-line prompts
- Validation of connection parameters
- Automatic connection testing
- Secure password handling
- JSON configuration file generation
- Detailed logging to logs/ folder

Author: Forex Data Management System
Version: 1.0.0
Created: 2025-10-06
"""

import json
import os
import sys
import argparse
from datetime import datetime
from getpass import getpass
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    import clickhouse_connect
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False
    print("Warning: clickhouse-connect not installed. Connection testing will be skipped.")


class ClickHouseConfigurator:
    """
    ClickHouse database configuration manager.
    
    Handles interactive configuration, validation, and testing of 
    ClickHouse database connections.
    """
    
    DEFAULT_CONFIG = {
        'host': '192.168.2.168',
        'port': 9000,
        'http_port': 8123,
        'interserver_http_port': 9009,
        'user': 'default',
        'password': 'default',
        'database': 'forex'
    }
    
    def __init__(self, config_file='clickhouse_config.json', log_dir='logs'):
        """
        Initialize the configurator.
        
        Args:
            config_file (str): Path to configuration file
            log_dir (str): Directory for log files
        """
        self.config_file = config_file
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.log_file = self.log_dir / f"clickhouse_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
    def log(self, message, level='INFO'):
        """
        Write log message to file and console.
        
        Args:
            message (str): Log message
            level (str): Log level (INFO, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # Write to file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
        
        # Print to console
        if level == 'ERROR':
            print(f"❌ {message}")
        elif level == 'WARNING':
            print(f"⚠️  {message}")
        elif level == 'SUCCESS':
            print(f"✅ {message}")
        else:
            print(f"ℹ️  {message}")
    
    def load_existing_config(self):
        """
        Load existing configuration file if it exists.
        
        Returns:
            dict: Existing configuration or default values
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.log(f"Loaded existing configuration from {self.config_file}")
                return config
            except Exception as e:
                self.log(f"Failed to load existing config: {e}", 'WARNING')
                return self.DEFAULT_CONFIG.copy()
        else:
            self.log("No existing configuration found, using defaults")
            return self.DEFAULT_CONFIG.copy()
    
    def validate_host(self, host):
        """
        Validate host address.
        
        Args:
            host (str): Host address
            
        Returns:
            bool: True if valid
        """
        if not host or not host.strip():
            return False
        # Basic validation - could be IP or hostname
        return True
    
    def validate_port(self, port):
        """
        Validate port number.
        
        Args:
            port (int): Port number
            
        Returns:
            bool: True if valid
        """
        try:
            port_int = int(port)
            return 1 <= port_int <= 65535
        except ValueError:
            return False
    
    def interactive_configure(self):
        """
        Run interactive configuration session.
        
        Returns:
            dict: Configuration dictionary
        """
        print("\n" + "="*60)
        print("   ClickHouse Database Configuration Wizard")
        print("="*60 + "\n")
        
        # Load existing config for defaults
        existing_config = self.load_existing_config()
        
        config = {}
        
        # Host configuration
        while True:
            default_host = existing_config.get('host', '192.168.2.168')
            host = input(f"Enter ClickHouse host IP [{default_host}]: ").strip()
            if not host:
                host = default_host
            
            if self.validate_host(host):
                config['host'] = host
                self.log(f"Host set to: {host}")
                break
            else:
                print("❌ Invalid host address. Please try again.")
        
        # Client port configuration (native protocol)
        while True:
            default_port = existing_config.get('port', 9000)
            port_input = input(f"Enter ClickHouse client port (native) [{default_port}]: ").strip()
            if not port_input:
                port = default_port
            else:
                port = port_input
            
            if self.validate_port(port):
                config['port'] = int(port)
                self.log(f"Client port set to: {port}")
                break
            else:
                print("❌ Invalid port number (must be 1-65535). Please try again.")
        
        # HTTP port configuration
        while True:
            default_http_port = existing_config.get('http_port', 8123)
            http_port_input = input(f"Enter ClickHouse HTTP port [{default_http_port}]: ").strip()
            if not http_port_input:
                http_port = default_http_port
            else:
                http_port = http_port_input
            
            if self.validate_port(http_port):
                config['http_port'] = int(http_port)
                self.log(f"HTTP port set to: {http_port}")
                break
            else:
                print("❌ Invalid port number (must be 1-65535). Please try again.")
        
        # Interserver HTTP port configuration
        while True:
            default_interserver_port = existing_config.get('interserver_http_port', 9009)
            interserver_port_input = input(f"Enter ClickHouse interserver HTTP port [{default_interserver_port}]: ").strip()
            if not interserver_port_input:
                interserver_port = default_interserver_port
            else:
                interserver_port = interserver_port_input
            
            if self.validate_port(interserver_port):
                config['interserver_http_port'] = int(interserver_port)
                self.log(f"Interserver HTTP port set to: {interserver_port}")
                break
            else:
                print("❌ Invalid port number (must be 1-65535). Please try again.")
        
        # Username configuration
        default_user = existing_config.get('user', 'default')
        username = input(f"Enter username [{default_user}]: ").strip()
        if not username:
            username = default_user
        config['user'] = username
        self.log(f"Username set to: {username}")
        
        # Password configuration
        print("\nEnter password (input hidden): ")
        password = getpass("Password: ")
        if not password:
            default_pass = existing_config.get('password', 'default')
            if default_pass:
                use_existing = input(f"Use existing/default password? [Y/n]: ").strip().lower()
                if use_existing != 'n':
                    password = default_pass
                    self.log("Using existing password")
                else:
                    password = 'default'
                    self.log("Password set to default")
            else:
                password = 'default'
                self.log("Password set to default")
        else:
            self.log("New password configured")
        config['password'] = password
        
        # Database name
        default_db = existing_config.get('database', 'forex')
        database = input(f"Enter database name [{default_db}]: ").strip()
        if not database:
            database = default_db
        config['database'] = database
        self.log(f"Database set to: {database}")
        
        return config
    
    def save_config(self, config):
        """
        Save configuration to JSON file.
        
        Args:
            config (dict): Configuration dictionary
            
        Returns:
            bool: True if successful
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self.log(f"Configuration saved to {self.config_file}", 'SUCCESS')
            return True
        except Exception as e:
            self.log(f"Failed to save configuration: {e}", 'ERROR')
            return False
    
    def test_connection(self, config):
        """
        Test database connection with given configuration.
        
        Args:
            config (dict): Configuration dictionary
            
        Returns:
            bool: True if connection successful
        """
        if not CLICKHOUSE_AVAILABLE:
            self.log("Cannot test connection: clickhouse-connect not installed", 'WARNING')
            print("\n⚠️  To test connection, install: pip install clickhouse-connect")
            return False
        
        print("\n🔍 Testing database connection...")
        self.log("Testing database connection...")
        
        try:
            # Attempt to connect using HTTP port
            client = clickhouse_connect.get_client(
                host=config['host'],
                port=config.get('http_port', 8123),  # Use HTTP port for connection
                username=config.get('user', 'default'),
                password=config['password'],
                database=config.get('database', 'default')
            )
            
            # Test query
            result = client.query("SELECT version()")
            version = result.first_row[0] if result.row_count > 0 else "Unknown"
            
            self.log(f"Connection successful! ClickHouse version: {version}", 'SUCCESS')
            print(f"\n✅ Connection successful!")
            print(f"   ClickHouse version: {version}")
            print(f"   Host: {config['host']}")
            print(f"   Client Port (native): {config.get('port', 9000)}")
            print(f"   HTTP Port: {config.get('http_port', 8123)}")
            print(f"   Interserver Port: {config.get('interserver_http_port', 9009)}")
            print(f"   Database: {config.get('database', 'default')}")
            
            # Get database info
            try:
                db_query = f"SELECT name FROM system.databases WHERE name = '{config.get('database', 'forex')}'"
                db_result = client.query(db_query)
                if db_result.row_count > 0:
                    self.log(f"Database '{config.get('database')}' exists", 'SUCCESS')
                else:
                    self.log(f"Database '{config.get('database')}' does not exist yet", 'WARNING')
                    print(f"\n⚠️  Note: Database '{config.get('database')}' does not exist yet.")
                    print(f"   Create it with: CREATE DATABASE {config.get('database')}")
            except Exception as e:
                self.log(f"Could not check database existence: {e}", 'WARNING')
            
            client.close()
            return True
            
        except Exception as e:
            self.log(f"Connection failed: {e}", 'ERROR')
            print(f"\n❌ Connection failed!")
            print(f"   Error: {e}")
            print(f"\n   Please check:")
            print(f"   1. ClickHouse server is running")
            print(f"   2. Host ({config['host']}) and HTTP port ({config.get('http_port', 8123)}) are correct")
            print(f"   3. Username and password are valid")
            print(f"   4. Firewall allows connection on port {config.get('http_port', 8123)}")
            return False
    
    def display_config(self, config):
        """
        Display configuration summary.
        
        Args:
            config (dict): Configuration dictionary
        """
        print("\n" + "="*60)
        print("   Configuration Summary")
        print("="*60)
        print(f"  Host:                  {config['host']}")
        print(f"  Client Port (native):  {config.get('port', 9000)}")
        print(f"  HTTP Port:             {config.get('http_port', 8123)}")
        print(f"  Interserver Port:      {config.get('interserver_http_port', 9009)}")
        print(f"  Username:              {config.get('user', 'default')}")
        print(f"  Password:              {'*' * len(config.get('password', '')) if config.get('password') else '(empty)'}")
        print(f"  Database:              {config.get('database', 'default')}")
        print("="*60 + "\n")
    
    def run(self, auto_test=True):
        """
        Run the configuration wizard.
        
        Args:
            auto_test (bool): Automatically test connection after configuration
            
        Returns:
            bool: True if configuration successful
        """
        try:
            # Interactive configuration
            config = self.interactive_configure()
            
            # Display summary
            self.display_config(config)
            
            # Confirm
            confirm = input("Save this configuration? [Y/n]: ").strip().lower()
            if confirm == 'n':
                self.log("Configuration cancelled by user")
                print("\n❌ Configuration cancelled.")
                return False
            
            # Save configuration
            if not self.save_config(config):
                return False
            
            # Test connection
            if auto_test:
                success = self.test_connection(config)
                if success:
                    print(f"\n✅ Configuration complete and tested!")
                else:
                    print(f"\n⚠️  Configuration saved but connection test failed.")
                    print(f"   You can test again later or check server settings.")
            else:
                print(f"\n✅ Configuration saved successfully!")
                print(f"   Use --test flag to test connection later.")
            
            print(f"\n📝 Log saved to: {self.log_file}")
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n❌ Configuration interrupted by user.")
            self.log("Configuration interrupted by user", 'WARNING')
            return False
        except Exception as e:
            self.log(f"Unexpected error: {e}", 'ERROR')
            print(f"\n❌ Unexpected error: {e}")
            return False


def main():
    """Main entry point for the configurator."""
    parser = argparse.ArgumentParser(
        description='ClickHouse Database Configuration Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run interactive configuration wizard
  python clickhouse_configurator.py
  
  # Configure without testing connection
  python clickhouse_configurator.py --no-test
  
  # Test existing configuration
  python clickhouse_configurator.py --test-only
  
  # Specify custom config file
  python clickhouse_configurator.py --config my_config.json
        """
    )
    
    parser.add_argument('--config', type=str, default='clickhouse_config.json',
                        help='Configuration file path (default: clickhouse_config.json)')
    parser.add_argument('--no-test', action='store_true',
                        help='Skip connection testing after configuration')
    parser.add_argument('--test-only', action='store_true',
                        help='Only test existing configuration without modifying')
    parser.add_argument('--log-dir', type=str, default='logs',
                        help='Log directory (default: logs)')
    
    args = parser.parse_args()
    
    configurator = ClickHouseConfigurator(
        config_file=args.config,
        log_dir=args.log_dir
    )
    
    if args.test_only:
        # Test only mode
        print("\n🔍 Testing existing configuration...")
        config = configurator.load_existing_config()
        if config == configurator.DEFAULT_CONFIG:
            print("❌ No configuration file found!")
            print(f"   Create one with: python clickhouse_configurator.py")
            sys.exit(1)
        
        configurator.display_config(config)
        success = configurator.test_connection(config)
        sys.exit(0 if success else 1)
    else:
        # Normal configuration mode
        success = configurator.run(auto_test=not args.no_test)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
