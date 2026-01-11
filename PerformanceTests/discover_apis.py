"""
API Discovery Script
Tests all known endpoints and attempts to discover available APIs
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
        return config['environments'][env_name], config.get('endpoints', {})
    except FileNotFoundError:
        print(f"Error: Configuration file not found: {config_path}")
        print(f"Please ensure api_config.json exists at: {Path(config_path).absolute()}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        return None, None
    except KeyError as e:
        print(f"Error: Environment '{env_name}' not found in configuration")
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"Available environments: {list(config.get('environments', {}).keys())}")
        except:
            pass
        return None, None


def discover_apis(env_config, known_endpoints_config):
    """Discover and test APIs"""
    BASE_URL = env_config['base_url']
    API_PREFIX = env_config.get('api_prefix', '/api')
    headers = env_config.get('headers', {
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    verify_ssl = env_config.get('verify_ssl', False)
    timeout = env_config.get('timeout', 10)
    
    print(f"\n{'='*80}")
    print(f"API Discovery")
    print(f"{'='*80}")
    print(f"Environment: {env_config.get('description', 'N/A')}")
    print(f"Base URL: {BASE_URL}")
    print(f"API Prefix: {API_PREFIX}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    # Build known endpoints from config
    known_endpoints = {}
    if known_endpoints_config:
        for resource, endpoint_info in known_endpoints_config.items():
            resource_name = resource.capitalize()
            path = endpoint_info.get('path', f'{API_PREFIX}/{resource_name}')
            known_endpoints[resource_name] = {
                f"GET {path}": f"List all {resource}",
                f"GET {path}/{{id}}": f"Get {resource[:-1] if resource.endswith('s') else resource} by ID",
                f"POST {path}": f"Create new {resource[:-1] if resource.endswith('s') else resource}",
                f"PUT {path}/{{id}}": f"Update {resource[:-1] if resource.endswith('s') else resource}",
                f"DELETE {path}/{{id}}": f"Delete {resource[:-1] if resource.endswith('s') else resource}"
            }
    else:
        # Fallback defaults
        known_endpoints = {
            "Authors": {
                "GET /api/Authors": "List all authors",
                "GET /api/Authors/{id}": "Get author by ID",
                "POST /api/Authors": "Create new author",
                "PUT /api/Authors/{id}": "Update author",
                "DELETE /api/Authors/{id}": "Delete author"
            },
            "Books": {
                "GET /api/Books": "List all books",
                "GET /api/Books/{id}": "Get book by ID",
                "POST /api/Books": "Create new book",
                "PUT /api/Books/{id}": "Update book",
                "DELETE /api/Books/{id}": "Delete book"
            }
        }

    # Additional potential endpoints to check
    potential_endpoints = [
        "/api",
        f"{API_PREFIX}/Genres",
        f"{API_PREFIX}/Customers",
        f"{API_PREFIX}/Rentals",
        f"{API_PREFIX}/Stocks",
        f"{API_PREFIX}/Users",
        f"{API_PREFIX}/Roles",
        "/swagger",
        "/swagger/v1/swagger.json",
        "/api/swagger.json",
        "/health",
        f"{API_PREFIX}/health"
    ]

    available_apis = []
    unavailable_apis = []

    print("="*80)
    print("TESTING KNOWN ENDPOINTS")
    print("="*80 + "\n")

    # Test known endpoints
    for resource, endpoints in known_endpoints.items():
        print(f"\n{resource} Endpoints:")
        print("-" * 40)
        
        for endpoint, description in endpoints.items():
            method, path = endpoint.split(" ", 1)
            url = f"{BASE_URL}{path}"
            
            # Only test GET methods
            if method == "GET" and "{id}" not in path:
                try:
                    response = requests.get(url, headers=headers, verify=verify_ssl, timeout=timeout)
                    status = "✓ AVAILABLE" if response.status_code == 200 else f"✗ {response.status_code}"
                    print(f"{endpoint:40} - {status}")
                    print(f"  Description: {description}")
                    
                    if response.status_code == 200:
                        available_apis.append({
                            'endpoint': endpoint,
                            'url': url,
                            'description': description,
                            'status_code': response.status_code
                        })
                    else:
                        unavailable_apis.append({
                            'endpoint': endpoint,
                            'url': url,
                            'description': description,
                            'status_code': response.status_code
                        })
                except requests.exceptions.RequestException as e:
                    print(f"{endpoint:40} - ✗ ERROR: {str(e)}")
                    unavailable_apis.append({
                        'endpoint': endpoint,
                        'url': url,
                        'description': description,
                        'error': str(e)
                    })
            else:
                # For other methods, just document them
                print(f"{endpoint:40} - (Not tested - {method} method)")

    print("\n" + "="*80)
    print("DISCOVERING ADDITIONAL ENDPOINTS")
    print("="*80 + "\n")

    # Try to discover additional endpoints
    for endpoint in potential_endpoints:
        url = f"{BASE_URL}{endpoint}"
        
        try:
            response = requests.get(url, headers=headers, verify=verify_ssl, timeout=timeout)
            if response.status_code in [200, 301, 302]:
                print(f"✓ Found: {endpoint:40} - Status: {response.status_code}")
                available_apis.append({
                    'endpoint': f"GET {endpoint}",
                    'url': url,
                    'description': 'Additional discovered endpoint',
                    'status_code': response.status_code
                })
                
                # Try to get content info
                content_type = response.headers.get('Content-Type', '')
                if 'json' in content_type:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"  → Returns array with {len(data)} items")
                        elif isinstance(data, dict):
                            print(f"  → Returns object with keys: {', '.join(list(data.keys())[:5])}")
                    except:
                        pass
            else:
                print(f"✗ {endpoint:40} - Status: {response.status_code}")
        except requests.exceptions.RequestException:
            pass  # Silently skip unavailable endpoints

    return available_apis, unavailable_apis


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Discover and test API endpoints using api_config.json',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test target environment (default)
  python discover_apis.py
  
  # Test source environment
  python discover_apis.py --env source
  
  # Test local environment
  python discover_apis.py --env local
  
  # Use custom config file
  python discover_apis.py --env target --config ../custom_api_config.json
  
  # Save output to file
  python discover_apis.py --env source --output api_discovery_source.json
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
    
    parser.add_argument(
        '--output',
        help='Save results to JSON file (optional)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    env_config, endpoints_config = load_api_config(args.config, args.env)
    
    if not env_config:
        print("\nFailed to load configuration. Exiting.")
        return 1
    
    # Run API discovery
    available, unavailable = discover_apis(env_config, endpoints_config)
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nAvailable APIs: {len(available)}")
    print(f"Unavailable APIs: {len(unavailable)}")
    
    if available:
        print("\n✓ Available Endpoints:")
        for api in available:
            print(f"  - {api['endpoint']}")
    
    if unavailable:
        print("\n✗ Unavailable Endpoints:")
        for api in unavailable:
            error_info = f" (Error: {api['error']})" if 'error' in api else f" (Status: {api.get('status_code', 'N/A')})"
            print(f"  - {api['endpoint']}{error_info}")
    
    # Save to file if requested
    if args.output:
        results = {
            'timestamp': datetime.now().isoformat(),
            'environment': args.env,
            'base_url': env_config['base_url'],
            'available_apis': available,
            'unavailable_apis': unavailable,
            'summary': {
                'total_available': len(available),
                'total_unavailable': len(unavailable)
            }
        }
        
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to: {args.output}")
    
    print("\n" + "="*80)
    return 0


if __name__ == "__main__":
    exit(main())
