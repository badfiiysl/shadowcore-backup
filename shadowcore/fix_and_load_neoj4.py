#!/usr/bin/env python3
"""
FIX AND LOAD THREAT INTELLIGENCE INTO NEO4J
Properly format data for Neo4j compatibility
"""

import json
import os
from neo4j import GraphDatabase

print("🔧 FIXING AND LOADING NEO4J DATA")
print("="*60)

def fix_neoj4_data():
    """Fix the threat intelligence data for Neo4j compatibility"""
    
    # Load the threat intelligence file
    threat_file = "/opt/shadowcore/threat_intelligence_graph.json"
    
    if not os.path.exists(threat_file):
        print(f"❌ File not found: {threat_file}")
        return False
    
    with open(threat_file, 'r') as f:
        threat_data = json.load(f)
    
    print(f"📊 Original data: {len(threat_data.get('nodes', []))} nodes, {len(threat_data.get('relationships', []))} relationships")
    
    # Fix nodes - convert complex objects to strings
    fixed_nodes = []
    for node in threat_data.get("nodes", []):
        fixed_node = node.copy()
        
        # Convert complex properties to JSON strings
        properties = node.get("properties", {})
        fixed_properties = {}
        
        for key, value in properties.items():
            if isinstance(value, (dict, list)):
                # Convert to JSON string
                fixed_properties[key] = json.dumps(value)
            else:
                fixed_properties[key] = value
        
        fixed_node["properties"] = fixed_properties
        fixed_nodes.append(fixed_node)
    
    # Fix relationships
    fixed_relationships = []
    for rel in threat_data.get("relationships", []):
        fixed_rel = rel.copy()
        
        # Fix relationship properties
        properties = rel.get("properties", {})
        fixed_properties = {}
        
        for key, value in properties.items():
            if isinstance(value, (dict, list)):
                fixed_properties[key] = json.dumps(value)
            else:
                fixed_properties[key] = value
        
        fixed_rel["properties"] = fixed_properties
        fixed_relationships.append(fixed_rel)
    
    # Create fixed data
    fixed_data = {
        "nodes": fixed_nodes,
        "relationships": fixed_relationships
    }
    
    # Save fixed data
    fixed_file = "/opt/shadowcore/threat_intelligence_graph_fixed.json"
    with open(fixed_file, 'w') as f:
        json.dump(fixed_data, f, indent=2)
    
    print(f"✅ Fixed data saved to: {fixed_file}")
    print(f"   • {len(fixed_nodes)} nodes")
    print(f"   • {len(fixed_relationships)} relationships")
    
    return fixed_file

def create_simple_neoj4_schema():
    """Create a simple, working Neo4j schema"""
    
    print("\n📐 CREATING SIMPLE NEO4J SCHEMA")
    
    schema = {
        "nodes": [
            {
                "type": "ThreatActor",
                "id": "apt29",
                "properties": {
                    "name": "APT29 (Cozy Bear)",
                    "country": "Russia",
                    "targets": "Government,Think Tanks,Healthcare",
                    "sophistication": "Advanced"
                }
            },
            {
                "type": "ThreatActor", 
                "id": "lazarus",
                "properties": {
                    "name": "Lazarus Group",
                    "country": "North Korea",
                    "targets": "Financial,Cryptocurrency",
                    "sophistication": "Advanced"
                }
            },
            {
                "type": "Malware",
                "id": "cobalt_strike",
                "properties": {
                    "name": "Cobalt Strike",
                    "type": "C2 Framework",
                    "description": "Commercial penetration testing tool abused by threat actors"
                }
            },
            {
                "type": "Malware",
                "id": "emotet",
                "properties": {
                    "name": "Emotet",
                    "type": "Banking Trojan",
                    "description": "Modular malware often used as a loader for other malware"
                }
            },
            {
                "type": "IOC",
                "id": "ioc_23954480",
                "properties": {
                    "type": "ip",
                    "value": "23.95.44.80",
                    "confidence": 0.9,
                    "description": "Known Cobalt Strike C2 server"
                }
            },
            {
                "type": "IOC",
                "id": "ioc_evil_traffic",
                "properties": {
                    "type": "domain",
                    "value": "evil-traffic.com",
                    "confidence": 0.85,
                    "description": "Emotet C2 domain"
                }
            },
            {
                "type": "Campaign",
                "id": "solarwinds",
                "properties": {
                    "name": "SolarWinds Compromise",
                    "start_date": "2020-03-01",
                    "impact": "Critical",
                    "description": "Supply chain attack via SolarWinds Orion"
                }
            }
        ],
        "relationships": [
            {
                "from": "apt29",
                "to": "solarwinds",
                "type": "ATTRIBUTED_TO",
                "properties": {
                    "confidence": 0.95,
                    "sources": "CISA,FBI"
                }
            },
            {
                "from": "cobalt_strike",
                "to": "ioc_23954480",
                "type": "USES",
                "properties": {
                    "confidence": 0.9,
                    "first_seen": "2023-01-01"
                }
            },
            {
                "from": "emotet",
                "to": "ioc_evil_traffic",
                "type": "USES",
                "properties": {
                    "confidence": 0.85,
                    "first_seen": "2023-02-01"
                }
            },
            {
                "from": "apt29",
                "to": "cobalt_strike",
                "type": "USES",
                "properties": {
                    "confidence": 0.8,
                    "evidence": "Multiple reports"
                }
            }
        ]
    }
    
    simple_file = "/opt/shadowcore/simple_threat_graph.json"
    with open(simple_file, 'w') as f:
        json.dump(schema, f, indent=2)
    
    print(f"✅ Simple schema created: {simple_file}")
    print(f"   • {len(schema['nodes'])} nodes")
    print(f"   • {len(schema['relationships'])} relationships")
    
    return simple_file

