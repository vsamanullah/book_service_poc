"""
Comprehensive Endpoint Test Script
Tests all CRUD operations for Authors and Books endpoints
Corresponds to all 10 JMeter test scripts
Updated to use api_config.json with environment parameters
"""

import requests
import urllib3
import json
import argparse
from datetime import datetime
import random
import string
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


def generate_random_string(length=8):
    """Generate random string for test data"""
    return ''.join(random.choices(string.ascii_letters, k=length))


def comprehensive_test(env_config):
    """Run comprehensive endpoint tests"""
    BASE_URL = env_config['base_url']
    headers = env_config.get('headers', {
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    verify_ssl = env_config.get('verify_ssl', False)
    timeout = env_config.get('timeout', 10)
    
    print(f"\n{'='*80}")
    print(f"Comprehensive Endpoint Test for Book Service")
    print(f"{'='*80}")
    print(f"Environment: {env_config.get('description', 'N/A')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    test_results = []

    # ============================================================================
    # AUTHORS ENDPOINTS TESTING
    # ============================================================================
    print("=" * 80)
    print("TESTING AUTHORS ENDPOINTS")
    print("=" * 80 + "\n")

    # Test 1: GET All Authors (from 01_Authors_GET_All.jmx)
    print("1. GET /api/Authors - Get all authors")
    try:
        response = requests.get(f"{BASE_URL}/api/Authors", headers=headers, verify=verify_ssl, timeout=timeout)
        print(f"   [✓] Status: {response.status_code} | Response Time: {response.elapsed.total_seconds():.3f}s")
        if response.status_code == 200:
            authors = response.json()
            print(f"   [i] Found {len(authors)} authors")
            test_results.append({"test": "GET /api/Authors", "status": "PASS"})
        else:
            test_results.append({"test": "GET /api/Authors", "status": "FAIL", "code": response.status_code})
    except Exception as e:
        print(f"   [✗] Error: {str(e)}")
        test_results.append({"test": "GET /api/Authors", "status": "ERROR", "error": str(e)})

    print()

    # Test 2: POST Create Author (from 03_Authors_POST_Create.jmx)
    print("2. POST /api/Authors - Create a new author")
    test_author_name = f"TestAuthor_{generate_random_string()}"
    author_id = None
    try:
        payload = {"Name": test_author_name}
        response = requests.post(f"{BASE_URL}/api/Authors", headers=headers, json=payload, verify=verify_ssl, timeout=timeout)
        print(f"   [✓] Status: {response.status_code} | Response Time: {response.elapsed.total_seconds():.3f}s")
        if response.status_code == 201:
            author_data = response.json()
            author_id = author_data.get('Id')
            print(f"   [i] Created author with ID: {author_id}, Name: {author_data.get('Name')}")
            test_results.append({"test": "POST /api/Authors", "status": "PASS", "id": author_id})
        else:
            print(f"   [!] Unexpected status code: {response.status_code}")
            print(f"   [!] Response: {response.text[:200]}")
            test_results.append({"test": "POST /api/Authors", "status": "FAIL", "code": response.status_code})
    except Exception as e:
        print(f"   [✗] Error: {str(e)}")
        test_results.append({"test": "POST /api/Authors", "status": "ERROR", "error": str(e)})

    print()

    # Test 3: GET Author by ID (from 02_Authors_GET_ById.jmx)
    if author_id:
        print(f"3. GET /api/Authors/{author_id} - Get author by ID")
        try:
            response = requests.get(f"{BASE_URL}/api/Authors/{author_id}", headers=headers, verify=verify_ssl, timeout=timeout)
            print(f"   [✓] Status: {response.status_code} | Response Time: {response.elapsed.total_seconds():.3f}s")
            if response.status_code == 200:
                author_data = response.json()
                print(f"   [i] Author: ID={author_data.get('Id')}, Name={author_data.get('Name')}")
                test_results.append({"test": "GET /api/Authors/{id}", "status": "PASS"})
            else:
                test_results.append({"test": "GET /api/Authors/{id}", "status": "FAIL", "code": response.status_code})
        except Exception as e:
            print(f"   [✗] Error: {str(e)}")
            test_results.append({"test": "GET /api/Authors/{id}", "status": "ERROR", "error": str(e)})
        print()

    # Test 4: PUT Update Author (from 04_Authors_PUT_Update.jmx)
    if author_id:
        print(f"4. PUT /api/Authors/{author_id} - Update author")
        updated_name = f"UpdatedAuthor_{generate_random_string()}"
        try:
            payload = {"Id": author_id, "Name": updated_name}
            response = requests.put(f"{BASE_URL}/api/Authors/{author_id}", headers=headers, json=payload, verify=verify_ssl, timeout=timeout)
            print(f"   [✓] Status: {response.status_code} | Response Time: {response.elapsed.total_seconds():.3f}s")
            if response.status_code in [200, 204]:
                print(f"   [i] Successfully updated author to: {updated_name}")
                test_results.append({"test": "PUT /api/Authors/{id}", "status": "PASS"})
            else:
                print(f"   [!] Unexpected status code: {response.status_code}")
                test_results.append({"test": "PUT /api/Authors/{id}", "status": "FAIL", "code": response.status_code})
        except Exception as e:
            print(f"   [✗] Error: {str(e)}")
            test_results.append({"test": "PUT /api/Authors/{id}", "status": "ERROR", "error": str(e)})
        print()

    # Test 5: DELETE Author (from 05_Authors_DELETE.jmx)
    if author_id:
        print(f"5. DELETE /api/Authors/{author_id} - Delete author")
        try:
            response = requests.delete(f"{BASE_URL}/api/Authors/{author_id}", headers=headers, verify=verify_ssl, timeout=timeout)
            print(f"   [✓] Status: {response.status_code} | Response Time: {response.elapsed.total_seconds():.3f}s")
            if response.status_code in [200, 204]:
                print(f"   [i] Successfully deleted author with ID: {author_id}")
                test_results.append({"test": "DELETE /api/Authors/{id}", "status": "PASS"})
            else:
                print(f"   [!] Unexpected status code: {response.status_code}")
                test_results.append({"test": "DELETE /api/Authors/{id}", "status": "FAIL", "code": response.status_code})
        except Exception as e:
            print(f"   [✗] Error: {str(e)}")
            test_results.append({"test": "DELETE /api/Authors/{id}", "status": "ERROR", "error": str(e)})
        print()

    # ============================================================================
    # BOOKS ENDPOINTS TESTING
    # ============================================================================
    print("=" * 80)
    print("TESTING BOOKS ENDPOINTS")
    print("=" * 80 + "\n")

    # First, create an author for book tests
    print("Setup: Creating an author for book tests...")
    try:
        payload = {"Name": f"BookTestAuthor_{generate_random_string()}"}
        response = requests.post(f"{BASE_URL}/api/Authors", headers=headers, json=payload, verify=verify_ssl, timeout=timeout)
        if response.status_code == 201:
            test_author = response.json()
            test_author_id = test_author.get('Id')
            print(f"   [✓] Created test author with ID: {test_author_id}\n")
        else:
            test_author_id = 1  # Fallback to ID 1
            print(f"   [!] Using fallback author ID: {test_author_id}\n")
    except:
        test_author_id = 1
        print(f"   [!] Using fallback author ID: {test_author_id}\n")

    # Test 6: GET All Books (from 06_Books_GET_All.jmx)
    print("6. GET /api/Books - Get all books")
    try:
        response = requests.get(f"{BASE_URL}/api/Books", headers=headers, verify=verify_ssl, timeout=timeout)
        print(f"   [✓] Status: {response.status_code} | Response Time: {response.elapsed.total_seconds():.3f}s")
        if response.status_code == 200:
            books = response.json()
            print(f"   [i] Found {len(books)} books")
            test_results.append({"test": "GET /api/Books", "status": "PASS"})
        else:
            test_results.append({"test": "GET /api/Books", "status": "FAIL", "code": response.status_code})
    except Exception as e:
        print(f"   [✗] Error: {str(e)}")
        test_results.append({"test": "GET /api/Books", "status": "ERROR", "error": str(e)})

    print()

    # Test 7: POST Create Book (from 08_Books_POST_Create.jmx)
    print("7. POST /api/Books - Create a new book")
    book_id = None
    try:
        payload = {
            "Title": f"TestBook_{generate_random_string()}",
            "AuthorId": test_author_id
        }
        response = requests.post(f"{BASE_URL}/api/Books", headers=headers, json=payload, verify=verify_ssl, timeout=timeout)
        print(f"   [✓] Status: {response.status_code} | Response Time: {response.elapsed.total_seconds():.3f}s")
        if response.status_code == 201:
            book_data = response.json()
            book_id = book_data.get('Id')
            print(f"   [i] Created book with ID: {book_id}, Title: {book_data.get('Title')}")
            test_results.append({"test": "POST /api/Books", "status": "PASS", "id": book_id})
        else:
            print(f"   [!] Unexpected status code: {response.status_code}")
            print(f"   [!] Response: {response.text[:200]}")
            test_results.append({"test": "POST /api/Books", "status": "FAIL", "code": response.status_code})
    except Exception as e:
        print(f"   [✗] Error: {str(e)}")
        test_results.append({"test": "POST /api/Books", "status": "ERROR", "error": str(e)})

    print()

    # Test 8: GET Book by ID (from 07_Books_GET_ById.jmx)
    if book_id:
        print(f"8. GET /api/Books/{book_id} - Get book by ID")
        try:
            response = requests.get(f"{BASE_URL}/api/Books/{book_id}", headers=headers, verify=verify_ssl, timeout=timeout)
            print(f"   [✓] Status: {response.status_code} | Response Time: {response.elapsed.total_seconds():.3f}s")
            if response.status_code == 200:
                book_data = response.json()
                print(f"   [i] Book: ID={book_data.get('Id')}, Title={book_data.get('Title')}, AuthorId={book_data.get('AuthorId')}")
                test_results.append({"test": "GET /api/Books/{id}", "status": "PASS"})
            else:
                test_results.append({"test": "GET /api/Books/{id}", "status": "FAIL", "code": response.status_code})
        except Exception as e:
            print(f"   [✗] Error: {str(e)}")
            test_results.append({"test": "GET /api/Books/{id}", "status": "ERROR", "error": str(e)})
        print()

    # Test 9: PUT Update Book (from 09_Books_PUT_Update.jmx)
    if book_id:
        print(f"9. PUT /api/Books/{book_id} - Update book")
        updated_title = f"UpdatedBook_{generate_random_string()}"
        try:
            payload = {"Id": book_id, "Title": updated_title, "AuthorId": test_author_id}
            response = requests.put(f"{BASE_URL}/api/Books/{book_id}", headers=headers, json=payload, verify=verify_ssl, timeout=timeout)
            print(f"   [✓] Status: {response.status_code} | Response Time: {response.elapsed.total_seconds():.3f}s")
            if response.status_code in [200, 204]:
                print(f"   [i] Successfully updated book to: {updated_title}")
                test_results.append({"test": "PUT /api/Books/{id}", "status": "PASS"})
            else:
                print(f"   [!] Unexpected status code: {response.status_code}")
                test_results.append({"test": "PUT /api/Books/{id}", "status": "FAIL", "code": response.status_code})
        except Exception as e:
            print(f"   [✗] Error: {str(e)}")
            test_results.append({"test": "PUT /api/Books/{id}", "status": "ERROR", "error": str(e)})
        print()

    # Test 10: DELETE Book (from 10_Books_DELETE.jmx)
    if book_id:
        print(f"10. DELETE /api/Books/{book_id} - Delete book")
        try:
            response = requests.delete(f"{BASE_URL}/api/Books/{book_id}", headers=headers, verify=verify_ssl, timeout=timeout)
            print(f"   [✓] Status: {response.status_code} | Response Time: {response.elapsed.total_seconds():.3f}s")
            if response.status_code in [200, 204]:
                print(f"   [i] Successfully deleted book with ID: {book_id}")
                test_results.append({"test": "DELETE /api/Books/{id}", "status": "PASS"})
            else:
                print(f"   [!] Unexpected status code: {response.status_code}")
                test_results.append({"test": "DELETE /api/Books/{id}", "status": "FAIL", "code": response.status_code})
        except Exception as e:
            print(f"   [✗] Error: {str(e)}")
            test_results.append({"test": "DELETE /api/Books/{id}", "status": "ERROR", "error": str(e)})
        print()

    # ============================================================================
    # SUMMARY
    # ============================================================================
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80 + "\n")

    passed = sum(1 for r in test_results if r.get('status') == 'PASS')
    failed = sum(1 for r in test_results if r.get('status') == 'FAIL')
    errors = sum(1 for r in test_results if r.get('status') == 'ERROR')
    total = len(test_results)

    print(f"Total Tests: {total}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"⚠ Errors: {errors}")
    print(f"\nSuccess Rate: {(passed/total*100):.1f}%")

    if failed > 0 or errors > 0:
        print("\n⚠ Failed/Error Tests:")
        for r in test_results:
            if r.get('status') in ['FAIL', 'ERROR']:
                print(f"   - {r['test']}: {r.get('status')} (Code: {r.get('code', 'N/A')})")

    print("\n" + "=" * 80)
    print(f"All JMeter script endpoints have been tested!")
    print("=" * 80 + "\n")
    
    return test_results


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Comprehensive test of all API endpoints using api_config.json',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test target environment (default)
  python comprehensive_endpoint_test.py
  
  # Test source environment
  python comprehensive_endpoint_test.py --env source
  
  # Test local environment
  python comprehensive_endpoint_test.py --env local
  
  # Use custom config file
  python comprehensive_endpoint_test.py --env target --config ../custom_api_config.json
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
    
    # Run comprehensive tests
    results = comprehensive_test(env_config)
    
    return 0


if __name__ == "__main__":
    exit(main())
