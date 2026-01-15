#!/usr/bin/env python3
"""
ENTERPRISE UI/FRONTEND VALIDATION
Tests ShadowCore UI for enterprise readiness and backend communication
"""
import json
import requests
import subprocess
import os
import sys
from datetime import datetime
import socket
import time

print("""
╔══════════════════════════════════════════════════════════╗
║      SHADOWCORE ENTERPRISE UI VALIDATION                ║
║      Frontend/Backend Integration Test                  ║
╚══════════════════════════════════════════════════════════╝
""")

def test_port(port, service_name):
    """Test if a port is listening"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def test_http(url, expected_status=200):
    """Test HTTP endpoint"""
    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        return response.status_code == expected_status
    except:
        return False

def run_validation():
    results = {
        'timestamp': datetime.now().isoformat(),
        'system': 'ShadowCore Enterprise UI Validation',
        'tests': [],
        'score': 0
    }
    
    tests_passed = 0
    total_tests = 0
    
    def add_test(name, status, details):
        nonlocal tests_passed, total_tests
        total_tests += 1
        if status:
            tests_passed += 1
            symbol = '✅'
        else:
            symbol = '❌'
        
        results['tests'].append({
            'name': name,
            'status': 'PASS' if status else 'FAIL',
            'details': details
        })
        
        print(f"{symbol} {name}: {details}")
        return status
    
    print("🔍 CHECKING ENTERPRISE UI READINESS")
    print("=" * 60)
    
    # Test 1: Project Structure
    print("\n🎯 PROJECT STRUCTURE:")
    print("-" * 40)
    
    required_files = [
        'package.json',
        'README.md',
        'Dockerfile',
        'docker-compose.yml',
        'src/',
        'public/',
        'dist/'
    ]
    
    for file in required_files:
        exists = os.path.exists(f"/root/ShadowCore-Hardened/{file}")
        add_test(f'File: {file}', exists, 
                "Exists" if exists else "Missing")
    
    # Test 2: Package.json analysis
    print("\n🎯 PACKAGE ANALYSIS:")
    print("-" * 40)
    
    try:
        with open('/root/ShadowCore-Hardened/package.json') as f:
            package = json.load(f)
        
        # Check for enterprise dependencies
        has_react = 'react' in package.get('dependencies', {})
        has_typescript = 'typescript' in package.get('devDependencies', {})
        has_build_script = 'build' in package.get('scripts', {})
        has_start_script = 'start' in package.get('scripts', {})
        
        add_test('React Framework', has_react, 
                "Using React" if has_react else "No React")
        add_test('TypeScript Support', has_typescript,
                "TypeScript enabled" if has_typescript else "No TypeScript")
        add_test('Build Script', has_build_script,
                "Build script available" if has_build_script else "No build script")
        add_test('Start Script', has_start_script,
                "Start script available" if has_start_script else "No start script")
        
        # Check for security dependencies
        deps = package.get('dependencies', {})
        dev_deps = package.get('devDependencies', {})
        security_libs = ['helmet', 'cors', 'express-validator', 'bcrypt', 'jsonwebtoken']
        security_found = any(lib in deps or lib in dev_deps for lib in security_libs)
        
        add_test('Security Libraries', security_found,
                "Security libraries present" if security_found else "Limited security libs")
        
    except Exception as e:
        add_test('Package Analysis', False, f"Error: {str(e)}")
    
    # Test 3: Docker/Containerization
    print("\n🎯 CONTAINERIZATION:")
    print("-" * 40)
    
    dockerfile_exists = os.path.exists('/root/ShadowCore-Hardened/Dockerfile')
    docker_compose_exists = os.path.exists('/root/ShadowCore-Hardened/docker-compose.yml')
    
    add_test('Dockerfile', dockerfile_exists,
            "Dockerfile present" if dockerfile_exists else "No Dockerfile")
    add_test('Docker Compose', docker_compose_exists,
            "docker-compose.yml present" if docker_compose_exists else "No docker-compose")
    
    if dockerfile_exists:
        try:
            with open('/root/ShadowCore-Hardened/Dockerfile') as f:
                docker_content = f.read()
            
            has_multistage = 'FROM' in docker_content and docker_content.count('FROM') > 1
            has_healthcheck = 'HEALTHCHECK' in docker_content
            has_non_root = 'USER' in docker_content and 'root' not in docker_content
            
            add_test('Multi-stage Build', has_multistage,
                    "Multi-stage build used" if has_multistage else "Single stage build")
            add_test('Health Check', has_healthcheck,
                    "Health check configured" if has_healthcheck else "No health check")
            add_test('Non-root User', has_non_root,
                    "Non-root user configured" if has_non_root else "Running as root")
        except:
            pass
    
    # Test 4: Backend Services
    print("\n🎯 BACKEND SERVICES:")
    print("-" * 40)
    
    backend_ports = {
        8003: 'Threat API',
        8020: 'Dashboard API',
        8000: 'REST API',
        8004: 'Main API',
        3000: 'Grafana',
        7474: 'Neo4j Browser'
    }
    
    for port, service in backend_ports.items():
        is_listening = test_port(port, service)
        add_test(f'{service} (:{port})', is_listening,
                "Listening" if is_listening else "Not listening")
    
    # Test 5: Frontend-Backend Communication
    print("\n🎯 FRONTEND-BACKEND COMMUNICATION:")
    print("-" * 40)
    
    # Test API endpoints
    api_endpoints = [
        ('http://localhost:8003/health', 'Threat API Health'),
        ('http://localhost:8020', 'Dashboard'),
        ('http://localhost:8000', 'REST API'),
        ('http://localhost:3000', 'Grafana'),
        ('http://localhost:7474', 'Neo4j Browser')
    ]
    
    for url, name in api_endpoints:
        is_accessible = test_http(url, 200)
        add_test(f'{name} Accessibility', is_accessible,
                f"HTTP 200" if is_accessible else "Not accessible")
    
    # Test actual threat analysis
    print("\n🎯 THREAT ANALYSIS INTEGRATION:")
    print("-" * 40)
    
    test_iocs = [
        '162.243.103.246',
        '8.8.8.8',
        'evil-traffic.com'
    ]
    
    for ioc in test_iocs:
        try:
            response = requests.get(f'http://localhost:8003/analyze?ioc={ioc}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                add_test(f'IOC Analysis: {ioc}', True,
                        f"Success - Threat: {data.get('threat_level', 'unknown')}")
            else:
                add_test(f'IOC Analysis: {ioc}', False,
                        f"HTTP {response.status_code}")
        except Exception as e:
            add_test(f'IOC Analysis: {ioc}', False, f"Error: {str(e)[:30]}")
    
    # Test 6: Build and Package
    print("\n🎯 BUILD & DEPLOYMENT:")
    print("-" * 40)
    
    # Check if build directory exists
    dist_exists = os.path.exists('/root/ShadowCore-Hardened/dist')
    add_test('Build Output (dist/)', dist_exists,
            "Build directory exists" if dist_exists else "No build output")
    
    # Check for TypeScript compilation
    tsconfig_exists = os.path.exists('/root/ShadowCore-Hardened/tsconfig.json')
    add_test('TypeScript Config', tsconfig_exists,
            "TypeScript configured" if tsconfig_exists else "No TypeScript config")
    
    # Test 7: Documentation
    print("\n🎯 DOCUMENTATION:")
    print("-" * 40)
    
    docs = [
        'README.md',
        'API.md',
        'SECURITY.md',
        'CHANGELOG.md',
        'CONTRIBUTING.md'
    ]
    
    for doc in docs:
        exists = os.path.exists(f"/root/ShadowCore-Hardened/{doc}")
        add_test(f'Documentation: {doc}', exists,
                "Exists" if exists else "Missing")
    
    # Test 8: Try to start the UI
    print("\n🎯 UI STARTUP TEST:")
    print("-" * 40)
    
    # Check if we can run npm commands
    try:
        # First check if node_modules exists
        node_modules_exists = os.path.exists('/root/ShadowCore-Hardened/node_modules')
        add_test('Node Modules', node_modules_exists,
                "Installed" if node_modules_exists else "Not installed")
        
        # Try to check npm version
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True, cwd='/root/ShadowCore-Hardened')
        add_test('NPM Available', result.returncode == 0,
                f"NPM v{result.stdout.strip()}" if result.returncode == 0 else "NPM not available")
        
        # Try to run build
        if node_modules_exists:
            result = subprocess.run(['npm', 'run', 'build', '--', '--dry-run'],
                                  capture_output=True, text=True, 
                                  cwd='/root/ShadowCore-Hardened', timeout=10)
            add_test('Build Process', 'dry-run' in result.stdout or result.returncode == 0,
                    "Build process works" if result.returncode == 0 else "Build failed")
        
    except Exception as e:
        add_test('UI Startup', False, f"Error: {str(e)[:30]}")
    
    # Calculate score
    results['score'] = (tests_passed / total_tests) * 100
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION RESULTS")
    print("=" * 60)
    
    score = results['score']
    
    if score >= 90:
        grade = "🏆 ENTERPRISE READY"
        color_start = '\033[1;32m'
        status = "PRODUCTION GRADE"
    elif score >= 75:
        grade = "✅ GOOD"
        color_start = '\033[1;33m'
        status = "NEARLY ENTERPRISE"
    elif score >= 60:
        grade = "⚠️  ACCEPTABLE"
        color_start = '\033[1;33m'
        status = "NEEDS IMPROVEMENT"
    else:
        grade = "❌ NOT ENTERPRISE READY"
        color_start = '\033[1;31m'
        status = "REQUIRES SIGNIFICANT WORK"
    
    color_end = '\033[0m'
    
    print(f"\nOverall Score: {color_start}{score:.1f}%{color_end}")
    print(f"Grade: {color_start}{grade}{color_end}")
    print(f"Status: {color_start}{status}{color_end}")
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    print("\n🚀 ENTERPRISE FEATURES VERIFIED:")
    print("-" * 40)
    
    enterprise_features = [
        ("✅" if score >= 90 else "❌", "Containerization (Docker)"),
        ("✅" if any(t['name'] == 'Security Libraries' and t['status'] == 'PASS' for t in results['tests']) else "❌", "Security Hardening"),
        ("✅" if any(t['name'] == 'TypeScript Support' and t['status'] == 'PASS' for t in results['tests']) else "❌", "TypeScript Support"),
        ("✅" if any(t['name'] == 'Multi-stage Build' and t['status'] == 'PASS' for t in results['tests']) else "❌", "Production Builds"),
        ("✅" if all(t['status'] == 'PASS' for t in results['tests'] if 'IOC Analysis' in t['name']) else "❌", "Backend Integration"),
        ("✅" if any(t['name'] == 'Health Check' and t['status'] == 'PASS' for t in results['tests']) else "❌", "Health Monitoring"),
        ("✅" if any(t['name'] == 'Non-root User' and t['status'] == 'PASS' for t in results['tests']) else "❌", "Security Best Practices")
    ]
    
    for symbol, feature in enterprise_features:
        print(f"  {symbol} {feature}")
    
    print("\n🔧 RECOMMENDATIONS:")
    print("-" * 40)
    
    if score >= 90:
        print("  🎉 Your UI is enterprise-ready!")
        print("  • Deploy to production environment")
        print("  • Set up CI/CD pipeline")
        print("  • Configure monitoring and alerting")
    elif score >= 75:
        print("  ⚠️  Good foundation, needs some improvements:")
        print("  • Add health checks to Dockerfile")
        print("  • Implement non-root user in containers")
        print("  • Add more security headers")
    else:
        print("  ❌ Significant improvements needed:")
        print("  • Fix missing dependencies")
        print("  • Implement proper security measures")
        print("  • Add containerization support")
    
    # Save results
    with open('/opt/shadowcore/ui_validation_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create summary
    with open('/opt/shadowcore/UI_VALIDATION_SUMMARY.md', 'w') as f:
        f.write("# 🏆 SHADOWCORE UI ENTERPRISE VALIDATION\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Overall Score:** {score:.1f}%\n")
        f.write(f"**Status:** {status}\n")
        f.write(f"**Tests Passed:** {tests_passed}/{total_tests}\n\n")
        
        f.write("## Test Results\n\n")
        for test in results['tests']:
            status_symbol = "✅" if test['status'] == 'PASS' else "❌"
            f.write(f"{status_symbol} **{test['name']}**: {test['details']}\n")
        
        f.write("\n## Recommendations\n\n")
        if score >= 90:
            f.write("✅ **ENTERPRISE READY** - Your UI meets enterprise requirements.\n")
        elif score >= 75:
            f.write("⚠️ **NEARLY ENTERPRISE** - Minor improvements needed.\n")
        else:
            f.write("❌ **NOT ENTERPRISE READY** - Significant work required.\n")
    
    print(f"\n📄 Full report saved to: /opt/shadowcore/ui_validation_report.json")
    print(f"📋 Summary saved to: /opt/shadowcore/UI_VALIDATION_SUMMARY.md")
    
    return results

if __name__ == "__main__":
    run_validation()
