#!/usr/bin/env python3
"""
HARMOGEN Dataset Normalization Script
======================================
This script normalizes the exported HARMOGEN-R datasets to a 0-100 scale
and ensures correct question type classifications.

Author: HARMOGEN-R Research Team
Date: 2025
License: CC BY 4.0
"""

import pandas as pd
import numpy as np
import os
import sys
from typing import Dict, List, Tuple, Optional

class HARMOGENDataNormalizer:
    """
    Normalizes HARMOGEN-R dataset scores to 0-100 scale and fixes question types.
    """
    
    def __init__(self):
        """Initialize the normalizer with question metadata."""
        
        # Define question max scores for all assignments
        self.max_scores = {
            # Assignment 7
            21: 50,   # Text/longtext
            22: 20,   # Multiple choice
            23: 20,   # Multiple choice
            24: 20,   # Multiple choice
            25: 90,   # Code
            # Assignment 8
            26: 50,   # Text/longtext
            27: 20,   # Multiple choice
            28: 20,   # Multiple choice
            29: 20,   # Multiple choice
            31: 90,   # Code (note: no question 30)
            # Assignment 9
            32: 50,   # Text/longtext
            38: 20,   # Multiple choice
            39: 20,   # Multiple choice
            40: 20,   # Multiple choice
            41: 90    # Code
        }
        
        # Define which questions should be Multiple choice
        self.mc_questions = [22, 23, 24, 27, 28, 29, 38, 39, 40]
        
        # Define which questions are code
        self.code_questions = [25, 31, 41]
        
        # Define which questions are text/longtext
        self.text_questions = [21, 26, 32]
        
        # Rubric source mapping
        self.rubric_sources = {
            1: 'Human',
            2: 'OpenAI Hybrid LLMs structured',
            3: 'OpenAI Hybrid LLMs free',
            4: 'DeepSeek Hybrid LLM structured',
            5: 'DeepSeek Hybrid LLM free'
        }
    
    def _infer_question_type(self, question_id: int) -> str:
        """Infer question type based on question ID."""
        if question_id in self.mc_questions:
            return 'text'  # Multiple choice questions are stored as 'text' in the database
        elif question_id in self.code_questions:
            return 'code'
        elif question_id in self.text_questions:
            return 'text'  # Text questions are also stored as 'text' 
        else:
            return 'unknown'
    
    def normalize_wide_format_dataset(self, input_filepath: str, output_filepath: Optional[str] = None) -> str:
        """
        Normalize wide format datasets (all_evaluations_wide_format files).
        
        These files have columns:
        - assignment_id (optional), response_id, question_id, question_type, source_question_criteria
        - teacher_1_score through teacher_4_score
        - llm1_eval1_score through llm13_eval3_score
        """
        print(f"\n{'='*60}")
        print(f"Processing Wide Format: {input_filepath}")
        print(f"{'='*60}")
        
        # Load data
        try:
            df = pd.read_csv(input_filepath)
            print(f"✓ Successfully loaded data: {len(df):,} rows × {len(df.columns)} columns")
        except Exception as e:
            print(f"✗ Error loading CSV: {e}")
            return None
        
        # Display original data info
        print(f"\n📊 Original Data Summary:")
        print(f"   Total rows: {len(df):,}")
        if 'assignment_id' in df.columns:
            print(f"   Unique assignments: {df['assignment_id'].nunique()}")
        print(f"   Unique questions: {df['question_id'].nunique()}")
        print(f"   Unique responses: {df['response_id'].nunique()}")
        print(f"   Unique rubric sources: {sorted(df['source_question_criteria'].unique())}")
        
        # Create a copy for normalization
        df_normalized = df.copy()
        
        # Fix question types if needed
        print(f"\n🔧 Step 1: Checking question types...")
        if 'question_type' in df_normalized.columns:
            # The question_type column exists - just verify it's correct
            print("   Question types found in data:")
            for q_id in sorted(df_normalized['question_id'].unique()):
                q_type = df_normalized[df_normalized['question_id'] == q_id]['question_type'].iloc[0]
                expected_type = self._infer_question_type(q_id)
                if q_type != expected_type and expected_type != 'unknown':
                    print(f"     Question {q_id}: {q_type} (fixing to {expected_type})")
                    df_normalized.loc[df_normalized['question_id'] == q_id, 'question_type'] = expected_type
                else:
                    print(f"     Question {q_id}: {q_type} ✓")
        
        # Normalize scores
        print(f"\n🔧 Step 2: Normalizing scores to 0-100 scale...")
        score_columns = [col for col in df_normalized.columns if col.endswith('_score')]
        print(f"   Found {len(score_columns)} score columns to normalize")
        
        normalization_stats = {}
        for q_id in sorted(df_normalized['question_id'].unique()):
            if q_id in self.max_scores:
                max_score = self.max_scores[q_id]
                q_mask = df_normalized['question_id'] == q_id
                rows_affected = q_mask.sum()
                
                # Normalize each score column for this question
                for col in score_columns:
                    # Apply normalization: (score / max_score) * 100
                    df_normalized.loc[q_mask, col] = df_normalized.loc[q_mask, col].apply(
                        lambda x: round((x / max_score) * 100, 2) if pd.notna(x) else x
                    )
                
                normalization_stats[q_id] = {'max_score': max_score, 'rows': rows_affected}
                print(f"     Question {q_id}: normalized {rows_affected} rows (max score: {max_score})")
        
        # Verify integrity
        print(f"\n🔧 Step 3: Verifying data integrity...")
        issues = 0
        for col in score_columns:
            over_100 = (df_normalized[col] > 100).sum()
            under_0 = (df_normalized[col] < 0).sum()
            if over_100 > 0:
                print(f"   ⚠️ {over_100} scores > 100% in {col}")
                issues += over_100
            if under_0 > 0:
                print(f"   ⚠️ {under_0} scores < 0% in {col}")
                issues += under_0
        
        if issues == 0:
            print("   ✓ All normalized scores are within 0-100% range")
        
        # Save normalized data
        if output_filepath is None:
            input_dir = os.path.dirname(input_filepath)
            input_basename = os.path.basename(input_filepath)
            output_basename = input_basename.replace('.csv', '_normalized.csv')
            output_filepath = os.path.join(input_dir, output_basename)
        
        try:
            df_normalized.to_csv(output_filepath, index=False)
            print(f"\n✓ Normalized data saved to: {output_filepath}")
        except Exception as e:
            print(f"✗ Error saving normalized data: {e}")
            return None
        
        # Summary
        print(f"\n📊 Final Summary:")
        print(f"   Input rows: {len(df):,}")
        print(f"   Output rows: {len(df_normalized):,}")
        print(f"   Questions normalized: {len(normalization_stats)}")
        
        return output_filepath
    
    def normalize_rubric_comparison_dataset(self, input_filepath: str, output_filepath: Optional[str] = None) -> str:
        """
        Normalize rubric comparison dataset (rubric_comparison_final_evaluations files).
        
        These files have columns:
        - evaluator_id, evaluator_type, question_id, type, response_id, source, score
        """
        print(f"\n{'='*60}")
        print(f"Processing Rubric Comparison: {input_filepath}")
        print(f"{'='*60}")
        
        # Load data
        try:
            df = pd.read_csv(input_filepath)
            print(f"✓ Successfully loaded data: {len(df):,} rows × {len(df.columns)} columns")
        except Exception as e:
            print(f"✗ Error loading CSV: {e}")
            return None
        
        # Display original data info
        print(f"\n📊 Original Data Summary:")
        print(f"   Total rows: {len(df):,}")
        print(f"   Unique questions: {df['question_id'].nunique()}")
        print(f"   Unique responses: {df['response_id'].nunique()}")
        print(f"   Unique rubric sources: {sorted(df['source'].unique())}")
        print(f"   Evaluator types: {df['evaluator_type'].unique()}")
        
        # Create a copy for normalization
        df_normalized = df.copy()
        
        # Fix column names if needed
        if 'type' in df_normalized.columns and 'question_type' not in df_normalized.columns:
            df_normalized.rename(columns={'type': 'question_type'}, inplace=True)
            print("\n   ℹ️ Renamed 'type' column to 'question_type'")
        
        if 'source' in df_normalized.columns and 'source_question_criteria' not in df_normalized.columns:
            df_normalized.rename(columns={'source': 'source_question_criteria'}, inplace=True)
            print("   ℹ️ Renamed 'source' column to 'source_question_criteria'")
        
        # Normalize scores
        print(f"\n🔧 Normalizing scores to 0-100 scale...")
        
        normalization_stats = {}
        for q_id in sorted(df_normalized['question_id'].unique()):
            if q_id in self.max_scores:
                max_score = self.max_scores[q_id]
                q_mask = df_normalized['question_id'] == q_id
                rows_affected = q_mask.sum()
                
                # Normalize score column
                df_normalized.loc[q_mask, 'score'] = df_normalized.loc[q_mask, 'score'].apply(
                    lambda x: round((x / max_score) * 100, 2) if pd.notna(x) else x
                )
                
                normalization_stats[q_id] = {'max_score': max_score, 'rows': rows_affected}
                print(f"   Question {q_id}: normalized {rows_affected} rows (max score: {max_score})")
        
        # Verify integrity
        print(f"\n🔧 Verifying data integrity...")
        over_100 = (df_normalized['score'] > 100).sum()
        under_0 = (df_normalized['score'] < 0).sum()
        
        if over_100 > 0:
            print(f"   ⚠️ {over_100} scores > 100%")
        if under_0 > 0:
            print(f"   ⚠️ {under_0} scores < 0%")
        if over_100 == 0 and under_0 == 0:
            print("   ✓ All normalized scores are within 0-100% range")
        
        # Check for perfect scores in multiple choice questions
        print("\n   Multiple Choice Perfect Score Check:")
        for q_id in self.mc_questions:
            if q_id in df_normalized['question_id'].values:
                q_data = df_normalized[df_normalized['question_id'] == q_id]
                perfect_scores = (q_data['score'] == 100).sum()
                total_scores = len(q_data)
                if total_scores > 0:
                    print(f"     Question {q_id}: {perfect_scores}/{total_scores} perfect scores "
                          f"({perfect_scores/total_scores*100:.1f}%)")
        
        # Save normalized data
        if output_filepath is None:
            input_dir = os.path.dirname(input_filepath)
            input_basename = os.path.basename(input_filepath)
            output_basename = input_basename.replace('.csv', '_normalized.csv')
            output_filepath = os.path.join(input_dir, output_basename)
        
        try:
            df_normalized.to_csv(output_filepath, index=False)
            print(f"\n✓ Normalized data saved to: {output_filepath}")
        except Exception as e:
            print(f"✗ Error saving normalized data: {e}")
            return None
        
        # Summary
        print(f"\n📊 Final Summary:")
        print(f"   Input rows: {len(df):,}")
        print(f"   Output rows: {len(df_normalized):,}")
        print(f"   Questions normalized: {len(normalization_stats)}")
        
        # Show rubric source distribution
        print(f"\n   Rubric Source Distribution:")
        source_counts = df_normalized.groupby('source_question_criteria').size()
        for source_id, count in source_counts.items():
            source_name = self.rubric_sources.get(source_id, f"Unknown ({source_id})")
            print(f"     {source_name}: {count:,} rows")
        
        return output_filepath
    
    def normalize_all_exports(self, input_dir: str = 'datasets') -> List[str]:
        """
        Normalize all three exported dataset files with appropriate handling for each format.
        
        Args:
            input_dir: Directory containing the exported CSV files
        
        Returns:
            List of paths to normalized files
        """
        print("\n" + "="*80)
        print(" HARMOGEN-R DATASET NORMALIZATION ".center(80, "="))
        print("="*80)
        
        normalized_files = []
        
        # Process rubric comparison file (different format)
        rubric_file = os.path.join(input_dir, 'rubric_comparison_final_evaluations_assignment_7.csv')
        if os.path.exists(rubric_file):
            output = self.normalize_rubric_comparison_dataset(rubric_file)
            if output:
                normalized_files.append(output)
        else:
            print(f"\n⚠️ File not found: {rubric_file}")
        
        # Process wide format files
        wide_format_files = [
            'all_evaluations_wide_format_assignment_7.csv',
            'all_evaluations_wide_format_all_assignments.csv'
        ]
        
        for filename in wide_format_files:
            input_filepath = os.path.join(input_dir, filename)
            if os.path.exists(input_filepath):
                output = self.normalize_wide_format_dataset(input_filepath)
                if output:
                    normalized_files.append(output)
            else:
                print(f"\n⚠️ File not found: {input_filepath}")
        
        # Summary
        print("\n" + "="*80)
        print(" NORMALIZATION COMPLETE ".center(80, "="))
        print("="*80)
        print(f"\n✓ Successfully normalized {len(normalized_files)} files:")
        for filepath in normalized_files:
            print(f"   - {os.path.basename(filepath)}")
        
        return normalized_files


def main():
    """Main execution function."""
    
    # Create normalizer instance
    normalizer = HARMOGENDataNormalizer()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Process specific file from command line
        input_file = sys.argv[1]
        # Determine which normalization method to use based on filename
        if 'rubric_comparison' in input_file:
            normalizer.normalize_rubric_comparison_dataset(input_file)
        else:
            normalizer.normalize_wide_format_dataset(input_file)
    else:
        # Process all exported files
        normalized_files = normalizer.normalize_all_exports('datasets')
        
        if normalized_files:
            print("\n💡 Next steps:")
            print("1. Run the exploratory data analysis on normalized data:")
            print("   python harmogenr_exploratory_data_analysis.py")
            print("2. The normalized data has all scores on a 0-100 scale")
            print("3. Multiple choice questions should show high agreement patterns")
            print("\n📊 Question Type Reference:")
            print("   Multiple Choice: Questions 22, 23, 24, 27, 28, 29, 38, 39, 40 (max 20 pts → 100%)")
            print("   Code: Questions 25, 31, 41 (max 90 pts → 100%)")
            print("   Text/Long: Questions 21, 26, 32 (max 50 pts → 100%)")


if __name__ == "__main__":
    main()