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
    table_info = None
    ##To make it more dynamic, store flags in extended properties and grab:
    create_date = "create_date" 
    modify_date = "modify_date"


    def __init__(self, secrets):
        self.secrets = secrets
        self.table_info = {}
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

    def get_rows(self, table_name, select_what = "*", where_clause = {}, schema_name = "dbo"):  
        """
        Get the row 

        :select_what: Column(s) being selected for
        :where_clause: A dictionary like column_name:column_value to form the where clause
        """
        query = f"SELECT {select_what} FROM {schema_name}.{table_name} "
        if where_clause:
            where = self._build_where_clause(where_clause)
            query += f"{where['placeholder']}"
            result = pd.read_sql_query(query, self.engine, params=where['values'])
        else:
            result = pd.read_sql_query(query, self.engine)
    
        return result.to_dict('records')
    
    def get_column_names(self, table_name, schema_name = "dbo"):
        """
        Get the column names of a specified table in the Azure DB.
        """
        ##Check to see if it's already set/stored
        if self._check_table_dictionary(table_name, 'columns'):
            return self.table_info[table_name]['columns']   
        
        query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{schema_name}'"    
        
        try:
            result = pd.read_sql_query(query, self.engine)
            self.table_info[table_name]['columns'] =  result['COLUMN_NAME'].tolist()
            return self.table_info[table_name]['columns']
        except Exception as e:
            return str(e)
   
    def get_primary_key_name(self, table_name, schema_name = "dbo"):
        """
        Get the primary key of a specified table in the Azure DB.
        """
        if self._check_table_dictionary(table_name, 'p_key'):
            return self.table_info[table_name]['p_key']
        
        query = f"EXECUTE sys.sp_pkeys @table_name=N'{table_name}' @table_owner=N'{schema_name}'"
        result = pd.read_sql_query(query, self.engine)
        self.table_info[table_name]['p_key'] = result['COLUMN_NAME'].iloc[0]
        return self.table_info[table_name]['p_key']
    
       
    def single_insert(self, data, table_name, schema_name = "dbo"):
        """
        Insert data into the Azure DB Server.
        Return insert id

        :data: A single dictionary of column:values to insert
        """
        data[self.create_date] = datetime.now() ##set the create date

        valid_columns = self._validate_columns(table_name, schema_name)
        filtered = {k: v for k, v in data.items() if k in valid_columns}

        columns = ', '.join(filtered.keys())
        placeholders = ', '.join(['?'] * len(filtered))
        values = tuple(filtered.values())  
        

        try: ## use raw connection to return the primary key 
            query = f"INSERT INTO {schema_name}.{table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.connection.commit()
            self.cursor.execute("SELECT SCOPE_IDENTITY()")
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Failed to insert row: {e}")
            self.connection.rollback()
            return f"Failed insert into {table_name}: " + str(e)

    def bulk_insert(self, data, table_name, schema_name = "dbo"):
        """
        Insert bulk data into the specified table on Azure DB Server.

        :data: A list of dictionaries containing data to be inserted
        """
        for row in data: ##set the create date for all rows
            row[self.create_date] = datetime.now()

        df = pd.DataFrame(data)

        try:
            df = self._validate_columns(df, table_name, schema_name)
            df.to_sql(table_name, self.engine, schema=schema_name, if_exists='append', index=False)
            return True
        except Exception as e:
            print(f"Failed to insert data: {e}")
            return str(e)

    def single_update(self, data, table_name, primary_key_value, schema_name = "dbo"):
        """
        Update a single row based on its primary key

        :data: A single dictionary of column:values to update
        :primary_key_value: The actual value of the PK, not the PK name
        """
        if not self._check_table_dictionary(table_name, 'p_key'):
            self.get_primary_key_name(table_name, schema_name)
        
        primary_key = self.table_info[table_name]['p_key']
        data[self.modify_date] = datetime.now() ##set the modify date 

        valid_columns = self._validate_columns(table_name, schema_name)
        filtered = {k: v for k, v in data.items() if k in valid_columns}

        columns = ', '.join(f"{col} = ?" for col in filtered)
        values = tuple(filtered.values())  

        try:
            query = f"UPDATE {schema_name}.{table_name} SET {columns} WHERE {primary_key} = {primary_key_value}"
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Failed to updated row: {e}")
            return str(e)
        


    def bulk_update_by_where(self, data, table_name, where_clause, schema_name = "dbo"):
        """
        Update a number of rows with the same values, hopefully based on a where condition

        :data: A single dictionary containing the data column_name:value to be updated
        :where_clause: A dictionary of column_name:column_value containing the where condition
        """

        for row in data: ##set the modify date for all rows
            row[self.modify_date] = datetime.now()
        
        df = pd.DataFrame(data)
        df = self._validate_columns(df, table_name, schema_name)    
        columns = ', '.join(f"{col} = ?" for col in df.columns)
        values = tuple(df.values[0])
        try:
            where = self._build_where_clause(where_clause)
            all_values = values + where['values']
            query = f"UPDATE {schema_name}.{table_name} SET {columns} {where['placeholder']}"

            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Failed to updated row: {e}")
            return str(e)

        pass

    def bulk_update_by_id(self, data, table_name, id_name, schema_name = "dbo"):
        """
        Update a number of rows with different values based on the specified identifier

        :data: A list of dictionaries containing the data column_name:values,... to be updated
        """
    
        for row in data: ##set the modify date for all rows
            row[self.modify_date] = datetime.now() 

        pass
    

    ## CLASS HELPERS ##

    def _check_table_dictionary(self, table_name, look_up = None):    
        """
        Check if table exists in the dictionary. If not, create it.

        :look_up: Key to search in the specified table dictionary, optional
        """
        if table_name not in self.table_info:
            self.table_info[table_name] = {}
            self.table_info[table_name]['p_key']= None
            self.table_info[table_name]['columns'] = None
            return False
       
        if look_up and not self.table_info[table_name][look_up]:
            return False

        return True
        

    def _validate_columns(self, table_name, schema_name = "dbo", df = None):
        """
        Dynamically validate the columns of the data against the table's actual columns in the Azure DB.

        :df: DataFrame to validate against
        """
        if not self._check_table_dictionary(table_name, 'columns'):
            self.get_column_names(table_name, schema_name)
        
        if df is None:
            return self.table_info[table_name]['columns']
        ## Filter the DataFrame to only include valid columns 
        return df[[col for col in df.columns if col in self.table_info[table_name]['columns']]]
    
    def _build_where_clause(self, where = {}, key_word = "AND"):
        """
        Builds the where string for the query

        :where: A dictionary of column_name:column_value containing the where condition.
        """
        ##add dynamic validation for where clause?? is that overkill?
        placeholder = "WHERE "
        match key_word:
            case "AND": # format: {"column_name_one": value, "column_name_two": value...}
                placeholder = " AND ".join(f"{key} = ? " for key in where)
                values = tuple(where.values())
            case "IN":  # format: {"column_name": [value, value, value]}
                column = next(iter(where))
                placeholder += f"{column} IN (" +  ', '.join(['?'] * len(where[column])) + ")"
                values = tuple(where[column])

        return {'placeholder' : placeholder, 'values': values }

        

       

          



