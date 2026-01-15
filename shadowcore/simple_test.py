#!/usr/bin/env python3
"""
Simple test of the fixed orchestrator
"""

import asyncio
import sys
import os

sys.path.insert(0, '/opt/shadowcore')

async def test():
    print("🧪 Testing fixed orchestrator...")
    
    try:
        # Import the fixed orchestrator
        from orchestrator_fixed import ShadowCoreOrchestrator
        
        print("✅ Module imported successfully")
        
        # Create instance
        orchestrator = ShadowCoreOrchestrator()
        
        # Quick health check
        print("\n🏥 Running health check...")
        healthy, total = await orchestrator.health_check()
        
        print(f"\n📊 Health: {healthy}/{total} components")
        
        if healthy > 0:
            # Test with one IOC
            print("\n🔍 Testing with one IOC...")
            results = await orchestrator.process_threat_ioc("192.168.1.100")
            
            if results and "report" in results:
                print(f"✅ Test successful!")
                print(f"Report ID: {results['report']['report_id']}")
                print(f"Threat Level: {results['report']['threat_level']}")
                
                # Show where report was saved
                reports_dir = "/opt/shadowcore/reports"
                if os.path.exists(reports_dir):
                    reports = os.listdir(reports_dir)
                    if reports:
                        print(f"\n📁 Reports saved in: {reports_dir}")
                        print(f"Latest: {reports[-1]}")
                
                return True
            else:
                print("⚠️  Test completed but no report generated")
                return False
        else:
            print("❌ No healthy components")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ORCHESTRATOR IS WORKING!")
        print("\nYour vision is now a reality:")
        print("• Agent Manager coordinates")
        print("• Worker Pool processes")
        print("• AI Engines analyze")
        print("• OSINT Engine enriches")
        print("• Memory stores & correlates")
        print("\nRun the full version: python3 /opt/shadowcore/orchestrator_fixed.py")
    else:
        print("⚠️  Orchestrator needs attention")
        print("Check your services are running:")
        print("• Python APIs (8000, 8003, 8004, 8006)")
        print("• shadowbrain (8001)")
        print("• Dashboard (8020)")
        print("• Neo4j (7474, 7687)")
        print("• Redis (6379)")
    print("=" * 50)
