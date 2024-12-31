import streamlit as st
import requests
import os
import snowflake.connector
import datacompy
from dotenv import load_dotenv
import polars as pl

# Load environment variables
load_dotenv()

# Must be the first Streamlit command used
st.set_page_config(
    page_title="🥧 BAKeD",
    page_icon="🥧",
    layout="wide",  # Use wide layout instead of centered
    initial_sidebar_state="auto"
)

# Custom CSS to make things wider and more readable
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        .element-container {
            width: 100%;
        }
        .stDataFrame {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

def add_header():
    """Add branded header to the app"""
    # Add logo
    st.image("https://www.cuestapartners.com/wp-content/uploads/2022/09/logo-blue-transparent-cuesta.png", width=200)
    
    # Add title and subtitle
    st.title("🥧 BAKeD")
    st.subheader("Branch Analysis in Keboola using DataComPy")
    
    # Add author credit with link
    st.markdown("Written by [Cuesta Partners](https://www.cuestapartners.com)")
    
    # Add separator
    st.markdown("---")

# Start of the main app
add_header()

def get_branches():
    """Fetch branches from Keboola API"""
    kbc_token = os.getenv('KBC_TOKEN')
    kbc_url = os.getenv('KBC_URL')
    
    headers = {
        'X-StorageApi-Token': kbc_token
    }
    
    response = requests.get(
        f'{kbc_url}/v2/storage/dev-branches',
        headers=headers
    )
    
    if response.status_code == 200:
        branches = response.json()
        # Create a dictionary of "id - name" : id for the selectbox
        branch_options = {f"{b['id']} - {b['name']}": b['id'] for b in branches}
        return branch_options
    return {}

def get_schemas(branch_id):
    """Fetch schemas from Snowflake that match the branch ID"""
    try:
        # Establish Snowflake connection
        ctx = snowflake.connector.connect(
            user = st.secrets.user,
            password = st.secrets.password, 
            account = st.secrets.account,
            warehouse = st.secrets.warehouse,
            database = st.secrets.database
        )
        
        cursor = ctx.cursor()
        
        # Execute SQL to get schemas
        cursor.execute("SELECT schema_name FROM information_schema.schemata")
        schemas = cursor.fetchall()
        
        # Filter schemas that contain the branch ID
        matching_schemas = [
            schema[0] for schema in schemas 
            if str(branch_id) in schema[0]
        ]
        
        return matching_schemas
        
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {str(e)}")
        return []
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'ctx' in locals():
            ctx.close()

def get_tables(schema_name):
    """Fetch tables from the selected schema in Snowflake"""
    try:
        # Establish Snowflake connection
        ctx = snowflake.connector.connect(
             user = st.secrets.user,
            password = st.secrets.password, 
            account = st.secrets.account,
            warehouse = st.secrets.warehouse,
            database = st.secrets.database
        )
        
        cursor = ctx.cursor()
        
        # Execute SQL to get tables for the selected schema
        cursor.execute(f"""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = '{schema_name}'
        """)
        
        tables = cursor.fetchall()
        # Convert from list of tuples to list of strings
        table_names = [table[0] for table in tables]
        
        return table_names
        
    except Exception as e:
        st.error(f"Error fetching tables: {str(e)}")
        return []
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'ctx' in locals():
            ctx.close()

def get_dataframe_comparison(database, dev_schema, table_name, branch_id, join_column):
    """Get comparison between production and development schemas"""
    try:
        # Establish Snowflake connection
        ctx = snowflake.connector.connect(
            user = "SAPI_WORKSPACE_995497350",
            password = os.getenv('SNOWFLAKE_PASSWORD'),
            account = "keboola",
            warehouse = "KEBOOLA_PROD_SMALL",
            database = "SAPI_9508"
        )
        
        cursor = ctx.cursor()
        
        # Get production schema by removing branch_id from dev_schema
        prod_schema = dev_schema.replace(f"-{branch_id}", "")
        
        # Query for df1 (production)
        query1 = f'SELECT * FROM "{database}"."{prod_schema}"."{table_name}"'
        cursor.execute(query1)
        # First get pandas DataFrame then convert to Polars
        df1 = pl.from_pandas(cursor.fetch_pandas_all())
        
        # Query for df2 (development)
        query2 = f'SELECT * FROM "{database}"."{dev_schema}"."{table_name}"'
        cursor.execute(query2)
        # First get pandas DataFrame then convert to Polars
        df2 = pl.from_pandas(cursor.fetch_pandas_all())
        
        # Drop _timestamp column if it exists in either dataframe
        if '_timestamp' in df1.columns:
            df1 = df1.drop('_timestamp')
        if '_timestamp' in df2.columns:
            df2 = df2.drop('_timestamp')
        
        # Compare the dataframes using PolarsCompare
        compare = datacompy.PolarsCompare(
            df1,
            df2,
            join_columns=[join_column],
            df1_name='Production',
            df2_name='Development'
        )
        
        return compare
        
    except Exception as e:
        raise Exception(f"Error performing comparison: {str(e)}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'ctx' in locals():
            ctx.close()

def format_comparison_report(compare):
    """Format the datacompy comparison results into structured Streamlit output"""
    
    # Header section
    st.markdown("## 📊 Comparison Report")
    st.markdown("---")
    
    # Match Stats
    st.markdown("### 🎯 Match Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows in Production", len(compare.df1))
    with col2:
        st.metric("Rows in Development", len(compare.df2))
    with col3:
        st.metric("Matched Rows", compare.count_matching_rows())
    
    # Match Rate
    st.markdown("### 📈 Match Rate")
    match_rate = compare.count_matching_rows() / max(len(compare.df1), len(compare.df2))
    st.progress(match_rate)
    st.metric("Match Percentage", f"{match_rate * 100:.2f}%")
    
    # Column Analysis
    st.markdown("### 📋 Column Analysis")
    st.markdown("#### Columns in both datasets:")
    st.write(compare.intersect_columns())
    
    df1_unique = compare.df1_unq_columns()
    if len(df1_unique) > 0:
        st.markdown("#### 🔴 Columns only in Production:")
        st.write(df1_unique)
    
    df2_unique = compare.df2_unq_columns()
    if len(df2_unique) > 0:
        st.markdown("#### 🔵 Columns only in Development:")
        st.write(df2_unique)
    
    # Sample Differences
    if not compare.matches():
        st.markdown("### ⚠️ Sample Differences")
        
        # Get all columns that have differences
        all_columns = compare.df1.columns
        
        # Check for value differences in each column
        for column in all_columns:
            try:
                df_mismatch = compare.sample_mismatch(column)
                if df_mismatch is not None and len(df_mismatch) > 0:
                    st.markdown(f"#### Value Differences in column: `{column}`")
                    st.dataframe(df_mismatch, use_container_width=True)
            except:
                continue
        
        # Production only rows
        df1_unq = compare.df1_unq_rows
        if len(df1_unq) > 0:
            st.markdown("#### Rows only in Production")
            st.markdown(f"**Total Rows in Production that are not in Dev:** {len(df1_unq):,}")
            st.markdown("*Showing first 10 rows as sample:*")
            st.dataframe(df1_unq.head(10), use_container_width=True)
        
        # Development only rows
        df2_unq = compare.df2_unq_rows
        if len(df2_unq) > 0:
            st.markdown("#### Rows only in Development")
            st.markdown(f"**Total Rows in Dev that are not in Production:** {len(df2_unq):,}")
            st.markdown("*Showing first 10 rows as sample:*")
            st.dataframe(df2_unq.head(10), use_container_width=True)
    
    # Overall Match Status
    st.markdown("---")
    if compare.matches():
        st.success("✅ The datasets are an exact match!")
    else:
        st.error("❌ The datasets have differences")

def get_columns(schema_name, table_name):
    """Fetch columns from the selected table"""
    try:
        # Establish Snowflake connection
        ctx = snowflake.connector.connect(
            user = st.secrets.user,
            password = st.secrets.password, 
            account = st.secrets.account,
            warehouse = st.secrets.warehouse,
            database = st.secrets.database
        )
        
        cursor = ctx.cursor()
        
        # First query to show columns
        cursor.execute(f"""
            SHOW COLUMNS IN TABLE "{st.secrets.database}"."{schema_name}"."{table_name}"
        """)
        
        # Second query to get column names
        cursor.execute(f"""
            SELECT "column_name"
            FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
            WHERE "table_name" = '{table_name}'
        """)
        
        columns = cursor.fetchall()
        # Convert from list of tuples to list of strings
        column_names = [col[0] for col in columns]
        
        return column_names
        
    except Exception as e:
        st.error(f"Error fetching columns: {str(e)}")
        return []
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'ctx' in locals():
            ctx.close()

# Set up the Streamlit page
st.title('Keboola Branch Manager')

# First dropdown - Branch Selection
branch_options = get_branches()
if branch_options:
    selected_branch = st.selectbox(
        'Select Branch:',
        options=[''] + list(branch_options.keys())
    )
    
    # Second dropdown - Dev Bucket Selection
    schemas = get_schemas(branch_options[selected_branch]) if selected_branch else []
    selected_schema = st.selectbox(
        'Select dev bucket:',
        options=[''] + schemas
    )
    
    # Third dropdown - Dev Table Selection
    tables = get_tables(selected_schema) if selected_schema else []
    selected_table = st.selectbox(
        'Select dev table:',
        options=[''] + tables
    )
    
    # Fourth dropdown - Join Column Selection
    columns = get_columns(selected_schema, selected_table) if selected_schema and selected_table else []
    selected_column = st.selectbox(
        'Select join column:',
        options=[''] + columns
    )
    
    # Show comparison if all selections are made
    if selected_branch and selected_schema and selected_table and selected_column:
        branch_id = branch_options[selected_branch]
        
        try:
            # Update comparison to use the selected join column
            comparison = get_dataframe_comparison(
                database=st.secrets.database,
                dev_schema=selected_schema,
                table_name=selected_table,
                branch_id=branch_id,
                join_column=selected_column
            )
            
            # Format and display the comparison
            format_comparison_report(comparison)
            
        except Exception as e:
            st.error(f"Error performing comparison: {str(e)}")
else:
    st.error("No branches found or error connecting to API")