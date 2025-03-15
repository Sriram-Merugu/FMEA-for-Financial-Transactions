from neo4j import GraphDatabase

def run_fmea(driver, threshold=30):
    """
    For each Transaction node, compute FMEA factors:
      - Severity: Based on how high the transaction amount is relative to global statistics.
      - Occurrence: Approximated by (number of SIMILAR relationships + 1), capped at 10.
      - Detection: A constant (5).
    Then compute RPN (severity * occurrence * detection) and flag as "High Risk" if RPN >= threshold.
    """
    # Compute global statistics for Transaction_Amount
    stats_query = """
    MATCH (t:Transaction)
    RETURN avg(t.Transaction_Amount) as avg_amt, stDev(t.Transaction_Amount) as std_amt
    """
    with driver.session() as session:
        result = session.run(stats_query)
        record = result.single()
        avg_amt = record["avg_amt"]
        std_amt = record["std_amt"]

    print("Global stats: Average Amount =", avg_amt, ", Std Dev =", std_amt)

    # FMEA query to compute and update each Transaction node with FMEA factors and failure_mode
    fmea_query = """
    MATCH (t:Transaction)
    OPTIONAL MATCH (t)-[r:SIMILAR]->()
    WITH t, count(r) as sim_count, $avg_amt as avg_amt, $std_amt as std_amt
    WITH t, sim_count, avg_amt, std_amt,
         CASE 
           WHEN t.Transaction_Amount > avg_amt + 2 * std_amt THEN 10
           WHEN t.Transaction_Amount > avg_amt + std_amt THEN 7
           ELSE 3
         END as severity
    WITH t, sim_count, severity,
         CASE WHEN sim_count + 1 > 10 THEN 10 ELSE sim_count + 1 END as occurrence,
         5 as detection,
         severity * (CASE WHEN sim_count + 1 > 10 THEN 10 ELSE sim_count + 1 END) * 5 as RPN
    SET t.severity = severity,
        t.occurrence = CASE WHEN sim_count + 1 > 10 THEN 10 ELSE sim_count + 1 END,
        t.detection = 5,
        t.RPN = RPN,
        t.failure_mode = CASE WHEN RPN >= $threshold THEN "High Risk" ELSE "Normal" END
    RETURN t.Transaction_ID as Transaction_ID, t.RPN as RPN, t.failure_mode as failure_mode
    """
    with driver.session() as session:
        result = session.run(fmea_query, avg_amt=avg_amt, std_amt=std_amt, threshold=threshold)
        print("FMEA analysis results:")
        for record in result:
            print(f"Transaction {record['Transaction_ID']}: RPN = {record['RPN']}, Mode = {record['failure_mode']}")

def main():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"  # Update with your Neo4j password
    driver = GraphDatabase.driver(uri, auth=(user, password))
    run_fmea(driver, threshold=30)  # Adjust threshold as needed
    driver.close()

if __name__ == "__main__":
    main()
