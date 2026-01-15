// Load threats from feeds into Neo4j

MERGE (i:IOC {value: ""first_seen_utc","dst_ip","dst_port","c2_status","last_online","malware""})
SET i.type = "ip",
    i.source = "feodotracker",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984582"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: ""2022-06-04 21:24:53","162.243.103.246","8080","offline","2026-01-04","Emotet""})
SET i.type = "ip",
    i.source = "feodotracker",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984590"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: ""2022-06-13 22:31:59","167.86.75.145","443","offline","2026-01-05","Emotet""})
SET i.type = "ip",
    i.source = "feodotracker",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984592"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: ""2025-09-13 14:31:12","137.184.9.29","443","offline","2026-01-04","QakBot""})
SET i.type = "ip",
    i.source = "feodotracker",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984593"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: ""2025-12-30 13:56:31","50.16.16.211","443","offline","2025-12-31","QakBot""})
SET i.type = "ip",
    i.source = "feodotracker",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984594"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.14.12.141"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984594"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.145.90.220"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984596"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.159.145.162"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984597"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.161.39.103"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984598"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.180.62.41"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984599"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.183.3.58"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984599"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.193.163.2"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984600"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.194.236.11"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984601"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.196.177.49"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984602"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.197.102.62"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984603"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.203.97.79"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984604"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.212.225.99"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984605"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.214.197.163"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984605"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.214.42.172"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984606"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;

MERGE (i:IOC {value: "1.227.228.131"})
SET i.type = "ip",
    i.source = "blocklist_de",
    i.threat_level = "high",
    i.first_seen = "2026-01-12T03:39:51.984607"
WITH i
MATCH (m:Malware {name: "Cobalt Strike"})
MERGE (i)-[:ASSOCIATED_WITH]->(m)
RETURN i.value as threat_ip, m.name as malware;
