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
    def __init__(self, sqlite_db_path, target_db_config, mappings_file, skip_invalid_doctors=False):
        self.sqlite_db_path = sqlite_db_path
        self.target_db_config = target_db_config
        self.target_db_type = target_db_config.get('db_type', 'postgresql')
        self.skip_invalid_doctors = skip_invalid_doctors
        
        # Load mappings from file
        with open(mappings_file, 'r') as f:
            self.mappings = json.load(f)
            
        self.sqlite_conn = None
        self.target_conn = None
        
        # Track successfully migrated patients
        self.migrated_patients = {}
        # Track available doctor IDs
        self.available_doctor_ids = set()
        # Track skipped records due to doctor ID issues
        self.skipped_records = {
            'patients': [],
            'medical_records': []
        }
        
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
            elif self.target_db_type.lower() == 'mysql':
                import mysql.connector
                self.target_conn = mysql.connector.connect(
                    host=self.target_db_config.get('host', 'localhost'),
                    database=self.target_db_config.get('database'),
                    user=self.target_db_config.get('user'),
                    password=self.target_db_config.get('password'),
                    port=self.target_db_config.get('port', 3306)
                )
                logger.info(f"Connected to MySQL database: {self.target_db_config.get('database')}")
            else:
                logger.error(f"Unsupported target database type: {self.target_db_type}")
                return False
                
            # After successful connection, load available doctor IDs
            if self.target_conn:
                self.load_available_doctor_ids()
                
            return True
        except Exception as e:
            logger.error(f"Error connecting to databases: {e}")
            self.close()
            return False
    
    def load_available_doctor_ids(self):
        """Load available doctor IDs from target database"""
        try:
            cursor = self.target_conn.cursor()
            cursor.execute("SELECT id FROM doctor_doctorprofile")
            self.available_doctor_ids = {row[0] for row in cursor.fetchall()}
            logger.info(f"Loaded {len(self.available_doctor_ids)} available doctor IDs: {self.available_doctor_ids}")
            cursor.close()
        except Exception as e:
            logger.error(f"Error loading doctor IDs: {e}")
            self.available_doctor_ids = {4}  # Default to doctor ID 4 if query fails
    
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
        """Get the columns of a target database table"""
        cursor = self.target_conn.cursor()
        
        if self.target_db_type.lower() == 'postgresql':
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
            """, (table_name,))
        elif self.target_db_type.lower() == 'mysql':
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s AND table_schema = %s
            """, (table_name, self.target_db_config.get('database')))
            
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
        
        # Get all patients
        cursor = self.sqlite_conn.cursor()
        try:
            cursor.execute(f"SELECT {select_columns} FROM {source_table}")
            rows = cursor.fetchall()
            logger.info(f"Found {len(rows)} patient records in source database")
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
                
                # Find doctor_id in the data
                doc_id_idx = None
                for i, col in enumerate(source_columns):
                    mapped_col = column_mapping[col].lower()
                    if mapped_col == 'doctor_id':
                        doc_id_idx = i
                
                # Check if doctor_id exists in target database
                if doc_id_idx is not None:
                    doctor_id = data[doc_id_idx] if data[doc_id_idx] else 0
                    if doctor_id and int(doctor_id) not in self.available_doctor_ids:
                        if self.skip_invalid_doctors:
                            # Skip this patient because doctor doesn't exist
                            self.skipped_records['patients'].append({
                                'id': data[0],
                                'name': data[source_columns.index('name')] if 'name' in source_columns else 'Unknown',
                                'doctor_id': doctor_id,
                                'reason': f"Doctor ID {doctor_id} not found in target database"
                            })
                            logger.warning(f"Skipping patient with ID {data[0]} - doctor ID {doctor_id} not found in target database")
                            continue
                
                # Process empty values and add current timestamp for date_added
                processed_data = []
                for i, value in enumerate(data):
                    col_name = target_columns[i].lower()
                    target_col_info = target_schema.get(col_name, {})
                    column_type = target_col_info.get('type', 'text')
                    
                    # Handle doctor_id specifically
                    if col_name == 'doctor_id':
                        doc_id = value if value else 0
                        # If doctor ID exists in target system, use it, otherwise default to 4
                        if doc_id and int(doc_id) in self.available_doctor_ids:
                            processed_data.append(int(doc_id))
                        else:
                            processed_data.append(4)  # Default to doctor_id=4
                        continue
                    
                    # Handle date fields
                    if (value == '' or value is None) and ('date' in col_name or 'birth' in col_name):
                        processed_data.append(self.default_date)  # Default date
                    # Handle gender capitalization
                    elif col_name == 'gender' and value and isinstance(value, str):
                        processed_data.append(value.capitalize())
                    # Handle empty string or None values with type-specific defaults
                    elif value == '' or value is None:
                        if col_name in ('id'):  # Keep IDs as is
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
                
        logger.info(f"Successfully migrated {count} new patients out of {len(rows)}")
        logger.info(f"Total patients available for medical records: {len(self.migrated_patients)}")
        target_cursor.close()
        cursor.close()
        
        # Log statistics about skipped records
        if self.skipped_records['patients']:
            logger.warning(f"Skipped {len(self.skipped_records['patients'])} patients due to missing doctor IDs")
        
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
        
        # Get all medical records without filtering
        cursor = self.sqlite_conn.cursor()
        try:
            # Get all medical records without filtering
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
                
                # Find doctor_id in the data (assume it's at column 'doc_id' or similar)
                doc_id_idx = None
                for i, col in enumerate(source_columns):
                    if col.lower() in ('doc_id', 'doctor_id'):
                        doc_id_idx = i
                        break
                
                # Get the doctor ID value
                original_doctor_id = None
                if doc_id_idx is not None:
                    original_doctor_id = data[doc_id_idx]
                
                # Check if doctor exists in target database
                if original_doctor_id and int(original_doctor_id) not in self.available_doctor_ids and self.skip_invalid_doctors:
                    # Skip this record because doctor doesn't exist
                    self.skipped_records['medical_records'].append({
                        'id': data[0],
                        'patient_id': data[1] if len(data) > 1 else 'Unknown',
                        'doctor_id': original_doctor_id,
                        'reason': f"Doctor ID {original_doctor_id} not found in target database"
                    })
                    logger.warning(f"Skipping medical record with ID {data[0]} - doctor ID {original_doctor_id} not found in target database")
                    continue
                
                # Process data with standard defaults
                processed_data = []
                for i, value in enumerate(data):
                    col_name = target_columns[i].lower()
                    target_col_info = target_schema.get(col_name, {})
                    column_type = target_col_info.get('type', 'text')
                    
                    # Handle doctor_id specifically
                    if col_name == 'doctor_id':
                        # If original doctor ID exists in target system, use it
                        if original_doctor_id and int(original_doctor_id) in self.available_doctor_ids:
                            processed_data.append(int(original_doctor_id))
                        else:
                            # Otherwise use doctor_id=4 as default
                            processed_data.append(4)
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
                
                # Add doctor_id to the end of the data if needed
                if 'doctor_id' in target_columns and 'doctor_id' not in column_mapping.values():
                    # If original doctor ID exists in target system, use it
                    if original_doctor_id and int(original_doctor_id) in self.available_doctor_ids:
                        processed_data.append(int(original_doctor_id))
                    else:
                        # Otherwise use doctor_id=4 as default
                        processed_data.append(4)
                
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
        
        # Log statistics about skipped records
        if self.skipped_records['medical_records']:
            logger.warning(f"Skipped {len(self.skipped_records['medical_records'])} medical records due to missing doctor IDs")
        
        return count
    
    def export_skipped_records(self, filename="skipped_records.json"):
        """Export information about skipped records to a JSON file"""
        if not any(self.skipped_records.values()):
            logger.info("No records were skipped during migration")
            return
            
        try:
            with open(filename, 'w') as f:
                json.dump(self.skipped_records, f, indent=2)
            logger.info(f"Exported information about skipped records to {filename}")
        except Exception as e:
            logger.error(f"Error exporting skipped records: {e}")
    
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
            
            # Export information about skipped records
            if self.skip_invalid_doctors:
                self.export_skipped_records()
            
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
    parser.add_argument('--target-type', choices=['postgresql', 'mysql'], default='postgresql', help='Target database type')
    parser.add_argument('--host', default='localhost', help='Target database host')
    parser.add_argument('--port', type=int, help='Target database port (default: 5432 for PostgreSQL, 3306 for MySQL)')
    parser.add_argument('--database', required=True, help='Target database name')
    parser.add_argument('--user', required=True, help='Target database username')
    parser.add_argument('--password', required=True, help='Target database password')
    parser.add_argument('--mappings', default='mappings.json', help='Path to mappings JSON file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--patients-only', action='store_true', help='Only migrate patients')
    parser.add_argument('--records-only', action='store_true', help='Only migrate medical records')
    parser.add_argument('--skip-invalid-doctors', action='store_true', help='Skip records with invalid doctor IDs instead of defaulting to doctor_id=4')
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    if not args.port:
        # Set default port based on database type
        args.port = 3306 if args.target_type.lower() == 'mysql' else 5432
    
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
    
    migrator = RobustMigrator(args.sqlite_db, target_config, args.mappings, args.skip_invalid_doctors)
    
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
