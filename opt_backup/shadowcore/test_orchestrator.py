#!/usr/bin/env python3
"""
Simple test of the orchestrator
"""

import asyncio
import sys
sys.path.insert(0, '/opt/shadowcore')

# Import and run a quick test
async def quick_test():
    print("🧪 Quick orchestrator test...")
    
    try:
        # Try to import
        from orchestrator import ShadowCoreOrchestrator
        
        # Create instance
        orchestrator = ShadowCoreOrchestrator()
        
        # Quick health check
        await orchestrator.health_check()
        
        # Process one IOC
        print("\n🔍 Testing with one IOC: 192.168.1.100")
        results = await orchestrator.process_threat_ioc("192.168.1.100")
        
        print(f"✅ Test successful!")
        print(f"Threat Level: {results['report']['threat_level']}")
        print(f"Report ID: {results['report']['report_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    if success:
        print("\n🎉 Orchestrator is working!")
        print("Run the full orchestrator: python3 /opt/shadowcore/orchestrator.py")
    else:
        print("\n⚠️  Orchestrator needs debugging")
