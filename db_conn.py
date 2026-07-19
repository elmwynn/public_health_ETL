import os
import pyodbc
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv



class connection_object:
    """
    A dynamic class to manage the connection to the Azure DB Server.
    """
    engine = None;
    connection = None;
    cursor = None;
    column_names = None;



    def __init__(self):
        load_dotenv()
        self.connect()

    def connect(self):
        """
        Establish a connection to the Azure DB Server.
        """ 
        try:
            connection_string = f"mssql+pyodbc://{os.getenv('UID')}:{os.getenv('DB_PWD')}@{os.getenv('SERVER')}/{os.getenv('DATABASE')}?driver={os.getenv('DRIVER')}"
            #Engine for bulk inserts/updates. Connection for dynamic single inserts
            self.engine = create_engine(connection_string)
            self.connection = self.engine.raw_connection()
            self.cursor = self.connection.cursor()
            print("SQL Server connection successful!")
        except Exception as e:
            print(f"SQL Server connection FAILED: {e}")
            return str(e)

    
    def close(self):
        """
        Close the connection to the Azure DB Server.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    
    
    def get_column_names(self, table_name, schema_name = "dbo"):
        """
        Get the column names of a specified table in the Azure DB Server.
        """
        ##Check to see if it's already stored
        if self.column_names.get(table_name, {}).get('columns'):
            return self.column_names[table_name]['columns']      
        query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{schema_name}'"    
        try:
            columns = pd.read_sql(query, self.connection)
            self.column_names[table_name] = {'columns' : columns['COLUMN_NAME'].tolist()}
            return self.column_names[table_name]['columns']
        except Exception as e:
            return str(e)
        
   
    def get_primary_key(self, table_name, schema_name = "dbo"):
        """
        Get the primary key of a specified table in the Azure DB Server.
        """
        if self.column_names.get(table_name, {}).get('p_key'):
            return self.column_names[table_name]['p_key']

        query = f"EXECUTE s"

        pass    
        

    def validate_columns(self, df, table_name, schema_name = "dbo"):
        """
        Validate the columns of the data against the table's columns in the Azure DB Server.
        """
        if not self.column_names[table_name]['columns']:
            self.get_column_names(table_name, schema_name)

        ## Filter the DataFrame to only include valid columns
        return df[[col for col in df.columns if col in self.column_names[table_name]['columns']]]


       
    def single_insert(self, data, table_name, schema_name = "dbo"):
        """
        Insert data into the Azure DB Server.
        Return insert id
        """

        df = pd.DataFrame(data)
        df = self.validate_columns(df, table_name, schema_name)
        columns =  ', '.join(self.column_names[table_name]['columns'])
        placeholders = ', '.join(['?'] * len(self.column_names[table_name]['columns']))
        values = tuple(df.values[0])
        try:
            query = f"INSERT INTO {schema_name}.{table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.cursor.execute("SELECT SCOPE_IDENTITY()")
            return self.cursor.fetchone()[0]
        except Exception as e:
            self.connection.rollback()
            return str(e)

        

    def bulk_insert(self, data, table_name, schema_name = "dbo"):
        """
        Insert bulk data into the Azure DB Server.
        """

        df = pd.DataFrame(data)

        try:
            df = self.validate_columns(df, table_name, schema_name)
            df.to_sql(table_name, self.engine, schema=schema_name, if_exists='append', index=False)
            return True
        except Exception as e:
            print(f"Failed to insert data: {e}")
            return str(e)

        pass  

    

