"""
Quick Endpoint Test Script
Tests basic GET endpoints to verify API availability
Updated to use api_config.json with environment parameters
"""

import requests
import urllib3
import json
import argparse
from datetime import datetime
from pathlib import Path

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_api_config(config_path="../api_config.json", env_name="target"):
    """Load API configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config['environments'][env_name]
    except FileNotFoundError:
        print(f"Error: Configuration file not found: {config_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        return None
    except KeyError as e:
        print(f"Error: Environment '{env_name}' not found in configuration")
        return None


def test_endpoints(env_config):
    """Test API endpoints"""
    BASE_URL = env_config['base_url']
    headers = env_config.get('headers', {
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    verify_ssl = env_config.get('verify_ssl', False)
    timeout = env_config.get('timeout', 10)
    
    endpoints = [
        {"method": "GET", "path": "/api/Authors", "name": "GET All Authors", "expected_status": 200},
        {"method": "GET", "path": "/api/Authors/1", "name": "GET Author by ID", "expected_status": [200, 404]},
        {"method": "GET", "path": "/api/Books", "name": "GET All Books", "expected_status": 200},
        {"method": "GET", "path": "/api/Books/1", "name": "GET Book by ID", "expected_status": [200, 404]},
    ]

    print(f"\n{'='*70}")
    print(f"Testing Endpoints")
    print(f"{'='*70}")
    print(f"Environment: {env_config.get('description', 'N/A')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    results = []
    for ep in endpoints:
        try:
            url = f"{BASE_URL}{ep['path']}"
            
            response = requests.request(
                method=ep['method'],
                url=url,
                headers=headers,
                verify=verify_ssl,
                timeout=timeout
            )
            
            expected = ep['expected_status']
            expected_list = expected if isinstance(expected, list) else [expected]
            
            status_match = response.status_code in expected_list
            status_icon = "✓" if status_match else "!"
            status_color = "OK" if status_match else "WARN"
            
            result = {
                "name": ep['name'],
                "url": url,
                "status": response.status_code,
                "success": status_match,
                "response_time": response.elapsed.total_seconds(),
                "response_size": len(response.content)
            }
            results.append(result)
            
            print(f"[{status_icon}] {ep['name']:<25} Status: {response.status_code:<3} Time: {response.elapsed.total_seconds():.3f}s Size: {len(response.content)} bytes")
            
        except requests.exceptions.SSLError as e:
            print(f"[✗] {ep['name']:<25} SSL Error: {str(e)[:50]}")
            results.append({"name": ep['name'], "url": url, "error": "SSL Error", "success": False})
        except requests.exceptions.ConnectionError as e:
            print(f"[✗] {ep['name']:<25} Connection Error: {str(e)[:50]}")
            results.append({"name": ep['name'], "url": url, "error": "Connection Error", "success": False})
        except requests.exceptions.Timeout:
            print(f"[✗] {ep['name']:<25} Timeout Error")
            results.append({"name": ep['name'], "url": url, "error": "Timeout", "success": False})
        except Exception as e:
            print(f"[✗] {ep['name']:<25} Error: {str(e)[:50]}")
            results.append({"name": ep['name'], "url": url, "error": str(e), "success": False})

    print(f"\n{'='*70}")
    success_count = sum(1 for r in results if r.get('success', False))
    total_count = len(results)
    print(f"Summary: {success_count}/{total_count} endpoints working")
    print(f"{'='*70}\n")
    
    return results


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Quick test of API endpoints using api_config.json',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test target environment (default)
  python test_endpoints.py
  
  # Test source environment
  python test_endpoints.py --env source
  
  # Test local environment
  python test_endpoints.py --env local
  
  # Use custom config file
  python test_endpoints.py --env target --config ../custom_api_config.json
        """
    )
    
    parser.add_argument(
        '--env',
        choices=['source', 'target', 'local'],
        default='target',
        help='Environment to test (default: target)'
    )
    
    parser.add_argument(
        '--config',
        default='../api_config.json',
        help='Path to API config file (default: ../api_config.json)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    env_config = load_api_config(args.config, args.env)
    
    if not env_config:
        print("\nFailed to load configuration. Exiting.")
        return 1
    
    # Run tests
    results = test_endpoints(env_config)
    
    return 0


if __name__ == "__main__":
    exit(main())
