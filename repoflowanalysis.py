import os
import re
import sys
import csv
import argparse
from pathlib import Path

# =====================================================
# Argument Parser (CLI)
# =====================================================
parser = argparse.ArgumentParser(
    description="Enterprise Spring Boot Repo Analyzer (Kafka, DB, Elasticsearch, Cassandra, REST, Flows)"
)

parser.add_argument(
    "--repo",
    required=True,
    help="Path to local Git repository"
)

parser.add_argument(
    "--out",
    default="repo-analysis-output",
    help="Output directory name (default: repo-analysis-output)"
)

parser.add_argument(
    "--no-md",
    action="store_true",
    help="Skip summary.md generation"
)

args = parser.parse_args()

REPO_ROOT = Path(args.repo).resolve()
if not REPO_ROOT.exists():
    print(f"❌ Invalid repo path: {REPO_ROOT}")
    sys.exit(1)

OUTPUT_DIR = REPO_ROOT / args.out
OUTPUT_DIR.mkdir(exist_ok=True)

# =====================================================
# Containers
# =====================================================
services = []
kafka = []
databases = []
flows = []

# =====================================================
# Regex Patterns
# =====================================================

# -------- Spring --------
REST_CONTROLLER = re.compile(r"@RestController")
SERVICE_ANNOTATION = re.compile(r"@(Service|Component)")
REQUEST_MAPPING = re.compile(
    r"@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\s*\(\"([^\"]*)\""
)

# -------- Kafka --------
WALMART_KAFKA_LISTENER = re.compile(
    r"@WalmartKafkaListener\s*\((.*?)\)",
    re.DOTALL
)

SPRING_KAFKA_LISTENER = re.compile(
    r"@KafkaListener\s*\((.*?)\)",
    re.DOTALL
)

TOPIC_EXTRACTOR = re.compile(
    r"topics\s*=\s*\{?\"([^\"]+)\""
)

KAFKA_TEMPLATE_SEND = re.compile(
    r"\b(\w*KafkaTemplate)\s*\.\s*send\s*\(",
    re.DOTALL
)

# -------- JDBC Databases --------
JDBC_TEMPLATE = re.compile(
    r"(JdbcTemplate|NamedParameterJdbcTemplate)"
)

SQL_OPERATION = re.compile(
    r"\b(SELECT|INSERT|UPDATE|DELETE)\b",
    re.IGNORECASE
)

TABLE_EXTRACTOR = re.compile(
    r"\bFROM\s+([A-Z0-9_\.]+)|"
    r"\bINTO\s+([A-Z0-9_\.]+)|"
    r"\bUPDATE\s+([A-Z0-9_\.]+)",
    re.IGNORECASE
)

# -------- Elasticsearch --------
ELASTIC_CLIENT = re.compile(
    r"(RestHighLevelClient|ElasticsearchClient|ElasticsearchOperations)"
)

ELASTIC_INDEX = re.compile(
    r"@Document\s*\(\s*indexName\s*=\s*\"([^\"]+)\""
)

ELASTIC_OPERATION = re.compile(
    r"(IndexRequest|UpdateRequest|DeleteRequest|SearchRequest)"
)

# -------- Cassandra --------
CASSANDRA_DRIVER = re.compile(
    r"com\.datastax\.oss\.driver\.api",
    re.IGNORECASE
)

CASSANDRA_QUERY_BUILDER = re.compile(
    r"QueryBuilder\.(insertInto|selectFrom|update|deleteFrom)",
    re.IGNORECASE
)

CASSANDRA_TABLE = re.compile(
    r"insertInto\s*\(\s*\"([^\"]+)\"|"
    r"from\s*\(\s*\"([^\"]+)\"",
    re.IGNORECASE
)

# -------- DB Type Detection --------
DB_TYPE_RULES = {
    "DB2": ["db2", "jdbc:db2", "com.ibm.db2"],
    "PostgreSQL": ["postgres", "jdbc:postgresql", "org.postgresql"],
    "AzureSQL": ["azure", "jdbc:sqlserver", "com.microsoft.sqlserver"],
    "Cassandra": ["com.datastax", "Cluster", "Session"]
}

def detect_db_type(content, file_path):
    combined = (content + " " + str(file_path)).lower()
    for db, indicators in DB_TYPE_RULES.items():
        for ind in indicators:
            if ind in combined:
                return db
    return "Unknown"

