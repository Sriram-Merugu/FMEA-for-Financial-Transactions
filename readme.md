Below is the updated `README.md` file reflecting that all non-code files are located in the `assets/` folder:

---

# FMEA for Financial Transactions using Neo4j and Streamlit

## Overview
This project implements a Failure Mode and Effects Analysis (FMEA) system for financial transactions using a graph-based approach. The system collects historical transaction data from a CSV file (downloadable from [Kaggle](https://www.kaggle.com/datasets/marusagar/bank-transaction-fraud-detection)), constructs a graph in a local Neo4j database, performs FMEA to identify potential failure modes, and visualizes the results interactively using Streamlit and Plotly.


1. **Data Collection:**  
   - Collect historical financial transaction data from a CSV file (located in `assets/Bank_Transaction_Fraud_Detection.csv`).  
   - The CSV file is sourced from Kaggle (download the full dataset from [here](https://www.kaggle.com/datasets/marusagar/bank-transaction-fraud-detection)).

2. **Graph Construction:**  
   - Use the script `graph_construction.py` to clean the CSV data, transform date/time fields, and load transaction nodes into a local Neo4j database.  
   - Construct a graph where each node represents a transaction enriched with attributes (e.g., transaction amount, type, timestamp) and edges represent relationships (such as consecutive transactions via `NEXT` and similar transactions via `SIMILAR`).

3. **FMEA Implementation:**  
   - Implement an FMEA algorithm using `fmea_implementation.py` that computes FMEA factors—**severity**, **occurrence**, and **detection**—for each transaction.  
   - Calculate a Risk Priority Number (RPN) for every transaction and flag potential failure modes based on a set threshold.

4. **Visualization and Reporting:**  
   - Utilize interactive visualizations with Plotly and Streamlit (via `app.py`, `view_fmea_implementation.py`, and `view_original_graph.py`) to display:
     - Pre-generated graph snapshots (e.g., `original_graph.png`, `failure_mode_graph.png`) and HTML snapshots (`original_graph.html`, `transaction_graph.html`).
     - An interactive Streamlit interface that shows the original and FMEA-enhanced transaction graphs.
     - A summary report (generated with `summary_report.py`) highlighting key metrics such as total transactions, number of high-risk transactions, average RPN, minimum RPN, and maximum RPN.




## Repository Structure

```
.
├── app.py                          # Streamlit app for data cleaning, interactive visualization, and FMEA summary report.
├── fmea_implementation.py          # Code for FMEA analysis on the transaction graph in Neo4j.
├── graph_construction.py           # Code for constructing the transaction graph in Neo4j from the CSV data.
├── summary_report.py               # Script for generating a summary report (FMEA statistics) from Neo4j.
├── view_fmea_implementation.py     # (Optional) Code to interactively view FMEA results.
├── view_original_graph.py          # (Optional) Code to interactively view the original transaction graph.
└── assets
    ├── Bank_Transaction_Fraud_Detection.csv   # CSV file (partial dataset; download full dataset from Kaggle).
    ├── failure_mode_graph.png                   # Snapshot image of the failure mode graph.
    ├── original_graph.html                      # HTML snapshot of the original transaction graph.
    ├── original_graph.png                       # Snapshot image of the original transaction graph.
    └── transaction_graph.html                   # HTML snapshot of the transaction graph with FMEA highlights.
```

## Tools and Libraries
- **Python 3.x**
- **Neo4j:** Graph database (using the Neo4j Python driver)
- **Pandas & NumPy:** Data manipulation and analysis
- **Streamlit:** Interactive web app framework
- **Plotly & Plotly Express:** Interactive visualizations
- **NetworkX:** Graph construction and analysis
- **Pillow (PIL):** Image processing

## Setup and Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Sriram-Merugu/FMEA-for-Financial-Transactions
   cd FMEA-for-Financial-Transactions
   ```

2. **Create a Virtual Environment and Install Dependencies:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   pip install -r requirements.txt
   ```


3. **Set Up Neo4j:**
   - Install Neo4j Desktop or use a Docker container.
   - Create and start a database.
   - Update the connection details (`uri`, `user`, `password`) in the code files as needed.

4. **Data:**
   - The CSV file is located in the `assets/` folder.
   - For full analysis, download the complete CSV from [Kaggle](https://www.kaggle.com/datasets/marusagar/bank-transaction-fraud-detection) and replace or update the file path in the code accordingly.

## How to Run

1. **Graph Construction:**
   - Populate Neo4j with the transaction graph by running:
     ```bash
     python graph_construction.py
     ```

2. **FMEA Implementation:**
   - Update the transaction nodes with FMEA metrics by running:
     ```bash
     python fmea_implementation.py
     ```

3. **Summary Report:**
   - Generate a textual summary report by running:
     ```bash
     python summary_report.py
     ```

4. **Interactive Visualization:**
   - Launch the Streamlit app to view interactive visualizations and the FMEA summary report:
     ```bash
     streamlit run app.py
     ```
   - Optional dedicated visualization apps are available:
     - `view_fmea_implementation.py` for viewing FMEA results.
     - `view_original_graph.py` for viewing the original transaction graph.

## Report Summary
The FMEA summary report includes key metrics such as:
- **Total Transactions:** 2000
- **High Risk Transactions:** 442
- **Average RPN:** 20.51
- **Minimum RPN:** 15.00
- **Maximum RPN:** 140.00

These metrics help identify potential failure modes in transactions, facilitating further investigation into fraudulent activities.

## Conclusion
This project demonstrates how to leverage a graph database and FMEA techniques to analyze financial transactions for fraud detection. Interactive visualizations and detailed reports provide actionable insights into transaction behavior and highlight potential vulnerabilities.


## Acknowledgements
- **Dataset:** [Bank Transaction Fraud Detection on Kaggle](https://www.kaggle.com/datasets/marusagar/bank-transaction-fraud-detection)
- Thanks to the open-source community for providing the tools and libraries used in this project.

---
