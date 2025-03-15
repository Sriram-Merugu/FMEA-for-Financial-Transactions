import pandas as pd
import numpy as np
from neo4j import GraphDatabase
from datetime import datetime

def load_data(csv_path: str) -> pd.DataFrame:
    """
    Load the CSV file, perform data cleaning and transformation:
      - Drop unnecessary columns.
      - Convert Transaction_Date and Transaction_Time into numeric components.
      - Create a unified timestamp column and generate a unique Transaction_ID.
    """
    df = pd.read_csv(csv_path)

    # Drop columns not needed for analysis or privacy reasons
    df.drop(columns=['Customer_ID', 'Merchant_ID', 'Transaction_ID', 'Customer_Email', 'Customer_Contact',
                     'Transaction_Description'], inplace=True, axis=1)

    # Convert Transaction_Date to separate year, month, day columns
    df['year'] = pd.to_datetime(df['Transaction_Date'], dayfirst=True).dt.year
    df['month'] = pd.to_datetime(df['Transaction_Date'], dayfirst=True).dt.month
    df['day'] = pd.to_datetime(df['Transaction_Date'], dayfirst=True).dt.day

    # Convert Transaction_Time to hour, minute, second columns
    df['hour'] = pd.to_datetime(df['Transaction_Time'], format='%H:%M:%S').dt.hour
    df['minute'] = pd.to_datetime(df['Transaction_Time'], format='%H:%M:%S').dt.minute
    df['second'] = pd.to_datetime(df['Transaction_Time'], format='%H:%M:%S').dt.second

    # Drop original date/time and other unneeded columns
    df.drop(columns=['Transaction_Date', 'Transaction_Time'], inplace=True)
    df.drop(columns=['Transaction_Currency'], inplace=True, axis=1)
    df.drop(columns=['Customer_Name'], inplace=True, axis=1)

    # Create a unified timestamp column from the numeric date/time columns
    df['timestamp'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])
    df['timestamp_str'] = df['timestamp'].apply(lambda x: x.isoformat())

    # Generate a unique Transaction_ID using the row index
    df['Transaction_ID'] = df.index.astype(str)

    # For testing, we'll use only the first 1000 rows
    return df[:1000]

def create_transaction_nodes(driver, df: pd.DataFrame):
    """
    Create Transaction nodes in Neo4j using the cleaned CSV data.
    """
    query = """
    UNWIND $data as row
    CREATE (t:Transaction {
      Transaction_ID: row.Transaction_ID,
      Gender: row.Gender,
      Age: row.Age,
      State: row.State,
      City: row.City,
      Bank_Branch: row.Bank_Branch,
      Account_Type: row.Account_Type,
      Transaction_Amount: row.Transaction_Amount,
      Transaction_Type: row.Transaction_Type,
      Merchant_Category: row.Merchant_Category,
      Account_Balance: row.Account_Balance,
      Transaction_Device: row.Transaction_Device,
      Transaction_Location: row.Transaction_Location,
      Device_Type: row.Device_Type,
      Is_Fraud: row.Is_Fraud,
      timestamp: row.timestamp_str
    })
    """
    data = df.to_dict('records')
    with driver.session() as session:
        session.run(query, data=data)
    print("Transaction nodes created.")

def create_next_relationships(driver):
    """
    Create NEXT relationships between transactions ordered by timestamp.
    """
    query = """
    MATCH (t:Transaction)
    WITH t ORDER BY t.timestamp
    WITH collect(t) as txs
    UNWIND range(0, size(txs)-2) as idx
    WITH txs[idx] as t1, txs[idx+1] as t2
    CREATE (t1)-[:NEXT {time_diff: duration.inSeconds(datetime(t1.timestamp), datetime(t2.timestamp)).seconds}]->(t2)
    """
    with driver.session() as session:
        session.run(query)
    print("NEXT relationships created.")

def create_similar_relationships(driver):
    """
    Create SIMILAR relationships between transactions that share:
      - The same Transaction_Type,
      - Similar Transaction_Amount (within 10%),
      - And occur within one hour of each other.
    """
    query = """
    MATCH (t1:Transaction), (t2:Transaction)
    WHERE t1.Transaction_ID <> t2.Transaction_ID
      AND t1.Transaction_Type = t2.Transaction_Type
      AND abs(t1.Transaction_Amount - t2.Transaction_Amount) < 0.1 * t1.Transaction_Amount
      AND abs(duration.inSeconds(datetime(t1.timestamp), datetime(t2.timestamp)).seconds) < 3600
    CREATE (t1)-[:SIMILAR]->(t2)
    """
    with driver.session() as session:
        session.run(query)
    print("SIMILAR relationships created.")

def main():
    CSV_PATH = "assets/Bank_Transaction_Fraud_Detection.csv"  # Update with your CSV file path
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"  # Update with your Neo4j password

    driver = GraphDatabase.driver(uri, auth=(user, password))
    df = load_data(CSV_PATH)
    print("Data loaded. Number of transactions:", len(df))
    create_transaction_nodes(driver, df)
    create_next_relationships(driver)
    create_similar_relationships(driver)
    driver.close()

if __name__ == "__main__":
    main()