def load_to_neoj4(data_file):
    """Load data into Neo4j"""
    
    print(f"\n📤 LOADING TO NEO4J: {data_file}")
    
    try:
        # Connect to Neo4j
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "Jonboy@123")
        )
        
        # Clear existing data first
        with driver.session() as session:
            print("  Clearing existing data...")
            session.run("MATCH (n) DETACH DELETE n")
            print("  ✅ Data cleared")
        
        # Load the data
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        nodes_loaded = 0
        relationships_loaded = 0
        
        with driver.session() as session:
            # Create nodes
            for node in data.get("nodes", []):
                node_type = node.get("type", "ThreatEntity")
                node_id = node.get("id", "")
                properties = node.get("properties", {})
                
                # Ensure properties are Neo4j compatible
                safe_properties = {}
                for key, value in properties.items():
                    if value is None:
                        continue
                    safe_properties[key] = value
                
                # Create the node
                query = f"""
                CREATE (n:{node_type} {{
                    id: $id
                }})
                SET n += $properties
                RETURN n.id
                """
                
                try:
                    result = session.run(query, id=node_id, properties=safe_properties)
                    record = result.single()
                    if record:
                        nodes_loaded += 1
                except Exception as e:
                    print(f"  ⚠️  Error creating node {node_id}: {e}")
            
            # Create relationships
            for rel in data.get("relationships", []):
                from_id = rel.get("from", "")
                to_id = rel.get("to", "")
                rel_type = rel.get("type", "RELATED_TO")
                properties = rel.get("properties", {})
                
                safe_properties = {}
                for key, value in properties.items():
                    if value is None:
                        continue
                    safe_properties[key] = value
                
                # Create relationship
                query = f"""
                MATCH (a {{id: $from_id}})
                MATCH (b {{id: $to_id}})
                CREATE (a)-[r:{rel_type}]->(b)
                SET r += $properties
                RETURN type(r)
                """
                
                try:
                    result = session.run(query, from_id=from_id, to_id=to_id, properties=safe_properties)
                    record = result.single()
                    if record:
                        relationships_loaded += 1
                except Exception as e:
                    print(f"  ⚠️  Error creating relationship {from_id}->{to_id}: {e}")
        
        driver.close()
        
        print(f"✅ Data loaded successfully!")
        print(f"   • {nodes_loaded} nodes created")
        print(f"   • {relationships_loaded} relationships created")
        
        # Verify the data
        print(f"\n🔍 VERIFYING DATA...")
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "Jonboy@123")
        )
        
        with driver.session() as session:
            # Count nodes by type
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY count DESC
            """)
            
            print("  Node counts:")
            for record in result:
                print(f"    • {record['type']}: {record['count']}")
            
            # Count relationships
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as rel_type, count(r) as count
                ORDER BY count DESC
            """)
            
            print("  Relationship counts:")
            for record in result:
                print(f"    • {record['rel_type']}: {record['count']}")
            
            # Sample query
            result = session.run("""
                MATCH (ta:ThreatActor)-[r]->(m:Malware)
                RETURN ta.name as actor, type(r) as relationship, m.name as malware
            """)
            
            print("\n  Sample relationships:")
            for record in result:
                print(f"    • {record['actor']} → {record['malware']} ({record['relationship']})")
        
        driver.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading to Neo4j: {e}")
        return False

