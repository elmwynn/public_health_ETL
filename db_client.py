import pandas as pd
from datetime import datetime
from config import DRIVER
from sqlalchemy import create_engine


class DatabaseClient:
    """
    A dynamic class to manage the connection and SQL transactions to the Azure DB Server.
    """
    secrets = None
    engine = None
    connection = None
    cursor = None
    container = None
    column_names = None
    create_date = "create_date"
    modify_date = "modify_date"


    def __init__(self, secrets):
        self.secrets = secrets
        self.connect()

    def connect(self):
        """
        Establish a connection to the Azure DB Server.
        """ 
        try:    
            connection_string = f"mssql+pyodbc://{self.secrets['USER']}:{self.secrets['PASS']}@{self.secrets['SERVER']}/{self.secrets['DB']}?driver={DRIVER}"
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
        self.cursor.close()
        self.connection.close()
        self.engine.dispose()  
    
    def get_column_names(self, table_name, schema_name = "dbo"):
        """
        Get the column names of a specified table in the Azure DB Server.
        """
        ##Check to see if it's already stored
        if self.check_table_dictionary(table_name, 'columns'):
            return self.column_names[table_name]['columns']   
        
        query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{schema_name}'"    
        
        try:
            result = pd.read_sql(query, self.connection)
            self.column_names[table_name]['columns'] =  result['COLUMN_NAME'].tolist()
            return self.column_names[table_name]['columns']
        except Exception as e:
            return str(e)
   
    def get_primary_key_name(self, table_name, schema_name = "dbo"):
        """
        Get the primary key of a specified table in the Azure DB Server.
        """
        if self.check_table_dictionary(table_name, 'p_key'):
            return self.column_names[table_name]['p_key']
        
        query = f"EXECUTE sys.sp_pkeys @table_name=N'{table_name}' @table_owner=N'{schema_name}'"
        result = pd.read_sql(query, self.connection)
        self.column_names[table_name]['p_key'] = result['COLUMN_NAME'].iloc[0]
        return self.column_names[table_name]['p_key']
    

    def check_table_dictionary(self, table_name, look_up = None):    
        """
        Check if table exists in the dictionary. If not, create it.
        """
        if table_name not in self.column_names:
            self.column_names[table_name] = {}
            self.column_names[table_name]['p_key']= None
            self.column_names[table_name]['columns'] = None
            return False
       
        if look_up and not self.column_names[table_name][look_up]:
            return False

        return True
        


    def validate_columns(self, df, table_name, schema_name = "dbo"):
        """
        Dynamically validate the columns of the data against the table's actual columns in the Azure DB Server.
        """
        if not self.check_table_dictionary(table_name, 'columns'):
            self.get_column_names(table_name, schema_name)

        ## Filter the DataFrame to only include valid columns and return it
        return df[[col for col in df.columns if col in self.column_names[table_name]['columns']]]
       
    def single_insert(self, data, table_name, schema_name = "dbo"):
        """
        Insert data into the Azure DB Server.
        Return insert id
        """
        data['create_date'] = datetime.now() ##set the create date
        df = pd.DataFrame(data)
        df = self.validate_columns(df, table_name, schema_name)
        columns =  ', '.join(self.column_names[table_name]['columns'])
        placeholders = ', '.join(['?'] * len(self.column_names[table_name]['columns']))
        values = tuple(df.values[0])

        try: ## use raw connection to return the primary key 
            query = f"INSERT INTO {schema_name}.{table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.connection.commit()
            self.cursor.execute("SELECT SCOPE_IDENTITY()")
            return self.cursor.fetchone()[0]
        except Exception as e:
            self.connection.rollback()
            return str(e)

    def bulk_insert(self, data, table_name, schema_name = "dbo"):
        """
        Insert bulk data into the Azure DB Server.
        """
        for row in data:
            row[self.create_date] = datetime.now()
        df = pd.DataFrame(data)

        try:
            df = self.validate_columns(df, table_name, schema_name)
            df.to_sql(table_name, self.engine, schema=schema_name, if_exists='append', index=False)
            return True
        except Exception as e:
            print(f"Failed to insert data: {e}")
            return str(e)

    def single_update(self, data, table_name, primary_key_value, schema_name = "dbo"):
        if not self.check_table_dictionary(table_name, 'p_key'):
            self.get_primary_key_name(table_name, schema_name)
        
        if not self.check_table_dictionary(table_name, 'columns'):
            self.get_column_names(table_name, schema_name)

        data['modify_date'] = datetime.now() ##set the modify date    

        try:
            pass
        except Exception as e:
            pass
        


    def bulk_update(self, data, table_name, where_clause = None, schema_name = "dbo"):
        pass



