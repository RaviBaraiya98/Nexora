#!/usr/bin/env python3
"""
HARMOGEN-R Dataset CSV Export Script
===================================
This script exports data from the HARMOGEN-R dataset to CSV format for analysis.
It executes three main queries used in the study for rubric comparison analysis.

Author: HARMOGEN-R Research Team
Date: 2025
License: CC BY 4.0
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
import warnings

# Suppress pandas SQLAlchemy warning
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy')


class HARMOGENCSVExporter:
    """
    Export HARMOGEN-R dataset to CSV files.
    """
    
    def __init__(self, host='localhost', database='dataset_article', 
                 user='root', password='', port=3306, output_dir='datasets'):
        """
        Initialize database connection parameters and output directory.
        
        Args:
            host: MySQL host address
            database: Database name
            user: MySQL username
            password: MySQL password
            port: MySQL port
            output_dir: Directory to save CSV files (default: 'datasets')
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.output_dir = output_dir
        self.connection = None
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"✓ Created output directory: {self.output_dir}/")
        else:
            print(f"✓ Using existing output directory: {self.output_dir}/")
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            print(f"✓ Successfully connected to database '{self.database}'")
            return True
        except Error as e:
            print(f"✗ Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Database connection closed")
    
    def export_1_rubric_comparison_by_assignment(self, assignment_id=7):
        """
        Export 1: Rubric comparison for final evaluations in a specific assignment.
        
        This query extracts final evaluation scores for a specific assignment,
        showing how different evaluators (teachers and selected LLMs) scored
        student responses across different rubric sources.
        
        Args:
            assignment_id: ID of the assignment to export (default: 7)
        """
        print("\n" + "="*60)
        print(f"EXPORT 1: Rubric Comparison for Assignment {assignment_id}")
        print("="*60)
        
        query = """
        SELECT 
            fe.evaluator_id,
            fe.evaluator_type,
            q.id as question_id,
            q.type,
            sr.id as response_id,
            fe.source_question_criteria as source,
            fe.final_score as score
        FROM assignments a
        INNER JOIN questions q ON q.assignment_id = a.id
        INNER JOIN student_responses sr ON sr.question_id = q.id
        INNER JOIN final_evaluations fe ON fe.response_id = sr.id
        WHERE 
            a.id = %s
            AND (
                (fe.evaluator_type = 'teacher')
                OR 
                (fe.evaluator_type = 'llm' AND fe.evaluator_id IN (1, 4, 13))
            )
            AND a.is_active = 1
            AND q.is_active = 1
            AND sr.is_active = 1
            AND fe.is_active = 1
        ORDER BY 
            fe.evaluator_id,
            q.id, 
            sr.id, 
            fe.source_question_criteria
        """
        
        # Execute query and save to CSV
        df = pd.read_sql(query, self.connection, params=(assignment_id,))
        
        # Convert ID columns to nullable integers (Int64)
        id_columns = ['evaluator_id', 'question_id', 'response_id', 'source']
        for col in id_columns:
            if col in df.columns:
                df[col] = df[col].astype('Int64')
        
        filename = f"rubric_comparison_final_evaluations_assignment_{assignment_id}.csv"
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"✓ Exported: {filename}")
        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Path: {filepath}")
    
    def export_2_all_evaluations_wide_format(self, assignment_id=7):
        """
        Export 2: All evaluations in wide format for a specific assignment.
        
        This query creates a wide-format dataset where each row represents a
        student response with columns for each evaluator's scores (4 teachers
        and 3 LLMs with 3 evaluations each).
        
        Args:
            assignment_id: ID of the assignment to export (default: 7)
        """
        print("\n" + "="*60)
        print(f"EXPORT 2: All Evaluations Wide Format for Assignment {assignment_id}")
        print("="*60)
        
        query = """
        SELECT 
            sr.id as response_id,
            q.id as question_id,
            q.type as question_type,
            base.source_question_criteria,
            -- Teacher scores
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'teacher' AND is_active = 1 ORDER BY evaluator_id LIMIT 1) as teacher_1_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'teacher' AND is_active = 1 ORDER BY evaluator_id LIMIT 1,1) as teacher_2_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'teacher' AND is_active = 1 ORDER BY evaluator_id LIMIT 2,1) as teacher_3_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'teacher' AND is_active = 1 ORDER BY evaluator_id LIMIT 3,1) as teacher_4_score,
            -- LLM 1 scores
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 1 AND is_active = 1 ORDER BY created_at, id LIMIT 1) as llm1_eval1_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 1 AND is_active = 1 ORDER BY created_at, id LIMIT 1,1) as llm1_eval2_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 1 AND is_active = 1 ORDER BY created_at, id LIMIT 2,1) as llm1_eval3_score,
            -- LLM 4 scores
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 4 AND is_active = 1 ORDER BY created_at, id LIMIT 1) as llm4_eval1_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 4 AND is_active = 1 ORDER BY created_at, id LIMIT 1,1) as llm4_eval2_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 4 AND is_active = 1 ORDER BY created_at, id LIMIT 2,1) as llm4_eval3_score,
            -- LLM 13 scores
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 13 AND is_active = 1 ORDER BY created_at, id LIMIT 1) as llm13_eval1_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 13 AND is_active = 1 ORDER BY created_at, id LIMIT 1,1) as llm13_eval2_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 13 AND is_active = 1 ORDER BY created_at, id LIMIT 2,1) as llm13_eval3_score
        FROM assignments a
        INNER JOIN questions q ON q.assignment_id = a.id
        INNER JOIN student_responses sr ON sr.question_id = q.id
        INNER JOIN (
            SELECT DISTINCT student_response_id, source_question_criteria 
            FROM evaluations 
            WHERE is_active = 1 
            AND (evaluator_type = 'teacher' OR (evaluator_type = 'llm' AND evaluator_id IN (1, 4, 13)))
        ) base ON base.student_response_id = sr.id
        WHERE
            a.id = %s
            AND a.is_active = 1
            AND q.is_active = 1
            AND sr.is_active = 1
        ORDER BY
            sr.id,
            base.source_question_criteria
        """
        
        # Execute query and save to CSV
        df = pd.read_sql(query, self.connection, params=(assignment_id,))
        
        # Convert ID columns to nullable integers (Int64)
        id_columns = ['response_id', 'question_id', 'source_question_criteria']
        for col in id_columns:
            if col in df.columns:
                df[col] = df[col].astype('Int64')
        
        filename = f"all_evaluations_wide_format_assignment_{assignment_id}.csv"
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"✓ Exported: {filename}")
        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Path: {filepath}")
    
    def export_3_all_evaluations_wide_format_all_assignments(self):
        """
        Export 3: All evaluations in wide format for ALL assignments.
        
        Similar to Export 2 but includes all assignments with assignment_id column.
        """
        print("\n" + "="*60)
        print("EXPORT 3: All Evaluations Wide Format - All Assignments")
        print("="*60)
        
        query = """
        SELECT 
            a.id as assignment_id,
            sr.id as response_id,
            q.id as question_id,
            q.type as question_type,
            base.source_question_criteria,
            -- Teacher scores
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'teacher' AND is_active = 1 ORDER BY evaluator_id LIMIT 1) as teacher_1_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'teacher' AND is_active = 1 ORDER BY evaluator_id LIMIT 1,1) as teacher_2_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'teacher' AND is_active = 1 ORDER BY evaluator_id LIMIT 2,1) as teacher_3_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'teacher' AND is_active = 1 ORDER BY evaluator_id LIMIT 3,1) as teacher_4_score,
            -- LLM 1 scores
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 1 AND is_active = 1 ORDER BY created_at, id LIMIT 1) as llm1_eval1_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 1 AND is_active = 1 ORDER BY created_at, id LIMIT 1,1) as llm1_eval2_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 1 AND is_active = 1 ORDER BY created_at, id LIMIT 2,1) as llm1_eval3_score,
            -- LLM 4 scores
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 4 AND is_active = 1 ORDER BY created_at, id LIMIT 1) as llm4_eval1_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 4 AND is_active = 1 ORDER BY created_at, id LIMIT 1,1) as llm4_eval2_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 4 AND is_active = 1 ORDER BY created_at, id LIMIT 2,1) as llm4_eval3_score,
            -- LLM 13 scores
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 13 AND is_active = 1 ORDER BY created_at, id LIMIT 1) as llm13_eval1_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 13 AND is_active = 1 ORDER BY created_at, id LIMIT 1,1) as llm13_eval2_score,
            (SELECT ROUND(score, 2) FROM evaluations WHERE student_response_id = sr.id AND source_question_criteria = base.source_question_criteria AND evaluator_type = 'llm' AND evaluator_id = 13 AND is_active = 1 ORDER BY created_at, id LIMIT 2,1) as llm13_eval3_score
        FROM assignments a
        INNER JOIN questions q ON q.assignment_id = a.id
        INNER JOIN student_responses sr ON sr.question_id = q.id
        INNER JOIN (
            SELECT DISTINCT student_response_id, source_question_criteria 
            FROM evaluations 
            WHERE is_active = 1 
            AND (evaluator_type = 'teacher' OR (evaluator_type = 'llm' AND evaluator_id IN (1, 4, 13)))
        ) base ON base.student_response_id = sr.id
        WHERE
            a.is_active = 1
            AND q.is_active = 1
            AND sr.is_active = 1
        ORDER BY
            a.id,
            q.id,
            sr.id,
            base.source_question_criteria
        """
        
        # Execute query and save to CSV
        df = pd.read_sql(query, self.connection)
        
        # Convert ID columns to nullable integers (Int64)
        id_columns = ['assignment_id', 'response_id', 'question_id', 'source_question_criteria']
        for col in id_columns:
            if col in df.columns:
                df[col] = df[col].astype('Int64')
        
        filename = "all_evaluations_wide_format_all_assignments.csv"
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"✓ Exported: {filename}")
        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Path: {filepath}")


def main():
    """Main execution function."""
    # Database configuration
    config = {
        'host': 'localhost',
        'database': 'dataset_article',
        'user': 'root',
        'password': '',  # Update with your password
        'port': 3306,
        'output_dir': 'datasets'  # Output directory for CSV files
    }
    
    # Create exporter instance
    exporter = HARMOGENCSVExporter(**config)
    
    # Connect to database
    if not exporter.connect():
        return
    
    try:
        # Run the three exports
        exporter.export_1_rubric_comparison_by_assignment(assignment_id=7)
        exporter.export_2_all_evaluations_wide_format(assignment_id=7)
        exporter.export_3_all_evaluations_wide_format_all_assignments()
        
        print("\n" + "="*60)
        print("✓ CSV EXPORT COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Files saved in: {os.path.abspath(exporter.output_dir)}/")
        
    except Exception as e:
        print(f"\n✗ Error during export: {e}")
        import traceback
        traceback.print_exc()
    finally:
        exporter.disconnect()


if __name__ == "__main__":
    main()