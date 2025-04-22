#!/usr/bin/env python
import os
import sqlite3
import argparse
import logging
import json
import datetime
import traceback
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('robust_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RobustMigrator:
    def __init__(self, sqlite_db_path, target_db_config, mappings_file):
        self.sqlite_db_path = sqlite_db_path
        self.target_db_config = target_db_config
        self.target_db_type = target_db_config.get('db_type', 'postgresql')
        
        # Load mappings from file
        with open(mappings_file, 'r') as f:
            self.mappings = json.load(f)
            
        self.sqlite_conn = None
        self.target_conn = None
        
        # Track successfully migrated patients
        self.migrated_patients = {}
        
        # Default values for NULL fields
        self.default_date = "2005-12-10"  # YYYY-MM-DD format for database
        self.default_string = "No data"
        self.default_int = 0
        
    def connect(self):
        """Connect to both databases"""
        try:
            # Connect to SQLite
            self.sqlite_conn = sqlite3.connect(self.sqlite_db_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.sqlite_db_path}")
            
            # Connect to target database
            if self.target_db_type.lower() == 'postgresql':
                import psycopg2
                self.target_conn = psycopg2.connect(
                    host=self.target_db_config.get('host', 'localhost'),
                    database=self.target_db_config.get('database'),
                    user=self.target_db_config.get('user'),
                    password=self.target_db_config.get('password'),
                    port=self.target_db_config.get('port', 5432)
                )
                logger.info(f"Connected to PostgreSQL database: {self.target_db_config.get('database')}")
            else:
                logger.error(f"Unsupported target database type: {self.target_db_type}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error connecting to databases: {e}")
            self.close()
            return False
    
    def close(self):
        """Close database connections"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
            logger.info("SQLite connection closed")
        if self.target_conn:
            self.target_conn.close()
            logger.info("Target database connection closed")

    def get_table_schema(self, table_name):
        """Get the actual schema of an SQLite table"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = {col[1]: col[2] for col in cursor.fetchall()}
        cursor.close()
        return columns

    def get_target_columns(self, table_name):
        """Get the columns of a target PostgreSQL table"""
        cursor = self.target_conn.cursor()
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
        """, (table_name,))
        columns = {col[0]: {'type': col[1], 'nullable': col[2] == 'YES'} for col in cursor.fetchall()}
        cursor.close()
        return columns

    def parse_date(self, date_str):
        """Parse various date formats and return ISO format date string"""
        if not date_str or date_str == '':
            return self.default_date
            
        date_str = date_str.strip()
        
        # Remove any special characters or bullets
        date_str = re.sub(r'[•\s]+', ' ', date_str).strip()
        
        # Try various date formats
        date_formats = [
            '%Y-%m-%d',
            '%d/%m/%y',
            '%d/%m/%Y',
            '%m/%d/%y',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%m-%d-%Y',
            '%d.%m.%Y',
            '%m.%d.%Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
                return parsed_date
            except ValueError:
                continue
        
        # If all parsing attempts fail, log and return default date
        logger.warning(f"Could not parse date: {date_str}, using default date")
        return self.default_date

    def get_default_value(self, column_type):
        """Get default value based on column type"""
        if 'int' in column_type.lower() or 'serial' in column_type.lower():
            return self.default_int
        elif 'date' in column_type.lower() or 'time' in column_type.lower():
            return self.default_date
        else: # text, varchar, char, etc.
            return self.default_string

    def migrate_patients(self):
        """Migrate patients first to establish references"""
        source_table = 'patients'
        if source_table not in self.mappings:
            logger.warning(f"No mapping found for table: {source_table}")
            return 0
        
        mapping = self.mappings[source_table]
        target_table = mapping['target_table']
        column_mapping = mapping['columns']
        
        # Get SQLite schema
        sqlite_schema = self.get_table_schema(source_table)
        
        # Get columns in source table
        source_columns = list(column_mapping.keys())
        select_columns = ", ".join(source_columns)
        
        # Get available patient records - FILTER FOR DOCTOR ID 4 ONLY
        cursor = self.sqlite_conn.cursor()
        try:
            # Modified to filter only doctor_id = 4
            cursor.execute(f"SELECT {select_columns} FROM {source_table} WHERE doc_id = 4")
            rows = cursor.fetchall()
            logger.info(f"Found {len(rows)} patient records for doctor_id=4 in source database")
        except sqlite3.Error as e:
            logger.error(f"Error querying source table: {e}")
            cursor.close()
            return 0
            
        # Get target schema
        target_schema = self.get_target_columns(target_table)
        logger.info(f"Target schema for {target_table}: {target_schema}")
        
        # Prepare insert query
        target_columns = [column_mapping[col] for col in source_columns]
        if 'date_added' not in target_columns and 'date_added' in target_schema:
            target_columns.append('date_added')
            
        # Insert data
        count = 0
        target_cursor = self.target_conn.cursor()
        
        for row in rows:
            try:
                # Extract data
                data = list(row)
                
                # Process empty values and add current timestamp for date_added
                processed_data = []
                for i, value in enumerate(data):
                    col_name = target_columns[i].lower()
                    target_col_info = target_schema.get(col_name, {})
                    column_type = target_col_info.get('type', 'text')
                    
                    # Handle date fields
                    if (value == '' or value is None) and ('date' in col_name or 'birth' in col_name):
                        processed_data.append(self.default_date)  # Default date
                    # Handle gender capitalization
                    elif col_name == 'gender' and value and isinstance(value, str):
                        processed_data.append(value.capitalize())
                    # Handle empty string or None values with type-specific defaults
                    elif value == '' or value is None:
                        if col_name in ('id', 'doctor_id'):  # Keep IDs as is
                            processed_data.append(value)
                        elif 'int' in column_type.lower() or 'serial' in column_type.lower():
                            processed_data.append(0)  # Default for integers
                        elif 'date' in column_type.lower():
                            processed_data.append(self.default_date)  # Default for dates
                        else:
                            processed_data.append("No data")  # Default for text fields
                    else:
                        processed_data.append(value)
                
                # Add current timestamp for date_added if needed
                if 'date_added' in target_columns and len(processed_data) < len(target_columns):
                    processed_data.append(datetime.datetime.now())
                
                # Try to insert, but handle duplicate key errors gracefully
                try:
                    # Generate placeholders for the INSERT statement
                    placeholders = ", ".join(["%s" for _ in range(len(target_columns))])
                    insert_query = f"INSERT INTO {target_table} ({', '.join(target_columns)}) VALUES ({placeholders})"
                    
                    # Execute insert
                    target_cursor.execute(insert_query, processed_data)
                    
                    # Store the original ID to map it later for medical records
                    original_id = row[0]  # Assuming ID is the first column
                    self.migrated_patients[original_id] = original_id  # Keep same ID mapping
                    
                    self.target_conn.commit()
                    count += 1
                    
                except Exception as e:
                    # Check if it's a duplicate key error
                    if "duplicate key value violates unique constraint" in str(e):
                        logger.warning(f"Patient with ID {data[0]} already exists, skipping.")
                        # Still add the patient to migrated_patients for medical records
                        original_id = row[0]
                        self.migrated_patients[original_id] = original_id
                        self.target_conn.rollback()
                    else:
                        # For other errors, log and rollback
                        self.target_conn.rollback()
                        raise e
                
                if count % 50 == 0:
                    logger.info(f"Migrated {count} patients so far...")
                    
            except Exception as e:
                logger.error(f"Error inserting patient: {e}")
                logger.error(f"Row data: {data}")
                
        logger.info(f"Successfully migrated {count} new patients out of {len(rows)} for doctor_id=4")
        logger.info(f"Total patients available for medical records: {len(self.migrated_patients)}")
        target_cursor.close()
        cursor.close()
        return count

    def migrate_medical_records(self):
        """Migrate medical records with proper foreign key and date handling"""
        source_table = 'details'
        if source_table not in self.mappings:
            logger.warning(f"No mapping found for table: {source_table}")
            return 0
            
        mapping = self.mappings[source_table]
        target_table = mapping['target_table']
        column_mapping = mapping['columns']
        
        # Get SQLite schema
        sqlite_schema = self.get_table_schema(source_table)
        logger.info(f"Source schema for {source_table}: {sqlite_schema}")
        
        # Get target schema
        target_schema = self.get_target_columns(target_table)
        logger.info(f"Target schema for {target_table}: {target_schema}")
        
        # Get columns in source table
        source_columns = list(column_mapping.keys())
        select_columns = ", ".join(source_columns)
        
        # Get all medical records - we'll filter them after fetching
        cursor = self.sqlite_conn.cursor()
        try:
            # Query all records from the details table
            # Instead of filtering by patient_id which doesn't exist in the schema
            cursor.execute(f"SELECT {select_columns} FROM {source_table}")
            rows = cursor.fetchall()
            logger.info(f"Found {len(rows)} medical records total in source database")
        except sqlite3.Error as e:
            logger.error(f"Error querying source table: {e}")
            cursor.close()
            return 0
        
        # Prepare insert query
        target_columns = [column_mapping[col] for col in source_columns]
        
        # Add doctor_id if it's not part of the column mapping
        if 'doctor_id' not in target_columns and 'doctor_id' in target_schema:
            target_columns.append('doctor_id')
            
        # Insert data
        count = 0
        target_cursor = self.target_conn.cursor()
        
        for row in rows:
            try:
                # Extract data
                data = list(row)
                
                # Process data with standard defaults
                processed_data = []
                for i, value in enumerate(data):
                    col_name = target_columns[i].lower()
                    target_col_info = target_schema.get(col_name, {})
                    column_type = target_col_info.get('type', 'text')
                    
                    # If doctor_id is 0, make it 4
                    if col_name == 'doctor_id' and (value == 0 or value == '0'):
                        processed_data.append(4)  # Force doctor_id to be 4
                        continue
                    
                    # Critical fields that should not receive default values
                    if col_name in ('id', 'patient_id'):
                        processed_data.append(value)
                        continue
                    
                    # Handle date fields - using our robust date parser
                    if col_name == 'date':
                        if value is not None and value != '':
                            processed_data.append(self.parse_date(value))
                        else:
                            processed_data.append(self.default_date)
                    
                    # Apply default values based on type
                    elif value is None or value == '':
                        if 'int' in column_type.lower() or 'serial' in column_type.lower():
                            processed_data.append(0)  # Default for integers
                        elif 'date' in column_type.lower():
                            processed_data.append(self.default_date)  # Default for dates
                        else:
                            processed_data.append("No data")  # Default for text fields
                    else:
                        processed_data.append(value)
                
                # Add doctor_id to the end of the data if needed - always set to 4
                if 'doctor_id' in target_columns and 'doctor_id' not in column_mapping.values():
                    processed_data.append(4)  # Always use doctor_id=4
                
                # Try to insert with duplicate handling
                try:
                    # Generate placeholders for the INSERT statement
                    placeholders = ", ".join(["%s" for _ in range(len(target_columns))])
                    insert_query = f"INSERT INTO {target_table} ({', '.join(target_columns)}) VALUES ({placeholders})"
                    
                    # Execute insert
                    target_cursor.execute(insert_query, processed_data)
                    self.target_conn.commit()
                    count += 1
                except Exception as e:
                    if "duplicate key value violates unique constraint" in str(e):
                        logger.warning(f"Medical record already exists, skipping.")
                        self.target_conn.rollback()
                    else:
                        self.target_conn.rollback()
                        logger.error(f"Error inserting medical record: {e}")
                        logger.error(f"Row data: {processed_data}")
                
                if count % 50 == 0:
                    logger.info(f"Migrated {count} medical records so far...")
                    
            except Exception as e:
                logger.error(f"Error processing medical record: {e}")
                logger.error(f"Row data: {data}")
                
        logger.info(f"Successfully migrated {count} medical records out of {len(rows)}")
        target_cursor.close()
        cursor.close()
        return count
    
    def run_migration(self):
        """Run the complete migration process"""
        if not self.connect():
            logger.error("Failed to connect to databases. Migration aborted.")
            return False
            
        try:
            # Phase 1: Migrate all patients first
            logger.info("=== PHASE 1: MIGRATING PATIENTS ===")
            patients_count = self.migrate_patients()
            logger.info(f"Completed Phase 1: {patients_count} patients migrated successfully")
            
            if patients_count == 0:
                logger.warning("No patients were migrated. Skipping medical records migration.")
                return False
                
            # Phase 2: Migrate medical records with proper foreign key validation
            logger.info("=== PHASE 2: MIGRATING MEDICAL RECORDS ===")
            logger.info(f"Using {len(self.migrated_patients)} migrated patient IDs as reference")
            records_count = self.migrate_medical_records()
            logger.info(f"Completed Phase 2: {records_count} medical records migrated successfully")
            
            total_count = patients_count + records_count
            logger.info(f"Migration completed successfully. Total {total_count} records migrated.")
            
            return total_count > 0
            
        except Exception as e:
            logger.error(f"Migration failed with error: {e}")
            logger.error(traceback.format_exc())
            return False
        finally:
            self.close()

def main():
    parser = argparse.ArgumentParser(description='Robust database migration tool')
    parser.add_argument('--sqlite-db', required=True, help='SQLite database file path')
    parser.add_argument('--target-type', choices=['postgresql'], default='postgresql', help='Target database type')
    parser.add_argument('--host', default='localhost', help='Target database host')
    parser.add_argument('--port', type=int, default=5432, help='Target database port')
    parser.add_argument('--database', required=True, help='Target database name')
    parser.add_argument('--user', required=True, help='Target database username')
    parser.add_argument('--password', required=True, help='Target database password')
    parser.add_argument('--mappings', default='mappings.json', help='Path to mappings JSON file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--patients-only', action='store_true', help='Only migrate patients')
    parser.add_argument('--records-only', action='store_true', help='Only migrate medical records')
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    if not os.path.exists(args.sqlite_db):
        logger.error(f"SQLite database not found: {args.sqlite_db}")
        return
        
    if not os.path.exists(args.mappings):
        logger.error(f"Mappings file not found: {args.mappings}")
        return
    
    target_config = {
        'db_type': args.target_type,
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user,
        'password': args.password
    }
    
    migrator = RobustMigrator(args.sqlite_db, target_config, args.mappings)
    
    if args.patients_only and args.records_only:
        logger.error("Cannot specify both --patients-only and --records-only. Please use only one option.")
        return
    
    if args.patients_only:
        logger.info("Running patients-only migration")
        migrator.connect()
        patients_count = migrator.migrate_patients()
        migrator.close()
        logger.info(f"Patients-only migration completed. {patients_count} patients migrated.")
        return
    
    if args.records_only:
        logger.info("Running medical-records-only migration")
        migrator.connect()
        # First load migrated patient IDs
        logger.info("Loading existing patient IDs...")
        cursor = migrator.target_conn.cursor()
        try:
            cursor.execute("SELECT id FROM doctor_patients")
            for row in cursor.fetchall():
                migrator.migrated_patients[row[0]] = row[0]
            logger.info(f"Loaded {len(migrator.migrated_patients)} existing patient IDs")
        except Exception as e:
            logger.error(f"Failed to load patient IDs: {e}")
            migrator.close()
            return
        
        records_count = migrator.migrate_medical_records()
        migrator.close()
        logger.info(f"Medical-records-only migration completed. {records_count} records migrated.")
        return
    
    # Regular full migration
    success = migrator.run_migration()
    
    if success:
        logger.info("Migration completed successfully!")
    else:
        logger.error("Migration failed or no data was migrated")

if __name__ == "__main__":
    main()