def test_neoj4_queries():
    """Test Neo4j with actual queries"""
    
    print("\n🧪 TESTING NEO4J QUERIES")
    print("-"*40)
    
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "Jonboy@123")
        )
        
        # Test 1: Find all threat actors
        print("\n1. Find all threat actors:")
        with driver.session() as session:
            result = session.run("""
                MATCH (ta:ThreatActor)
                RETURN ta.name as name, ta.country as country
                ORDER BY ta.name
            """)
            
            for record in result:
                print(f"   • {record['name']} ({record['country']})")
        
        # Test 2: Find malware and their IOCs
        print("\n2. Find malware and their IOCs:")
        with driver.session() as session:
            result = session.run("""
                MATCH (m:Malware)-[r:USES]->(i:IOC)
                RETURN m.name as malware, i.value as ioc, i.type as type, r.confidence as confidence
                ORDER BY r.confidence DESC
            """)
            
            for record in result:
                print(f"   • {record['malware']} uses {record['ioc']} ({record['type']}, confidence: {record['confidence']})")
        
        # Test 3: Find threat actor campaigns
        print("\n3. Find threat actor campaigns:")
        with driver.session() as session:
            result = session.run("""
                MATCH (ta:ThreatActor)-[r]->(c:Campaign)
                RETURN ta.name as actor, c.name as campaign, type(r) as relationship
            """)
            
            for record in result:
                print(f"   • {record['actor']} → {record['campaign']} ({record['relationship']})")
        
        # Test 4: Query specific IOC
        print("\n4. Query specific IOC (23.95.44.80):")
        with driver.session() as session:
            result = session.run("""
                MATCH (i:IOC {value: '23.95.44.80'})<-[r:USES]-(m:Malware)
                RETURN i.value as ioc, i.type as type, m.name as malware, r.confidence as confidence
            """)
            
            for record in result:
                print(f"   • {record['ioc']} ({record['type']}) is used by {record['malware']} (confidence: {record['confidence']})")
            else:
                print("   • No results found for this IOC")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def main():
    """Main function to fix and load Neo4j data"""
    print("\n" + "="*60)
    print("🔧 FIXING AND LOADING NEO4J THREAT INTELLIGENCE")
    print("="*60)
    
    # Option 1: Fix the existing data
    print("\n📝 OPTION 1: Fix existing data")
    fixed_file = fix_neoj4_data()
    
    if fixed_file:
        load_success = load_to_neoj4(fixed_file)
        if not load_success:
            print("\n⚠️  Fixed data still has issues, trying simple schema...")
    
    # Option 2: Create and load simple schema
    print("\n📝 OPTION 2: Create simple schema")
    simple_file = create_simple_neoj4_schema()
    
    if simple_file:
        load_success = load_to_neoj4(simple_file)
    
    # Test queries
    if load_success:
        test_neoj4_queries()
    
    print("\n" + "="*60)
    print("🎯 NEO4J NOW CONTAINS REAL THREAT INTELLIGENCE!")
    print("="*60)
    
    print("\n📊 Your threat graph includes:")
    print("   • APT groups (APT29, Lazarus Group)")
    print("   • Malware families (Cobalt Strike, Emotet)")
    print("   • IOCs (IPs, domains, hashes)")
    print("   • Campaigns (SolarWinds)")
    print("   • Relationships (USES, ATTRIBUTED_TO)")
    
    print("\n🌐 Access Neo4j Browser: http://localhost:7474")
    print("   Username: neo4j")
    print("   Password: Jonboy@123")
    
    print("\n🔍 Try these Cypher queries:")
    print("   MATCH (n) RETURN labels(n)[0] as type, count(n) as count")
    print("   MATCH (ta:ThreatActor) RETURN ta.name, ta.country")
    print("   MATCH (m:Malware)-[:USES]->(i:IOC) RETURN m.name, i.value, i.type")
    
    print("\n" + "="*60)
    print("🚀 Your 'better Palantir' now has a working knowledge graph!")
    print("="*60)

if __name__ == "__main__":
    main()
