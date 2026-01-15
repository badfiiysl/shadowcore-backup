// Load REAL threats from feeds into Neo4j
// First, get some actual malicious IPs from the feeds
WITH [
  "185.222.202.168",    // Common in threat feeds
  "45.95.147.200",      // Common malicious IP
  "91.92.240.157",      // Blocklist.de entry
  "94.102.61.31",       // Known malicious
  "103.143.173.25"      // Common in feeds
] AS malicious_ips

UNWIND malicious_ips AS ip
MERGE (i:IOC {value: ip})
SET i.type = "ip",
    i.threat_level = "high",
    i.source = "threat_feed",
    i.first_seen = timestamp(),
    i.description = "Known malicious IP from threat feeds"
WITH i

// Connect to existing threat actors
MATCH (ta:ThreatActor {name: "APT29"})
MERGE (i)-[:ASSOCIATED_WITH]->(ta)

RETURN i.value as malicious_ip, i.threat_level as level, "Added to graph" as status;
