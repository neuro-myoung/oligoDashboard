import streamlit as st
import pandas as pd 
from pathlib import Path
import polars as pl
from io import StringIO

from src.oligo_align import oligoAlign

# Page configuration
st.set_page_config(
    page_title="🧬 Oligo Alignment Tool",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # Title
    st.title("🧬 Oligonucleotide Alignment Visualizer")
    st.write("")
    st.write("")
    st.write("")
    
    # File upload and plot button in columns
    col1, col2, col3 = st.columns([3,1,1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Drag and drop your CSV file here",
            type=['csv'],
            help="CSV should contain columns: position, nucleotide, compound_id, sugar, base, linker"
        )
    
    with col3:
        # Add some spacing to align button with file uploader
        plot_button = st.button("Align", type="primary", use_container_width=True)
    
    st.write("")
    st.write("")
    # Determine which data to use
    df = None
    data_source = ""
    
    if uploaded_file is not None:
        # Read the uploaded file content as string
        file_content = StringIO(uploaded_file.getvalue().decode("utf-8"))
        # Load with Polars
        df = pl.read_csv(file_content)
        data_source = f"Uploaded file: {uploaded_file.name}"
  
    else:
        # Use sample data if no file uploaded
        df = pl.read_csv("assets/sample.csv")
        data_source = "Sample data (assets/sample.csv)"
    
    # Always plot the data (either uploaded file or sample data)
    if df is not None:
        try:
            # Show data source
            st.info(f"Plotting: {data_source}")
            
            # Validate required columns
            required_cols = ['position', 'nucleotide', 'compound_id', 'sugar', 'base', 'linker']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
                st.write("**Available columns:**", list(df.columns))
                st.write("**Required columns:**", required_cols)
            else:
                # Create and display the plot
                with st.spinner("Generating visualization..."):
                    chart = oligoAlign(df, align='position')
                    st.altair_chart(chart, use_container_width=False)
                
                # Show basic data info
                st.metric("Sequences Aligned", len(df.select(pl.col("compound_id").unique())))
        
                    
        except Exception as e:
            st.error(f"Error generating plot: {str(e)}")
            st.write("Please check your data format and try again.")
            
            # Show instructions as fallback
            st.markdown("""
            ### Expected CSV Format:
            Your file should contain these columns:
            - `position` - Position of nucleotide in sequence (integer)
            - `nucleotide` - Nucleotide letter (A, T, G, C, U)
            - `compound_id` - Unique identifier for each oligonucleotide
            - `sugar` - Sugar type (DNA, RNA, etc.)
            - `base` - Base letter for display
            - `linker` - Type of linker between nucleotides (none, phosphate, sulfur, etc.)
            """)

if __name__ == "__main__":
    main()