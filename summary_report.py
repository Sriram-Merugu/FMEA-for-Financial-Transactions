# summary_report.py

from neo4j import GraphDatabase


def get_summary_report(driver):
    """
    Query Neo4j to obtain summary statistics from the Transaction nodes.
    Returns:
      - total: Total number of transactions.
      - highRisk: Count of transactions flagged as "High Risk".
      - avgRPN: Average Risk Priority Number.
      - minRPN: Minimum RPN.
      - maxRPN: Maximum RPN.
    """
    query = """
    MATCH (t:Transaction)
    RETURN count(t) as total,
           sum(CASE WHEN t.failure_mode = "High Risk" THEN 1 ELSE 0 END) as highRisk,
           avg(t.RPN) as avgRPN,
           min(t.RPN) as minRPN,
           max(t.RPN) as maxRPN
    """
    with driver.session() as session:
        result = session.run(query)
        record = result.single()
        return record


def main():
    uri = input("Enter Neo4j URI (e.g., bolt://localhost:7687): ")
    user = input("Enter Neo4j username: ")
    password = input("Enter Neo4j password: ")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    summary = get_summary_report(driver)
    if summary:
        print("FMEA Summary Report:")
        print(f"Total Transactions: {summary['total']}")
        print(f"High Risk Transactions: {summary['highRisk']}")
        print(f"Average RPN: {summary['avgRPN']:.2f}")
        print(f"Minimum RPN: {summary['minRPN']:.2f}")
        print(f"Maximum RPN: {summary['maxRPN']:.2f}")
    else:
        print("No summary data found.")
    driver.close()


if __name__ == "__main__":
    main()
