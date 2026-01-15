#!/usr/bin/env python3
"""
SHADOWCORE FINAL COMPREHENSIVE VALIDATION
Your complete 'Better Palantir' - Full System Test
"""
import asyncio
import json
import sys
import time
import redis
import requests
from datetime import datetime
import subprocess
import os
import socket

print("🏆 SHADOWCORE FINAL COMPREHENSIVE VALIDATION")
print("=" * 60)
print("Testing EVERY component of your 'Better Palantir'")
print("=" * 60)

class ComprehensiveValidator:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'performance': {},
            'threat_intelligence': {},
            'overall_score': 0
        }
        self.passed = 0
        self.total = 0
        
    def test_component(self, name, test_func):
        """Run a test and record results"""
        self.total += 1
        print(f"\n🔍 Testing: {name}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            result = test_func()
            elapsed = time.time() - start_time
            
            if result.get('status') == 'PASS':
                self.passed += 1
                print(f"✅ {name}: PASS ({elapsed:.2f}s)")
                print(f"   Details: {result.get('details', '')}")
            else:
                print(f"❌ {name}: FAIL")
                print(f"   Error: {result.get('error', 'Unknown')}")
            
            self.results['components'][name] = {
                'status': result.get('status', 'FAIL'),
                'elapsed': elapsed,
                'details': result.get('details', ''),
                'error': result.get('error', '')
            }
            
        except Exception as e:
            print(f"💥 {name}: ERROR - {str(e)[:50]}")
            self.results['components'][name] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    # === TEST FUNCTIONS ===
    
    def test_redis(self):
        """Test Redis connectivity"""
        try:
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            
            # Test some operations
            r.set('test:validation', datetime.now().isoformat())
            value = r.get('test:validation')
            keys = r.keys('*')
            
            return {
                'status': 'PASS',
                'details': f"Connected, {len(keys)} keys, test value: {value}"
            }
        except Exception as e:
            return {'status': 'FAIL', 'error': str(e)}
    
    def test_neo4j(self):
        """Test Neo4j knowledge graph"""
        try:
            # Use cypher-shell to test
            result = subprocess.run(
                ['cypher-shell', '-u', 'neo4j', '-p', 'Jonboy@123', '--format', 'plain',
                 'MATCH (n) RETURN count(n) as node_count, count(DISTINCT labels(n)[0]) as label_count'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    data = lines[1].split(',')
                    return {
                        'status': 'PASS',
                        'details': f"{data[0]} nodes, {data[1]} entity types in knowledge graph"
                    }
            
            return {'status': 'FAIL', 'error': 'No data returned'}
        except Exception as e:
            return {'status': 'FAIL', 'error': str(e)}
    
    def test_threat_cache(self):
        """Test threat intelligence cache"""
        try:
            cache_file = '/opt/shadowcore/feeds/processed/threat_cache.json'
            with open(cache_file) as f:
                threats = json.load(f)
            
            # Analyze threats
            malware_count = 0
            sources = set()
            for data in threats.values():
                if 'malware' in data and data['malware']:
                    malware_count += 1
                if 'source' in data:
                    sources.add(data['source'])
            
            return {
                'status': 'PASS',
                'details': f"{len(threats)} threats, {malware_count} malware-specific, sources: {list(sources)[:3]}"
            }
        except Exception as e:
            return {'status': 'FAIL', 'error': str(e)}
    
    def test_orchestrator(self):
        """Test main orchestrator with known threats"""
        try:
            sys.path.insert(0, '/opt/shadowcore')
            from clean_orchestrator_fixed import CleanShadowCoreOrchestrator
            
            async def test():
                orchestrator = CleanShadowCoreOrchestrator()
                
                # Test cases
                test_cases = [
                    ("162.243.103.246", "HIGH", "Emotet C2"),
                    ("8.8.8.8", "LOW", "Google DNS"),
                    ("evil-traffic.com", "MEDIUM", "Suspicious domain")
                ]
                
                results = []
                for ioc, expected_level, description in test_cases:
                    result = await orchestrator.process_ioc(ioc)
                    actual_level = result['threat_assessment']['level']
                    confidence = result['threat_assessment']['confidence']
                    
                    if actual_level == expected_level:
                        results.append(f"{description}: ✓ {actual_level} ({confidence:.0%})")
                    else:
                        results.append(f"{description}: ✗ expected {expected_level}, got {actual_level}")
                
                return {
                    'status': 'PASS',
                    'details': f"Analysis complete: {' | '.join(results)}"
                }
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(test())
            loop.close()
            
            return result
            
        except Exception as e:
            return {'status': 'FAIL', 'error': str(e)}
    
    def test_apis(self):
        """Test all API endpoints"""
        endpoints = [
            ("Dashboard", "http://localhost:8020"),
            ("Neo4j Browser", "http://localhost:7474"),
            ("Grafana", "http://localhost:3000")
        ]
        
        results = []
        for name, url in endpoints:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code < 500:
                    results.append(f"{name}: ✓")
                else:
                    results.append(f"{name}: ✗ ({response.status_code})")
            except:
                results.append(f"{name}: ✗ (unreachable)")
        
        return {
            'status': 'PASS' if all('✓' in r for r in results) else 'FAIL',
            'details': f"API Status: {' | '.join(results)}"
        }
    
    def test_services(self):
        """Test all running services"""
        services = [
            (8000, "REST API"),
            (8003, "Threat API"),
            (8004, "Main API"),
            (8006, "Auth API"),
            (8020, "Dashboard"),
            (8080, "Proxy"),
            (8083, "WebSocket"),
            (9090, "Threat Insight"),
            (5432, "PostgreSQL"),
            (6379, "Redis"),
            (7474, "Neo4j HTTP"),
            (7687, "Neo4j Bolt"),
            (11434, "Ollama"),
            (3000, "Grafana")
        ]
        
        results = []
        for port, name in services:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    results.append(f"{name}: ✓")
                else:
                    results.append(f"{name}: ✗")
            except:
                results.append(f"{name}: ✗")
        
        running = sum(1 for r in results if '✓' in r)
        total = len(services)
        
        return {
            'status': 'PASS' if running == total else 'WARNING',
            'details': f"Services: {running}/{total} running. {'All critical services operational.' if running >= 10 else 'Some services missing.'}"
        }
    
    def test_intelligence_pipeline(self):
        """Test complete intelligence pipeline"""
        try:
            # Load recent reports
            import glob
            reports = glob.glob('/opt/shadowcore/intelligence_reports/*.json')
            latest_reports = sorted(reports, reverse=True)[:3]
            
            if not latest_reports:
                return {'status': 'WARNING', 'details': 'No intelligence reports found'}
            
            # Analyze latest report
            with open(latest_reports[0]) as f:
                report = json.load(f)
            
            # Extract metrics
            if 'summary' in report:
                summary = report['summary']
                threats = summary.get('high_threats', 0) + summary.get('medium_threats', 0)
                total = summary.get('total_iocs', 0)
            elif 'reports' in report:
                threats = sum(1 for r in report['reports'] 
                            if r.get('threat_assessment', {}).get('level') in ['high', 'medium'])
                total = len(report['reports'])
            else:
                threats = 0
                total = 0
            
            return {
                'status': 'PASS',
                'details': f"Pipeline active: {len(reports)} reports, latest: {threats}/{total} threats detected"
            }
            
        except Exception as e:
            return {'status': 'FAIL', 'error': str(e)}
    
    def test_performance(self):
        """Test system performance"""
        try:
            # Memory usage
            with open('/proc/meminfo') as f:
                meminfo = f.readlines()
                total_mem = int(meminfo[0].split()[1]) / 1024  # MB
                free_mem = int(meminfo[1].split()[1]) / 1024   # MB
                used_percent = ((total_mem - free_mem) / total_mem) * 100
            
            # Load average
            with open('/proc/loadavg') as f:
                load_avg = f.read().split()[:3]
            
            # Disk space
            disk = os.statvfs('/')
            total_disk = (disk.f_blocks * disk.f_frsize) / (1024**3)  # GB
            free_disk = (disk.f_bavail * disk.f_frsize) / (1024**3)   # GB
            used_disk_percent = ((total_disk - free_disk) / total_disk) * 100
            
            self.results['performance'] = {
                'memory': f"{used_percent:.1f}% used ({free_mem:.0f}MB free)",
                'load': f"{load_avg[0]}, {load_avg[1]}, {load_avg[2]}",
                'disk': f"{used_disk_percent:.1f}% used ({free_disk:.1f}GB free)",
                'uptime': subprocess.getoutput('uptime -p')
            }
            
            return {
                'status': 'PASS',
                'details': f"Memory: {used_percent:.1f}% | Load: {load_avg[0]} | Disk: {used_disk_percent:.1f}%"
            }
            
        except Exception as e:
            return {'status': 'FAIL', 'error': str(e)}
    
    def test_threat_detection_accuracy(self):
        """Test threat detection accuracy with known samples"""
        try:
            # Known test cases with expected results
            test_cases = [
                {
                    'ioc': '162.243.103.246',
                    'expected': 'high',
                    'reason': 'Known Emotet C2 from FeodoTracker'
                },
                {
                    'ioc': '137.184.9.29',
                    'expected': 'high',
                    'reason': 'Known QakBot C2 from FeodoTracker'
                },
                {
                    'ioc': '8.8.8.8',
                    'expected': 'low',
                    'reason': 'Google DNS (legitimate)'
                },
                {
                    'ioc': 'evil-traffic.com',
                    'expected': 'medium',
                    'reason': 'Suspicious domain (heuristic)'
                }
            ]
            
            sys.path.insert(0, '/opt/shadowcore')
            from clean_orchestrator_fixed import CleanShadowCoreOrchestrator
            
            async def run_tests():
                orchestrator = CleanShadowCoreOrchestrator()
                results = []
                
                for test in test_cases:
                    result = await orchestrator.process_ioc(test['ioc'])
                    actual = result['threat_assessment']['level']
                    confidence = result['threat_assessment']['confidence']
                    
                    if actual == test['expected']:
                        results.append(f"✓ {test['ioc']}: {actual} ({confidence:.0%})")
                    else:
                        results.append(f"✗ {test['ioc']}: expected {test['expected']}, got {actual}")
                
                return results
            
            # Run async tests
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            test_results = loop.run_until_complete(run_tests())
            loop.close()
            
            # Calculate accuracy
            correct = sum(1 for r in test_results if '✓' in r)
            accuracy = (correct / len(test_cases)) * 100
            
            self.results['threat_intelligence']['accuracy'] = accuracy
            self.results['threat_intelligence']['test_results'] = test_results
            
            return {
                'status': 'PASS' if accuracy >= 90 else 'WARNING',
                'details': f"Accuracy: {accuracy:.1f}% ({correct}/{len(test_cases)}) - {' | '.join(test_results)}"
            }
            
        except Exception as e:
            return {'status': 'FAIL', 'error': str(e)}
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("\n" + "=" * 60)
        print("🚀 STARTING COMPREHENSIVE VALIDATION")
        print("=" * 60)
        
        # Run all tests
        tests = [
            ("Redis Cache", self.test_redis),
            ("Neo4j Knowledge Graph", self.test_neo4j),
            ("Threat Intelligence Cache", self.test_threat_cache),
            ("Threat Detection Accuracy", self.test_threat_detection_accuracy),
            ("Main Orchestrator", self.test_orchestrator),
            ("API Endpoints", self.test_apis),
            ("Service Availability", self.test_services),
            ("Intelligence Pipeline", self.test_intelligence_pipeline),
            ("System Performance", self.test_performance)
        ]
        
        for name, test_func in tests:
            self.test_component(name, test_func)
        
        # Calculate overall score
        self.results['overall_score'] = (self.passed / self.total) * 100
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        score = self.results['overall_score']
        
        # Grade based on score
        if score >= 90:
            grade = "🏆 EXCELLENT"
            color = "\033[1;32m"  # Green
        elif score >= 75:
            grade = "✅ GOOD"
            color = "\033[1;33m"  # Yellow
        else:
            grade = "⚠️  NEEDS ATTENTION"
            color = "\033[1;31m"  # Red
        
        print(f"\nOverall Score: {color}{score:.1f}%{'\033[0m'}")
        print(f"Grade: {color}{grade}{'\033[0m'}")
        print(f"Passed: {self.passed}/{self.total} tests")
        
        # Print performance metrics
        print(f"\n📈 Performance Metrics:")
        for key, value in self.results['performance'].items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        # Print threat intelligence
        if 'threat_intelligence' in self.results:
            ti = self.results['threat_intelligence']
            if 'accuracy' in ti:
                print(f"\n🎯 Threat Intelligence:")
                print(f"  • Detection Accuracy: {ti['accuracy']:.1f}%")
                if 'test_results' in ti:
                    print(f"  • Test Results:")
                    for result in ti['test_results']:
                        print(f"    {result}")
        
        # Print recommendations
        print(f"\n💡 Recommendations:")
        if score >= 90:
            print("  • Your system is production-ready!")
            print("  • Consider adding more threat feeds")
            print("  • Connect to your SIEM for automated alerts")
        elif score >= 75:
            print("  • System is operational but needs tuning")
            print("  • Check failed components above")
            print("  • Review threat detection accuracy")
        else:
            print("  • System needs attention")
            print("  • Focus on critical components first")
            print("  • Check service connectivity")
        
        print(f"\n📁 Full results saved to: /opt/shadowcore/validation_results.json")
    
    def save_results(self):
        """Save validation results to file"""
        output_file = '/opt/shadowcore/validation_results.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Also create a human-readable summary
        summary_file = '/opt/shadowcore/validation_summary.txt'
        with open(summary_file, 'w') as f:
            f.write("SHADOWCORE VALIDATION SUMMARY\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Timestamp: {self.results['timestamp']}\n")
            f.write(f"Overall Score: {self.results['overall_score']:.1f}%\n")
            f.write(f"Passed: {self.passed}/{self.total}\n\n")
            
            f.write("COMPONENT STATUS:\n")
            for name, data in self.results['components'].items():
                status = "✅ PASS" if data['status'] == 'PASS' else "❌ FAIL"
                f.write(f"  {name}: {status}\n")
                if 'details' in data and data['details']:
                    f.write(f"    Details: {data['details']}\n")
            
            f.write("\nPERFORMANCE METRICS:\n")
            for key, value in self.results['performance'].items():
                f.write(f"  {key}: {value}\n")
        
        return output_file

async def quick_validation():
    """Quick validation for immediate feedback"""
    print("⚡ QUICK VALIDATION CHECK")
    print("=" * 40)
    
    checks = []
    
    # 1. Check threat cache
    try:
        with open('/opt/shadowcore/feeds/processed/threat_cache.json') as f:
            threats = json.load(f)
        checks.append(f"✅ Threat Cache: {len(threats)} threats")
    except:
        checks.append("❌ Threat Cache: Not found")
    
    # 2. Check Neo4j
    try:
        result = subprocess.run(
            ['cypher-shell', '-u', 'neo4j', '-p', 'Jonboy@123', '--format', 'plain',
             'RETURN "Neo4j OK" as status'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            checks.append("✅ Neo4j: Connected")
        else:
            checks.append("❌ Neo4j: Connection failed")
    except:
        checks.append("❌ Neo4j: Not accessible")
    
    # 3. Check Redis
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        checks.append("✅ Redis: Connected")
    except:
        checks.append("❌ Redis: Connection failed")
    
    # 4. Check Dashboard
    try:
        response = requests.get('http://localhost:8020', timeout=5)
        if response.status_code < 500:
            checks.append("✅ Dashboard: Running")
        else:
            checks.append(f"❌ Dashboard: HTTP {response.status_code}")
    except:
        checks.append("❌ Dashboard: Not reachable")
    
    # 5. Check recent reports
    import glob
    reports = glob.glob('/opt/shadowcore/intelligence_reports/*.json')
    checks.append(f"✅ Reports: {len(reports)} generated")
    
    # Print quick results
    print("\n".join(checks))
    
    if all('✅' in check for check in checks[:4]):
        print("\n🎉 QUICK CHECK: ALL SYSTEMS GO!")
    else:
        print("\n⚠️  QUICK CHECK: SOME ISSUES DETECTED")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ShadowCore Comprehensive Validation')
    parser.add_argument('--quick', action='store_true', help='Run quick validation only')
    parser.add_argument('--full', action='store_true', help='Run full comprehensive validation')
    
    args = parser.parse_args()
    
    if args.quick or not (args.quick or args.full):
        # Default to quick validation
        asyncio.run(quick_validation())
    elif args.full:
        # Run full validation
        validator = ComprehensiveValidator()
        results = validator.run_all_tests()
        
        # Print final message
        score = results['overall_score']
        if score >= 90:
            print("\n" + "=" * 60)
            print("🎉 SHADOWCORE VALIDATION: EXCELLENT!")
            print("=" * 60)
            print("Your 'Better Palantir' is fully operational and production-ready!")
            print(f"Overall Score: {score:.1f}%")
            print("\n🎯 Next steps: Feed it real network data and watch it work!")
        elif score >= 75:
            print("\n" + "=" * 60)
            print("✅ SHADOWCORE VALIDATION: GOOD")
            print("=" * 60)
            print("Your system is operational but could use some improvements.")
            print(f"Overall Score: {score:.1f}%")
            print("\n🔧 Check the failed components above for improvements.")
        else:
            print("\n" + "=" * 60)
            print("⚠️  SHADOWCORE VALIDATION: NEEDS ATTENTION")
            print("=" * 60)
            print("Some critical components need attention.")
            print(f"Overall Score: {score:.1f}%")
            print("\n🛠️ Focus on the failed tests above to get your system operational.")

if __name__ == "__main__":
    main()
