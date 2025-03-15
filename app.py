import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from PIL import Image
import plotly.express as px


# -------------------- Data Cleaning Section --------------------
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the CSV data by:
      - Dropping unnecessary columns.
      - Converting Transaction_Date and Transaction_Time into separate numerical components.
    """
    # Remove columns not needed for analysis or to preserve privacy
    df.drop(columns=['Customer_ID', 'Merchant_ID', 'Transaction_ID',
                     'Customer_Email', 'Customer_Contact', 'Transaction_Description'],
            inplace=True, axis=1)

    # Extract year, month, and day from Transaction_Date
    df['year'] = pd.to_datetime(df['Transaction_Date'], dayfirst=True).dt.year
    df['month'] = pd.to_datetime(df['Transaction_Date'], dayfirst=True).dt.month
    df['day'] = pd.to_datetime(df['Transaction_Date'], dayfirst=True).dt.day

    # Extract hour, minute, and second from Transaction_Time
    df['hour'] = pd.to_datetime(df['Transaction_Time'], format='%H:%M:%S').dt.hour
    df['minute'] = pd.to_datetime(df['Transaction_Time'], format='%H:%M:%S').dt.minute
    df['second'] = pd.to_datetime(df['Transaction_Time'], format='%H:%M:%S').dt.second

    # Drop original date/time columns and other unneeded columns
    df.drop(columns=['Transaction_Date', 'Transaction_Time', 'Transaction_Currency', 'Customer_Name'], inplace=True,
            axis=1)

    return df


# -------------------- Graph Snapshot Visualization Section --------------------
def view_graph(path, title):
    """
    Load an image from a file and create an interactive Plotly figure.
    This is used for displaying pre-generated network graph snapshots.
    """
    img = Image.open(path)
    fig = px.imshow(img, title=title)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    # Set a large initial size for a better display
    fig.update_layout(width=1200, height=800)
    return fig


# -------------------- Main Streamlit App --------------------
def main():
    st.title("Transaction Data Analysis & Graph Visualizations")

    # ----- Data Cleaning Section -----
    st.header("1. Data Cleaning")
    df_original = pd.read_csv("assets/Bank_Transaction_Fraud_Detection.csv")
    st.subheader("Original Data (First 5 Rows)")
    st.dataframe(df_original.head())

    df_cleaned = clean_data(df_original.copy())
    st.subheader("Cleaned Data (First 5 Rows)")
    st.dataframe(df_cleaned.head())

    st.markdown("### Data Cleaning Explanation")
    st.markdown(
        """
        - **Column Removal:** Unnecessary columns (e.g., IDs, email, contact) are dropped to focus on relevant transaction details and protect sensitive information.
        - **Date/Time Conversion:** The Transaction_Date and Transaction_Time fields are converted into separate numerical components (year, month, day, hour, minute, second) for simplified time-based analysis.
        """
    )

    # ----- Graph Snapshots Section -----
    st.header("2. Graph Snapshots")
    st.subheader("2.1 Original Graph Snapshot")
    st.plotly_chart(view_graph("assets/original_graph.png", "Original Graph (48 nodes, 25 relationships)"),
                    use_container_width=True)

    st.subheader("2.2 Failure Mode Graph Snapshot")
    st.plotly_chart(
        view_graph("assets/failure_mode_graph.png", "Failure Mode Graph (Transaction Graph with Highlighted Failure Modes)"),
        use_container_width=True)

    # ----- Interactive Graphs Section -----
    st.header("3. Interactive Graph Visualizations")
    st.subheader("3.1 Interactive Original Graph")
    original_html = "./assets/original_graph.html"  # Ensure this file exists in the same directory
    try:
        with open(original_html, 'r', encoding='utf-8') as f:
            html_data = f.read()
        components.html(html_data, height=600, scrolling=True)
    except Exception as e:
        st.error(f"Error reading {original_html}: {e}")

    st.subheader("3.2 Interactive FMEA Transaction Graph")
    transaction_html = "./assets/transaction_graph.html"  # Ensure this file exists in the same directory
    try:
        with open(transaction_html, 'r', encoding='utf-8') as f:
            html_data = f.read()
        components.html(html_data, height=600, scrolling=True)
    except Exception as e:
        st.error(f"Error reading {transaction_html}: {e}")

    # ----- FMEA Summary Report Section -----
    st.header("4. FMEA Summary Report")
    st.markdown("**Total Transactions:** 2000")
    st.markdown("**High Risk Transactions:** 442")
    st.markdown("**Average RPN:** 20.51")
    st.markdown("**Minimum RPN:** 15.00")
    st.markdown("**Maximum RPN:** 140.00")


if __name__ == "__main__":
    main()
