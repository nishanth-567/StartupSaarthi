"""
Structured data parser for CSV and Excel files.
"""

from typing import List, Dict, Any
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


class StructuredDataParser:
    """Parse structured data (CSV, Excel) into text chunks."""
    
    def __init__(self):
        """Initialize structured data parser."""
        pass
    
    def process_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process CSV file.
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            List of chunks (one per row) with metadata
        """
        chunks = []
        
        try:
            df = pd.read_csv(file_path)
            
            for idx, row in df.iterrows():
                # Convert row to natural language text
                row_text = self._row_to_text(row, df.columns)
                
                chunks.append({
                    "content": row_text,
                    "metadata": {
                        "document": Path(file_path).name,
                        "type": "csv",
                        "row_index": int(idx),
                        "structured_data": row.to_dict()
                    }
                })
            
            logger.info(f"Processed CSV: {len(chunks)} rows from {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
        
        return chunks
    
    def process_excel(self, file_path: str, sheet_name: str = None) -> List[Dict[str, Any]]:
        """
        Process Excel file.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Specific sheet name (None = all sheets)
        
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                chunks.extend(self._process_dataframe(df, Path(file_path).name, sheet_name))
            else:
                # Process all sheets
                excel_file = pd.ExcelFile(file_path)
                for sheet in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    chunks.extend(self._process_dataframe(df, Path(file_path).name, sheet))
            
            logger.info(f"Processed Excel: {len(chunks)} rows from {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing Excel: {e}")
        
        return chunks
    
    def _process_dataframe(self, df: pd.DataFrame, document_name: str, sheet_name: str = None) -> List[Dict[str, Any]]:
        """Process DataFrame into chunks."""
        chunks = []
        
        for idx, row in df.iterrows():
            row_text = self._row_to_text(row, df.columns)
            
            metadata = {
                "document": document_name,
                "type": "excel",
                "row_index": int(idx),
                "structured_data": row.to_dict()
            }
            
            if sheet_name:
                metadata["sheet_name"] = sheet_name
            
            chunks.append({
                "content": row_text,
                "metadata": metadata
            })
        
        return chunks
    
    def _row_to_text(self, row: pd.Series, columns: pd.Index) -> str:
        """
        Convert DataFrame row to natural language text.
        
        Args:
            row: DataFrame row
            columns: Column names
        
        Returns:
            Natural language text representation
        """
        text_parts = []
        
        for col in columns:
            value = row[col]
            
            # Skip NaN values
            if pd.isna(value):
                continue
            
            # Format as "Column: Value"
            text_parts.append(f"{col}: {value}")
        
        return ". ".join(text_parts)
    
    def process_structured_data(self, file_path: str, data_type: str) -> List[Dict[str, Any]]:
        """
        Process structured data file.
        
        Args:
            file_path: Path to file
            data_type: Type (csv, excel)
        
        Returns:
            List of chunks with metadata
        """
        if data_type == "csv":
            return self.process_csv(file_path)
        elif data_type == "excel":
            return self.process_excel(file_path)
        else:
            logger.error(f"Unsupported structured data type: {data_type}")
            return []
