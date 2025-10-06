"""
Unit Tests for ClickHouse Configurator
======================================
Comprehensive test suite for the ClickHouse database configuration tool.

Test Coverage:
- Configuration validation
- File I/O operations
- Connection testing
- Error handling
- Interactive input simulation

Author: Forex Data Management System
Version: 1.0.0
Created: 2025-10-06
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from clickhouse_configurator import ClickHouseConfigurator


class TestClickHouseConfigurator(unittest.TestCase):
    """Test suite for ClickHouseConfigurator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, 'test_config.json')
        self.log_dir = os.path.join(self.test_dir, 'logs')
        
        # Create configurator instance
        self.configurator = ClickHouseConfigurator(
            config_file=self.config_file,
            log_dir=self.log_dir
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test configurator initialization."""
        self.assertEqual(self.configurator.config_file, self.config_file)
        self.assertTrue(os.path.exists(self.log_dir))
        self.assertIsNotNone(self.configurator.log_file)
    
    def test_validate_host_valid(self):
        """Test host validation with valid inputs."""
        valid_hosts = ['localhost', '127.0.0.1', 'db.example.com', '192.168.1.100']
        for host in valid_hosts:
            with self.subTest(host=host):
                self.assertTrue(self.configurator.validate_host(host))
    
    def test_validate_host_invalid(self):
        """Test host validation with invalid inputs."""
        invalid_hosts = ['', '   ', None]
        for host in invalid_hosts:
            with self.subTest(host=host):
                if host is not None:
                    self.assertFalse(self.configurator.validate_host(host))
    
    def test_validate_port_valid(self):
        """Test port validation with valid inputs."""
        valid_ports = [8123, 9000, 80, 443, 65535, '8123']
        for port in valid_ports:
            with self.subTest(port=port):
                self.assertTrue(self.configurator.validate_port(port))
    
    def test_validate_port_invalid(self):
        """Test port validation with invalid inputs."""
        invalid_ports = [0, -1, 65536, 'abc', '', 99999]
        for port in invalid_ports:
            with self.subTest(port=port):
                self.assertFalse(self.configurator.validate_port(port))
    
    def test_save_config(self):
        """Test configuration saving."""
        config = {
            'host': '192.168.2.168',
            'port': 9000,
            'http_port': 8123,
            'interserver_http_port': 9009,
            'user': 'default',
            'password': 'secret',
            'database': 'forex'
        }
        
        # Save config
        result = self.configurator.save_config(config)
        self.assertTrue(result)
        
        # Verify file exists
        self.assertTrue(os.path.exists(self.config_file))
        
        # Verify content
        with open(self.config_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        self.assertEqual(loaded, config)
    
    def test_load_existing_config(self):
        """Test loading existing configuration."""
        config = {
            'host': '192.168.1.100',
            'port': 9000,
            'http_port': 8123,
            'interserver_http_port': 9009,
            'user': 'admin',
            'password': 'password123',
            'database': 'test_db'
        }
        
        # Save config first
        self.configurator.save_config(config)
        
        # Load and verify
        loaded = self.configurator.load_existing_config()
        self.assertEqual(loaded, config)
    
    def test_load_config_nonexistent(self):
        """Test loading when config file doesn't exist."""
        loaded = self.configurator.load_existing_config()
        self.assertEqual(loaded, self.configurator.DEFAULT_CONFIG)
    
    def test_load_config_corrupted(self):
        """Test loading corrupted config file."""
        # Create corrupted file
        with open(self.config_file, 'w') as f:
            f.write("not valid json {{{")
        
        # Should return default config
        loaded = self.configurator.load_existing_config()
        self.assertEqual(loaded, self.configurator.DEFAULT_CONFIG)
    
    def test_logging(self):
        """Test logging functionality."""
        test_message = "Test log message"
        self.configurator.log(test_message, 'INFO')
        
        # Verify log file exists
        self.assertTrue(os.path.exists(self.configurator.log_file))
        
        # Verify log content
        with open(self.configurator.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn(test_message, content)
        self.assertIn('[INFO]', content)
    
    def test_display_config(self):
        """Test configuration display."""
        config = {
            'host': '192.168.2.168',
            'port': 9000,
            'http_port': 8123,
            'interserver_http_port': 9009,
            'user': 'default',
            'password': 'secret123',
            'database': 'forex'
        }
        
        # Should not raise exception
        with patch('builtins.print') as mock_print:
            self.configurator.display_config(config)
            # Verify print was called
            self.assertTrue(mock_print.called)
    
    @patch('clickhouse_configurator.CLICKHOUSE_AVAILABLE', False)
    def test_connection_no_driver(self):
        """Test connection when driver not available."""
        config = {
            'host': '192.168.2.168',
            'port': 9000,
            'http_port': 8123,
            'user': 'default',
            'password': 'default'
        }
        result = self.configurator.test_connection(config)
        self.assertFalse(result)
    
    @patch('clickhouse_configurator.CLICKHOUSE_AVAILABLE', True)
    @patch('clickhouse_configurator.clickhouse_connect.get_client')
    def test_connection_success(self, mock_get_client):
        """Test successful connection."""
        # Mock successful connection
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.first_row = ['22.8.1.2']
        mock_result.row_count = 1
        mock_client.query.return_value = mock_result
        mock_get_client.return_value = mock_client
        
        config = {
            'host': '192.168.2.168',
            'port': 9000,
            'http_port': 8123,
            'interserver_http_port': 9009,
            'user': 'default',
            'password': 'default',
            'database': 'forex'
        }
        
        result = self.configurator.test_connection(config)
        self.assertTrue(result)
        mock_get_client.assert_called_once()
        mock_client.close.assert_called_once()
    
    @patch('clickhouse_configurator.CLICKHOUSE_AVAILABLE', True)
    @patch('clickhouse_configurator.clickhouse_connect.get_client')
    def test_connection_failure(self, mock_get_client):
        """Test failed connection."""
        # Mock connection failure
        mock_get_client.side_effect = Exception("Connection refused")
        
        config = {
            'host': 'invalid.host',
            'port': 9000,
            'http_port': 9999,
            'user': 'wrong',
            'password': 'wrong',
            'database': 'forex'
        }
        
        result = self.configurator.test_connection(config)
        self.assertFalse(result)
    
    @patch('clickhouse_configurator.getpass')
    @patch('builtins.input')
    def test_interactive_configure(self, mock_input, mock_getpass):
        """Test interactive configuration."""
        # Mock user inputs
        mock_input.side_effect = [
            '192.168.2.168',  # host
            '9000',          # port
            '8123',          # http_port
            '9009',          # interserver_http_port
            'testuser',      # username
            'testdb'         # database
        ]
        mock_getpass.return_value = 'testpass'
        
        config = self.configurator.interactive_configure()
        
        self.assertEqual(config['host'], '192.168.2.168')
        self.assertEqual(config['port'], 9000)
        self.assertEqual(config['http_port'], 8123)
        self.assertEqual(config['interserver_http_port'], 9009)
        self.assertEqual(config['user'], 'testuser')
        self.assertEqual(config['password'], 'testpass')
        self.assertEqual(config['database'], 'testdb')
    
    @patch('clickhouse_configurator.getpass')
    @patch('builtins.input')
    def test_interactive_configure_defaults(self, mock_input, mock_getpass):
        """Test interactive configuration with default values."""
        # Mock empty inputs (use defaults) - 7 inputs: host, port, http_port, interserver_port, user, (use existing password prompt), database
        mock_input.side_effect = ['', '', '', '', '', 'y', '']
        mock_getpass.return_value = ''
        
        config = self.configurator.interactive_configure()
        
        # Should use default values
        self.assertEqual(config['host'], '192.168.2.168')
        self.assertEqual(config['port'], 9000)
        self.assertEqual(config['http_port'], 8123)
        self.assertEqual(config['interserver_http_port'], 9009)
        self.assertEqual(config['user'], 'default')
        self.assertEqual(config['database'], 'forex')
    
    @patch('clickhouse_configurator.getpass')
    @patch('builtins.input')
    def test_interactive_configure_invalid_port_retry(self, mock_input, mock_getpass):
        """Test port validation retry in interactive mode."""
        # Mock invalid then valid port - 8 inputs (invalid port adds one more, plus use existing password confirmation)
        mock_input.side_effect = [
            '192.168.2.168', # host
            'invalid',       # port (invalid)
            '9000',         # port (valid)
            '8123',         # http_port
            '9009',         # interserver_http_port
            'default',      # username
            'y',            # use existing password
            'forex'         # database
        ]
        mock_getpass.return_value = ''
        
        config = self.configurator.interactive_configure()
        self.assertEqual(config['port'], 9000)
    
    def test_default_config_values(self):
        """Test default configuration values."""
        defaults = self.configurator.DEFAULT_CONFIG
        self.assertEqual(defaults['host'], '192.168.2.168')
        self.assertEqual(defaults['port'], 9000)
        self.assertEqual(defaults['http_port'], 8123)
        self.assertEqual(defaults['interserver_http_port'], 9009)
        self.assertEqual(defaults['user'], 'default')
        self.assertEqual(defaults['password'], 'default')
        self.assertEqual(defaults['database'], 'forex')


class TestConfiguratorIntegration(unittest.TestCase):
    """Integration tests for full configuration workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, 'test_config.json')
        self.log_dir = os.path.join(self.test_dir, 'logs')
        
        self.configurator = ClickHouseConfigurator(
            config_file=self.config_file,
            log_dir=self.log_dir
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('clickhouse_configurator.CLICKHOUSE_AVAILABLE', False)
    @patch('clickhouse_configurator.getpass')
    @patch('builtins.input')
    def test_full_workflow_no_test(self, mock_input, mock_getpass):
        """Test complete configuration workflow without connection test."""
        # Mock user inputs
        mock_input.side_effect = [
            '192.168.1.100',  # host
            '9000',           # port
            '8123',           # http_port
            '9009',           # interserver_http_port
            'admin',          # username
            'production',     # database
            'y'               # confirm save
        ]
        mock_getpass.return_value = 'securepass'
        
        # Run configuration
        result = self.configurator.run(auto_test=False)
        
        # Verify success
        self.assertTrue(result)
        
        # Verify config file created
        self.assertTrue(os.path.exists(self.config_file))
        
        # Verify log file created
        log_files = list(Path(self.log_dir).glob('*.log'))
        self.assertEqual(len(log_files), 1)
        
        # Verify config content
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        self.assertEqual(config['host'], '192.168.1.100')
        self.assertEqual(config['port'], 9000)
        self.assertEqual(config['http_port'], 8123)
        self.assertEqual(config['interserver_http_port'], 9009)
        self.assertEqual(config['user'], 'admin')
        self.assertEqual(config['password'], 'securepass')
        self.assertEqual(config['database'], 'production')


def run_tests():
    """Run all tests and display results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestClickHouseConfigurator))
    suite.addTests(loader.loadTestsFromTestCase(TestConfiguratorIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