# =====================================================
# Scan Repo and Correlate Flows
# =====================================================
for root, _, files in os.walk(REPO_ROOT):
    for file in files:
        if not file.endswith(".java"):
            continue

        java_file = Path(root) / file
        content = java_file.read_text(encoding="utf-8", errors="ignore")

        # ---------------- REST Controllers ----------------
        if REST_CONTROLLER.search(content):
            endpoints = [m[1] for m in REQUEST_MAPPING.findall(content)]
            services.append({
                "File": str(java_file),
                "Type": "REST Controller",
                "Endpoints": ", ".join(endpoints) if endpoints else "Base mapping"
            })
            flows.append({"From": "Client", "To": "REST Controller", "Type": "Sync", "File": str(java_file)})

        elif SERVICE_ANNOTATION.search(content):
            services.append({
                "File": str(java_file),
                "Type": "Spring Service",
                "Endpoints": "N/A"
            })

        # ---------------- Kafka Consumers ----------------
        for block in WALMART_KAFKA_LISTENER.findall(content):
            topic = TOPIC_EXTRACTOR.search(block)
            kafka.append({
                "File": str(java_file),
                "Topic": topic.group(1) if topic else "Unknown",
                "Direction": "Consume",
                "Implementation": "WalmartKafkaListener"
            })
            flows.append({"From": "Kafka", "To": "Service", "Type": "Async", "File": str(java_file)})

        for block in SPRING_KAFKA_LISTENER.findall(content):
            topic = TOPIC_EXTRACTOR.search(block)
            kafka.append({
                "File": str(java_file),
                "Topic": topic.group(1) if topic else "Pattern/Unknown",
                "Direction": "Consume",
                "Implementation": "KafkaListener"
            })
            flows.append({"From": "Kafka", "To": "Service", "Type": "Async", "File": str(java_file)})

        # ---------------- Kafka Producers ----------------
        if KAFKA_TEMPLATE_SEND.search(content):
            kafka.append({
                "File": str(java_file),
                "Topic": "Resolved at runtime",
                "Direction": "Produce",
                "Implementation": "KafkaTemplate"
            })
            flows.append({"From": "Service", "To": "Kafka", "Type": "Async", "File": str(java_file)})

        # ---------------- JDBC Databases ----------------
        if JDBC_TEMPLATE.search(content):
            ops = set(SQL_OPERATION.findall(content))
            tables = {t for g in TABLE_EXTRACTOR.findall(content) for t in g if t}
            access = "Read/Write" if {"INSERT","UPDATE","DELETE"} & ops else "Read"

            databases.append({
                "File": str(java_file),
                "DB_Type": detect_db_type(content, java_file),
                "Access": access,
                "Tables": ", ".join(sorted(tables)) if tables else "Unable to resolve"
            })
            flows.append({"From": "Service", "To": "Database", "Type": "Sync", "File": str(java_file)})

        # ---------------- Elasticsearch ----------------
        if ELASTIC_CLIENT.search(content) or ELASTIC_INDEX.search(content):
            indices = ELASTIC_INDEX.findall(content)
            ops = ELASTIC_OPERATION.findall(content)
            access = "Read/Write" if {"IndexRequest","UpdateRequest","DeleteRequest"} & set(ops) else "Read"

            databases.append({
                "File": str(java_file),
                "DB_Type": "Elasticsearch",
                "Access": access,
                "Tables": ", ".join(indices) if indices else "Index resolved at runtime"
            })
            flows.append({"From": "Service", "To": "Elasticsearch", "Type": "Sync", "File": str(java_file)})

        # ---------------- Cassandra ----------------
        if CASSANDRA_DRIVER.search(content):
            ops = set()
            if re.search(r"insertInto", content, re.IGNORECASE):
                ops.add("INSERT")
            if re.search(r"selectFrom", content, re.IGNORECASE):
                ops.add("SELECT")
            if re.search(r"update", content, re.IGNORECASE):
                ops.add("UPDATE")
            if re.search(r"deleteFrom", content, re.IGNORECASE):
                ops.add("DELETE")

            tables = set()
            for match in CASSANDRA_TABLE.findall(content):
                for t in match:
                    if t:
                        tables.add(t)

            access = "Read"
            if {"INSERT", "UPDATE", "DELETE"} & ops:
                access = "Read/Write"

            databases.append({
                "File": str(java_file),
                "DB_Type": "Cassandra",
                "Access": access,
                "Tables": ", ".join(sorted(tables)) if tables else "Resolved at runtime"
            })

            flows.append({"From": "Service", "To": "Cassandra", "Type": "Sync", "File": str(java_file)})

# =====================================================
# CSV Writer
# =====================================================
def write_csv(name, rows, headers):
    with open(OUTPUT_DIR / name, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

write_csv("services.csv", services, ["File","Type","Endpoints"])
write_csv("kafka.csv", kafka, ["File","Topic","Direction","Implementation"])
write_csv("database.csv", databases, ["File","DB_Type","Access","Tables"])
write_csv("flow.csv", flows, ["From","To","Type","File"])

# =====================================================
# summary.md
# =====================================================
if not args.no_md:
    with open(OUTPUT_DIR / "summary.md", "w", encoding="utf-8") as f:
        f.write("# Repo Analysis Summary\n\n")

        f.write("## REST Controllers\n")
        for s in services:
            if s["Type"] == "REST Controller":
                f.write(f"- {s['File']} → {s['Endpoints']}\n")

        f.write("\n## Kafka\n")
        for k in kafka:
            f.write(f"- {k['Direction']} → {k['Topic']} ({k['Implementation']}) [{k['File']}]\n")

        f.write("\n## Databases\n")
        for d in databases:
            f.write(f"- {d['DB_Type']} | {d['Access']} | {d['Tables']} ({d['File']})\n")

        f.write("\n## Flows\n")
        for fl in flows:
            f.write(f"- {fl['From']} → {fl['To']} ({fl['Type']}) [{fl['File']}]\n")

# =====================================================
# Done
# =====================================================
print("Repo analysis completed successfully")
print(f"Output available at: {OUTPUT_DIR}")
