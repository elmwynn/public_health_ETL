import pandas as pd
from config import DRIVER
from sqlalchemy import create_engine


class DatabaseClient:
    """
    A dynamic class to manage the connection and SQL transactions to the Azure DB Server.
    """
    ##To make it more dynamic, store flags in extended properties and grab:
    create_date = "create_date" 
    modify_date = "modify_date"


    def __init__(self, secrets):
        self.secrets = secrets
        self.engine = None
        self.connection = None
        self.cursor = None
        self.table_info = {}
        self.connect()

    def connect(self):
        """
        Establish a connection to the Azure DB Server.
        Exceptions bubble up to the calling ETL script.
        """   
        connection_string = f"mssql+pyodbc://{self.secrets['USER']}:{self.secrets['PASS']}@{self.secrets['SERVER']}/{self.secrets['DB']}?driver={DRIVER}"
        #Engine for bulk inserts/updates. Connection for dynamic single inserts
        self.engine = create_engine(connection_string)
        self.connection = self.engine.raw_connection()
        self.cursor = self.connection.cursor()
       
    
    def close(self):
        """
        Close the connection to the Azure DB Server.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection: 
            self.connection.close()
        if self.engine:
            self.engine.dispose()  

    def get_rows(self, table_name: str, schema_name:str = "dbo", where_clause: dict = None, select_what:str = "*",  key_word: str = None):  
        """
        Get the row 

        :select_what: Column(s) being selected for
        :where_clause: A dictionary like column_name:column_value to form the where clause
        """
        try:
            query = f"SELECT {select_what} FROM {schema_name}.{table_name} "
            if where_clause:
                where = self._build_where_clause(where_clause, key_word)
                query += f"{where['placeholder']}"
                self.cursor.execute(query, where['values'])
            else:
                self.cursor.execute(query)
            results = self.cursor.fetchall()
            column_names = [desc[0] for desc in self.cursor.description]
            return {'success': True, 'data': [dict(zip(column_names, row)) for row in results]}
        except Exception as e:
            return {'success': False, 'error': f"Failed to fetch data from {table_name}: " + str(e)}
    
       
    def single_insert(self, data: dict, table_name: str, schema_name:str = "dbo"):
        """
        Insert data into the Azure DB Server.
        Return insert id

        :data: A single dictionary of column:values to insert
        """
        try:
            if not self._check_table_dictionary(table_name, 'p_key'):
                self._get_primary_key_name(table_name, schema_name)

            data[self.create_date] = pd.Timestamp.now() ##set the create date
            valid_columns = self._validate_columns(table_name, schema_name)
            ##filter only the valid items into the statement
            filtered = {k: v for k, v in data.items() if k in valid_columns}
            columns = ', '.join(filtered.keys())
            placeholders = ', '.join(['?'] * len(filtered))
            values = tuple(filtered.values())  

            ## use raw connection to return the primary key value
            query = f"INSERT INTO {schema_name}.{table_name} ({columns}) OUTPUT INSERTED.{self.table_info[table_name]['p_key']} VALUES ({placeholders})"
            self.cursor.execute(query, values)
            insert_id = self.cursor.fetchone()[0]
            self.connection.commit()
            return {'success': True, 'data': insert_id}
        except Exception as e:
            self.connection.rollback()
            return {'success': False, 'error': f"Failed insert into {table_name}: " + str(e)}

    def bulk_insert(self, data: list, table_name: str, schema_name = "dbo"):
        """
        Insert bulk data into the specified table on Azure DB Server.

        :data: A list of dictionaries containing data to be inserted
        """
        try:
            for row in data: ##set the create date for all rows
                row[self.create_date] = pd.Timestamp.now()

            df = pd.DataFrame(data)
            df = self._validate_columns(table_name, schema_name, df)
            df.to_sql(table_name, self.engine, schema=schema_name, if_exists='append', index=False)
            return {'success': True, 'data': None}
        except Exception as e:
            return {'success': False, 'error': f"Failed insert into {table_name}: " + str(e)}
            

    def single_update(self, data: dict, primary_key_value:int, table_name: str, schema_name = "dbo"):
        """
        Update a single row based on its primary key

        :data: A single dictionary of column:values to update
        :primary_key_value: The actual value of the PK, not the PK name
        """
        try:
            if not self._check_table_dictionary(table_name, 'p_key'):
                self._get_primary_key_name(table_name, schema_name)
            
            primary_key = self.table_info[table_name]['p_key']
            data[self.modify_date] = pd.Timestamp.now() ##set the modify date 

            valid_columns = self._validate_columns(table_name, schema_name)
            filtered = {k: v for k, v in data.items() if k in valid_columns}

            columns = ', '.join(f"{col} = ?" for col in filtered)
            all_values = tuple(filtered.values()) + (primary_key_value,)
            query = f"UPDATE {schema_name}.{table_name} SET {columns} WHERE {primary_key} = ?"
            self.cursor.execute(query, all_values)
            self.connection.commit()
            return {'success': True, 'data': None}
        except Exception as e:
            self.connection.rollback()
            return {'success': False, 'error': f"Failed to update row in {table_name}: " + str(e)}


    def bulk_update_by_where(self, data: dict, where_clause: dict, table_name: str, schema_name = "dbo"):
        """
        Update a number of rows with the same values, hopefully based on a where condition

        :data: A single dictionary containing the data column_name:value to be updated
        :where_clause: A dictionary of column_name:column_value containing the where condition
        """
        try:
            ##set the modify date for all rows
            data[self.modify_date] = pd.Timestamp.now()
            valid_columns = self._validate_columns(table_name, schema_name)   
            filtered = {k: v for k, v in data.items() if k in valid_columns} 
            columns = ', '.join(f"{col} = ?" for col in filtered)
            values = tuple(filtered.values())
            where = self._build_where_clause(where_clause)
            all_values = values + where['values']

            query = f"UPDATE {schema_name}.{table_name} SET {columns} {where['placeholder']}"
            self.cursor.execute(query, all_values)
            self.connection.commit()
            return {'success': True, 'data': None}
        except Exception as e:
            self.connection.rollback()
            return {'success': False, 'error': f"Failed to update rows in {table_name}: " + str(e)}

    def bulk_update_by_id(self, data: list, id_name: str, table_name: str, schema_name:str = "dbo"):
        """
        Update a number of rows with different values based on the specified identifier

        :data: A list of dictionaries containing the data column_name:values,... to be updated
        """
        try:
            for row in data: ##set the modify date for all rows
                row[self.modify_date] = pd.Timestamp.now()
            
            valid_columns = self._validate_columns(table_name, schema_name)   
            #loop through the list of dictionaries and for each dictionary, filter out the invalid columns 
            filtered =  [{k: v for k, v in row.items() if k in valid_columns} for row in data]
            columns_set = ', '.join(f"t.{col} = u.{col}" for col in filtered[0] if col != id_name)
            # assumes all rows have same keys in same order (guaranteed for same-source API data)
            all_values = tuple(value for row in filtered for value in row.values())
            columns = ','.join(str(col) for col in filtered[0])
            row_placeholder = '(' + ', '.join('?' for _ in filtered[0]) + ')'
            placeholder = ', '.join(row_placeholder for _ in filtered)
    
            query = f"UPDATE t SET {columns_set} FROM {schema_name}.{table_name} t INNER JOIN (VALUES {placeholder}) AS u({columns}) ON t.{id_name} = u.{id_name}"
            self.cursor.execute(query, all_values)
            self.connection.commit()
            return {'success': True, 'data': None}
        except Exception as e:
            self.connection.rollback()
            return {'success': False, 'error': f"Failed to update rows in {table_name}: " + str(e)}
       
        
    

    ## CLASS HELPERS ##

    def _check_table_dictionary(self, table_name: str, look_up:str = None):    
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
        

    def _validate_columns(self, table_name: str, schema_name:str = "dbo", df = None):
        """
        Dynamically validate the columns of the data against the table's actual columns in the Azure DB.

        :df: DataFrame to validate against
        """
        if not self._check_table_dictionary(table_name, 'columns'):
            self._get_column_names(table_name, schema_name)
        
        if df is None: ##single row operations, return the valid columns.
            return self.table_info[table_name]['columns']
        ## Filter the passed DataFrame to only include valid columns for bulk operations
        return df[[col for col in df.columns if col in self.table_info[table_name]['columns']]]
    
    def _build_where_clause(self, where: dict, key_word:str = "AND"):
        """
        Builds the where string for the query

        :where: A dictionary of column_name:column_value containing the where condition.
        """
        ##add dynamic validation for where clause?? is that overkill?
        placeholder = "WHERE "
        match key_word:
            case "AND": # format: {"column_name_one": value, "column_name_two": value...}
                placeholder += " AND ".join(f"{key} = ? " for key in where)
                values = tuple(where.values())
            case "IN":  # format: {"column_name": [value, value, value]}
                column = next(iter(where))
                placeholder += f"{column} IN (" +  ', '.join(['?'] * len(where[column])) + ")"
                values = tuple(where[column])
        return {'placeholder' : placeholder, 'values': values }

        
    def _get_column_names(self, table_name: str, schema_name:str = "dbo"):
        """
        Get the column names of a specified table in the Azure DB.
        """
        ##Check to see if it's already set/stored
        if self._check_table_dictionary(table_name, 'columns'):
            return self.table_info[table_name]['columns']   
           
        query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{schema_name}'"    
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        self.table_info[table_name]['columns'] =  [result[0] for result in results]
        return self.table_info[table_name]['columns']
       
   
    def _get_primary_key_name(self, table_name: str, schema_name:str = "dbo"):
        """
        Get the primary key of a specified table in the Azure DB.
        """
        if self._check_table_dictionary(table_name, 'p_key'):
            return self.table_info[table_name]['p_key']
        
        query = f"EXECUTE sys.sp_pkeys @table_name=N'{table_name}', @table_owner=N'{schema_name}'"
        self.cursor.execute(query)
        self.table_info[table_name]['p_key'] = self.cursor.fetchone()[3]
        return self.table_info[table_name]['p_key']


          



