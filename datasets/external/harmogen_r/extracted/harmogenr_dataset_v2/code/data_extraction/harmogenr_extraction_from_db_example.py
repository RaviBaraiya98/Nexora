#!/usr/bin/env python3
"""
HARMOGEN-R Dataset Extraction Demo Script
========================================
This script demonstrates how to extract and analyze data from the HARMOGEN-R dataset.
It includes 20+ important data extraction examples, with special focus on the 
evaluations table and JSON data processing.

Author: HARMOGEN-R Research Team
Date: 2025
License: CC BY 4.0
"""

import mysql.connector
from mysql.connector import Error
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class HARMOGENDataExtractor:
    """
    A comprehensive class for extracting and analyzing data from the HARMOGEN-R dataset.
    """
    
    def __init__(self, host='localhost', database='dataset_article', 
                 user='root', password='', port=3306):
        """
        Initialize database connection parameters.
        
        Args:
            host: MySQL host address
            database: Database name
            user: MySQL username
            password: MySQL password
            port: MySQL port
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        self.cursor = None
        
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
            self.cursor = self.connection.cursor(dictionary=True)
            print(f"✓ Successfully connected to database '{self.database}'")
            return True
        except Error as e:
            print(f"✗ Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("✓ Database connection closed")
    
    # ==================== EXTRACTION METHODS ====================
    
    def extract_1_database_overview(self):
        """Extract 1: Get overview statistics of the entire database."""
        print("\n" + "="*60)
        print("EXTRACTION 1: Database Overview Statistics")
        print("="*60)
        
        queries = {
            "Total Evaluations": "SELECT COUNT(*) as count FROM evaluations",
            "Total Student Responses": "SELECT COUNT(*) as count FROM student_responses",
            "Total Questions": "SELECT COUNT(*) as count FROM questions",
            "Total Assignments": "SELECT COUNT(*) as count FROM assignments",
            "Total LLM Models": "SELECT COUNT(*) as count FROM llms",
            "Human Evaluations": "SELECT COUNT(*) as count FROM evaluations WHERE evaluator_type='teacher'",
            "LLM Evaluations": "SELECT COUNT(*) as count FROM evaluations WHERE evaluator_type='llm'",
            "Total Question Criteria": "SELECT COUNT(*) as count FROM question_criterias",
            "Total Final Evaluations": "SELECT COUNT(*) as count FROM final_evaluations"
        }
        
        for label, query in queries.items():
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            print(f"{label}: {result['count']}")
    
    def extract_2_evaluation_by_id(self, evaluation_id=1):
        """Extract 2: Get complete evaluation details by ID, including JSON parsing."""
        print("\n" + "="*60)
        print(f"EXTRACTION 2: Complete Evaluation Details (ID={evaluation_id})")
        print("="*60)
        
        query = """
        SELECT 
            e.*,
            sr.question_id,
            sr.response,
            sr.created_at as submission_date
        FROM evaluations e
        JOIN student_responses sr ON e.student_response_id = sr.id
        WHERE e.id = %s
        """
        
        self.cursor.execute(query, (evaluation_id,))
        result = self.cursor.fetchone()
        
        if result:
            print(f"Evaluation ID: {result['id']}")
            print(f"Response ID: {result['student_response_id']}")
            print(f"Evaluator Type: {result['evaluator_type']}")
            print(f"Score: {result['score']}")
            print(f"Source Rubric Type: {result['source_question_criteria']}")
            print(f"Feedback: {result['feedback'][:100]}..." if result['feedback'] else "No feedback")
            
            # Parse JSON criteria evaluations if LLM
            if result['evaluator_type'] == 'llm' and result['criteria_evaluations_by_llm']:
                print("\n--- Criteria Evaluations (JSON) ---")
                criteria_evals = json.loads(result['criteria_evaluations_by_llm'])
                for i, criterion in enumerate(criteria_evals, 1):
                    print(f"\nCriterion {i}:")
                    print(f"  Name: {criterion.get('criterion', 'N/A')}")
                    print(f"  Score: {criterion.get('score', 'N/A')}")
                    print(f"  Justification: {criterion.get('justification', 'N/A')[:100]}...")
        else:
            print(f"No evaluation found with ID {evaluation_id}")
    
    def extract_3_llm_criteria_analysis(self):
        """Extract 3: Analyze all LLM criteria evaluations from JSON."""
        print("\n" + "="*60)
        print("EXTRACTION 3: LLM Criteria Analysis")
        print("="*60)
        
        query = """
        SELECT 
            id,
            criteria_evaluations_by_llm,
            score as total_score
        FROM evaluations 
        WHERE evaluator_type = 'llm' 
        AND criteria_evaluations_by_llm IS NOT NULL
        LIMIT 100
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        all_criteria = []
        criteria_scores = {}
        
        for row in results:
            if row['criteria_evaluations_by_llm']:
                try:
                    criteria_evals = json.loads(row['criteria_evaluations_by_llm'])
                    for criterion in criteria_evals:
                        criterion_name = criterion.get('criterion', 'Unknown')
                        score = criterion.get('score', 0)
                        
                        if criterion_name not in criteria_scores:
                            criteria_scores[criterion_name] = []
                        criteria_scores[criterion_name].append(score)
                except json.JSONDecodeError:
                    continue
        
        print(f"Total unique criteria found: {len(criteria_scores)}")
        print("\nCriteria Statistics:")
        for criterion, scores in list(criteria_scores.items())[:5]:  # Show first 5
            if scores:
                print(f"\n'{criterion}':")
                print(f"  Count: {len(scores)}")
                print(f"  Mean Score: {np.mean(scores):.2f}")
                print(f"  Std Dev: {np.std(scores):.2f}")
                print(f"  Min/Max: {min(scores)}/{max(scores)}")
    
    def extract_4_score_distribution_by_evaluator_type(self):
        """Extract 4: Compare score distributions between human and LLM evaluators."""
        print("\n" + "="*60)
        print("EXTRACTION 4: Score Distribution by Evaluator Type")
        print("="*60)
        
        query = """
        SELECT 
            evaluator_type,
            COUNT(*) as count,
            AVG(score) as avg_score,
            STD(score) as std_score,
            MIN(score) as min_score,
            MAX(score) as max_score
        FROM evaluations
        GROUP BY evaluator_type
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        for row in results:
            print(f"\n{row['evaluator_type'].upper()} Evaluations:")
            print(f"  Count: {row['count']}")
            print(f"  Average Score: {row['avg_score']:.2f}" if row['avg_score'] else "  Average Score: N/A")
            print(f"  Std Deviation: {row['std_score']:.2f}" if row['std_score'] else "  Std Deviation: N/A")
            print(f"  Min/Max: {row['min_score']:.2f}/{row['max_score']:.2f}" if row['min_score'] else "  Min/Max: N/A")
    
    def extract_5_rubric_source_comparison(self):
        """Extract 5: Compare evaluations across different rubric sources."""
        print("\n" + "="*60)
        print("EXTRACTION 5: Rubric Source Comparison")
        print("="*60)
        
        query = """
        SELECT 
            source_question_criteria,
            COUNT(*) as count,
            AVG(score) as avg_score,
            CASE source_question_criteria
                WHEN 1 THEN 'Human'
                WHEN 2 THEN 'LLMs structured'
                WHEN 3 THEN 'LLMs free'
                WHEN 4 THEN 'LLM reasoning structured'
                WHEN 5 THEN 'LLM reasoning free'
            END as source_name
        FROM evaluations
        GROUP BY source_question_criteria
        ORDER BY source_question_criteria
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        for row in results:
            print(f"\nSource {row['source_question_criteria']}: {row['source_name']}")
            print(f"  Total Evaluations: {row['count']}")
            print(f"  Average Score: {row['avg_score']:.2f}" if row['avg_score'] else "  Average Score: N/A")
    
    def extract_6_question_performance_analysis(self):
        """Extract 6: Analyze performance across different questions."""
        print("\n" + "="*60)
        print("EXTRACTION 6: Question Performance Analysis")
        print("="*60)
        
        query = """
        SELECT 
            q.id as question_id,
            SUBSTRING(q.question, 1, 50) as question_text,
            q.type,
            q.score as max_score,
            COUNT(DISTINCT sr.id) as response_count,
            COUNT(e.id) as evaluation_count,
            AVG(e.score) as avg_score
        FROM questions q
        LEFT JOIN student_responses sr ON q.id = sr.question_id
        LEFT JOIN evaluations e ON sr.id = e.student_response_id
        GROUP BY q.id, q.question, q.type, q.score
        ORDER BY q.id
        LIMIT 5
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        for row in results:
            print(f"\nQuestion {row['question_id']}: {row['question_text']}...")
            print(f"  Type: {row['type']}")
            print(f"  Max Score: {row['max_score']}")
            print(f"  Responses: {row['response_count']}")
            print(f"  Evaluations: {row['evaluation_count']}")
            print(f"  Avg Score: {row['avg_score']:.2f}" if row['avg_score'] else "  Avg Score: N/A")
    
    def extract_7_llm_model_performance(self):
        """Extract 7: Compare performance across different LLM models."""
        print("\n" + "="*60)
        print("EXTRACTION 7: LLM Model Performance Comparison")
        print("="*60)
        
        query = """
        SELECT 
            l.model_name,
            l.temperature,
            l.type as model_type,
            COUNT(e.id) as evaluation_count,
            AVG(e.score) as avg_score,
            STD(e.score) as std_score
        FROM evaluations e
        JOIN llms l ON e.evaluator_id = l.id
        WHERE e.evaluator_type = 'llm'
        GROUP BY l.id, l.model_name, l.temperature, l.type
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        for row in results:
            print(f"\n{row['model_name']} (Type: {row['model_type']}, Temp: {row['temperature']}):")
            print(f"  Evaluations: {row['evaluation_count']}")
            print(f"  Avg Score: {row['avg_score']:.2f}" if row['avg_score'] else "  Avg Score: N/A")
            print(f"  Std Dev: {row['std_score']:.2f}" if row['std_score'] else "  Std Dev: N/A")
    
    def extract_8_temporal_analysis(self):
        """Extract 8: Analyze evaluation patterns over time."""
        print("\n" + "="*60)
        print("EXTRACTION 8: Temporal Analysis of Evaluations")
        print("="*60)
        
        query = """
        SELECT 
            DATE(created_at) as evaluation_date,
            COUNT(*) as daily_count,
            AVG(score) as daily_avg_score,
            evaluator_type
        FROM evaluations
        WHERE created_at IS NOT NULL
        GROUP BY DATE(created_at), evaluator_type
        ORDER BY evaluation_date DESC
        LIMIT 10
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        if results:
            print("Recent evaluation activity:")
            for row in results:
                print(f"{row['evaluation_date']} - {row['evaluator_type']}: "
                      f"{row['daily_count']} evals, avg score: {row['daily_avg_score']:.2f}" if row['daily_avg_score'] else f"{row['daily_count']} evals")
        else:
            print("No temporal data available")
    
    def extract_9_agreement_between_evaluators(self):
        """Extract 9: Analyze agreement between human and LLM evaluators."""
        print("\n" + "="*60)
        print("EXTRACTION 9: Human-LLM Evaluator Agreement")
        print("="*60)
        
        query = """
        SELECT 
            sr.id as response_id,
            AVG(CASE WHEN e.evaluator_type = 'teacher' THEN e.score END) as human_avg,
            AVG(CASE WHEN e.evaluator_type = 'llm' THEN e.score END) as llm_avg,
            COUNT(CASE WHEN e.evaluator_type = 'teacher' THEN 1 END) as human_count,
            COUNT(CASE WHEN e.evaluator_type = 'llm' THEN 1 END) as llm_count
        FROM student_responses sr
        JOIN evaluations e ON sr.id = e.student_response_id
        GROUP BY sr.id
        HAVING human_count > 0 AND llm_count > 0
        LIMIT 50
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        differences = []
        for row in results:
            if row['human_avg'] and row['llm_avg']:
                diff = abs(row['human_avg'] - row['llm_avg'])
                differences.append(diff)
        
        if differences:
            print(f"Analyzed {len(differences)} responses with both human and LLM evaluations")
            print(f"Average absolute difference: {np.mean(differences):.2f}")
            print(f"Median absolute difference: {np.median(differences):.2f}")
            print(f"Max difference: {max(differences):.2f}")
            print(f"Responses with <5 point difference: {sum(1 for d in differences if d < 5)}/{len(differences)}")
        else:
            print("No responses found with both human and LLM evaluations")
    
    def extract_10_feedback_length_analysis(self):
        """Extract 10: Analyze feedback length patterns."""
        print("\n" + "="*60)
        print("EXTRACTION 10: Feedback Length Analysis")
        print("="*60)
        
        query = """
        SELECT 
            evaluator_type,
            AVG(LENGTH(feedback)) as avg_feedback_length,
            MIN(LENGTH(feedback)) as min_length,
            MAX(LENGTH(feedback)) as max_length,
            COUNT(*) as count
        FROM evaluations
        WHERE feedback IS NOT NULL AND feedback != ''
        GROUP BY evaluator_type
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        for row in results:
            print(f"\n{row['evaluator_type'].upper()}:")
            print(f"  Average feedback length: {row['avg_feedback_length']:.0f} chars" if row['avg_feedback_length'] else "  No feedback data")
            print(f"  Min/Max: {row['min_length']}/{row['max_length']} chars" if row['min_length'] else "  Min/Max: N/A")
            print(f"  Count with feedback: {row['count']}")
    
    def extract_11_rag_usage_statistics(self):
        """Extract 11: Analyze RAG (Retrieval Augmented Generation) usage."""
        print("\n" + "="*60)
        print("EXTRACTION 11: RAG Usage Statistics")
        print("="*60)
        
        query = """
        SELECT 
            COUNT(CASE WHEN rag_id IS NOT NULL THEN 1 END) as with_rag,
            COUNT(CASE WHEN rag_id IS NULL THEN 1 END) as without_rag,
            COUNT(*) as total
        FROM evaluations
        WHERE evaluator_type = 'llm'
        """
        
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        
        if result['total'] > 0:
            print(f"LLM Evaluations with RAG: {result['with_rag']} ({result['with_rag']/result['total']*100:.1f}%)")
            print(f"LLM Evaluations without RAG: {result['without_rag']} ({result['without_rag']/result['total']*100:.1f}%)")
        else:
            print("No LLM evaluations found")
    
    def extract_12_assignment_statistics(self):
        """Extract 12: Get statistics per assignment."""
        print("\n" + "="*60)
        print("EXTRACTION 12: Assignment Statistics")
        print("="*60)
        
        query = """
        SELECT 
            a.id,
            a.title,
            a.total_score as max_possible_score,
            COUNT(DISTINCT sr.id) as response_count,
            AVG(e.score) as avg_actual_score
        FROM assignments a
        LEFT JOIN questions q ON q.assignment_id = a.id
        LEFT JOIN student_responses sr ON sr.question_id = q.id
        LEFT JOIN evaluations e ON e.student_response_id = sr.id
        GROUP BY a.id, a.title, a.total_score
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        for row in results:
            print(f"\nAssignment: {row['title']}")
            print(f"  Max Score: {row['max_possible_score']}")
            print(f"  Responses: {row['response_count']}")
            if row['avg_actual_score']:
                print(f"  Avg Actual Score: {row['avg_actual_score']:.2f}")
                print(f"  Performance: {row['avg_actual_score']/row['max_possible_score']*100:.1f}%")
    
    def extract_13_criteria_consistency(self):
        """Extract 13: Analyze criteria consistency across evaluations."""
        print("\n" + "="*60)
        print("EXTRACTION 13: Criteria Consistency Analysis")
        print("="*60)
        
        query = """
        SELECT 
            student_response_id,
            COUNT(*) as eval_count,
            STD(score) as score_std,
            MAX(score) - MIN(score) as score_range
        FROM evaluations
        WHERE evaluator_type = 'llm'
        GROUP BY student_response_id
        HAVING eval_count >= 3
        ORDER BY score_std DESC
        LIMIT 10
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        if results:
            print("Top 10 responses with highest score variability (LLM evaluations):")
            for i, row in enumerate(results, 1):
                print(f"{i}. Response {row['student_response_id']}: "
                      f"Std Dev={row['score_std']:.2f}, Range={row['score_range']:.2f}" if row['score_std'] else f"Std Dev=N/A, Range={row['score_range']:.2f}")
        else:
            print("No responses found with 3+ LLM evaluations")
    
    def extract_14_json_criteria_extraction(self):
        """Extract 14: Extract specific criteria scores from JSON."""
        print("\n" + "="*60)
        print("EXTRACTION 14: Specific Criteria Extraction from JSON")
        print("="*60)
        
        query = """
        SELECT 
            id,
            criteria_evaluations_by_llm
        FROM evaluations
        WHERE evaluator_type = 'llm' 
        AND criteria_evaluations_by_llm IS NOT NULL
        LIMIT 100
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        # Extract specific criterion scores
        target_criterion = "Estruturas de Dados"
        scores = []
        
        for row in results:
            if row['criteria_evaluations_by_llm']:
                try:
                    criteria_evals = json.loads(row['criteria_evaluations_by_llm'])
                    for criterion in criteria_evals:
                        if criterion.get('criterion') == target_criterion:
                            scores.append(criterion.get('score', 0))
                            break
                except json.JSONDecodeError:
                    continue
        
        if scores:
            print(f"Analysis for criterion '{target_criterion}':")
            print(f"  Found in {len(scores)} evaluations")
            print(f"  Average score: {np.mean(scores):.2f}")
            unique_scores, counts = np.unique(scores, return_counts=True)
            print(f"  Score distribution: {dict(zip(unique_scores, counts))}")
        else:
            print(f"No evaluations found with criterion '{target_criterion}'")
    
    def extract_15_final_evaluations_analysis(self):
        """Extract 15: Analyze final aggregated evaluations."""
        print("\n" + "="*60)
        print("EXTRACTION 15: Final Evaluations Analysis")
        print("="*60)
        
        query = """
        SELECT 
            COUNT(*) as total,
            AVG(final_score) as avg_final_score,
            COUNT(CASE WHEN need_teacher_review = 1 THEN 1 END) as need_review,
            STD(final_score) as std_final_score
        FROM final_evaluations
        """
        
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        
        if result['total'] > 0:
            print(f"Total Final Evaluations: {result['total']}")
            print(f"Average Final Score: {result['avg_final_score']:.2f}" if result['avg_final_score'] else "Average Final Score: N/A")
            print(f"Need Teacher Review: {result['need_review']} ({result['need_review']/result['total']*100:.1f}%)")
            print(f"Std Dev of Final Scores: {result['std_final_score']:.2f}" if result['std_final_score'] else "Std Dev: N/A")
        else:
            print("No final evaluations found")
    
    def extract_16_question_type_performance(self):
        """Extract 16: Compare performance across question types."""
        print("\n" + "="*60)
        print("EXTRACTION 16: Performance by Question Type")
        print("="*60)
        
        query = """
        SELECT 
            q.type as question_type,
            COUNT(DISTINCT sr.id) as response_count,
            AVG(e.score) as avg_score,
            STD(e.score) as std_score,
            e.evaluator_type
        FROM questions q
        JOIN student_responses sr ON q.id = sr.question_id
        JOIN evaluations e ON sr.id = e.student_response_id
        GROUP BY q.type, e.evaluator_type
        ORDER BY q.type, e.evaluator_type
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        for row in results:
            print(f"\n{row['question_type']} - {row['evaluator_type']}:")
            print(f"  Responses: {row['response_count']}")
            print(f"  Avg Score: {row['avg_score']:.2f}" if row['avg_score'] else "  Avg Score: N/A")
            print(f"  Std Dev: {row['std_score']:.2f}" if row['std_score'] else "  Std Dev: N/A")
    
    def extract_17_comprehensive_json_analysis(self):
        """Extract 17: Comprehensive analysis of all JSON criteria fields."""
        print("\n" + "="*60)
        print("EXTRACTION 17: Comprehensive JSON Criteria Analysis")
        print("="*60)
        
        query = """
        SELECT 
            id,
            student_response_id,
            score as total_score,
            criteria_evaluations_by_llm
        FROM evaluations
        WHERE evaluator_type = 'llm' 
        AND criteria_evaluations_by_llm IS NOT NULL
        LIMIT 200
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        all_criteria_names = set()
        criteria_count = {}
        sum_validation = []
        
        for row in results:
            if row['criteria_evaluations_by_llm']:
                try:
                    criteria_evals = json.loads(row['criteria_evaluations_by_llm'])
                    criteria_sum = 0
                    
                    for criterion in criteria_evals:
                        name = criterion.get('criterion', 'Unknown')
                        score = criterion.get('score', 0)
                        
                        all_criteria_names.add(name)
                        criteria_count[name] = criteria_count.get(name, 0) + 1
                        criteria_sum += score
                    
                    # Validate if sum matches total score
                    sum_validation.append({
                        'eval_id': row['id'],
                        'total_score': row['total_score'],
                        'criteria_sum': criteria_sum,
                        'match': abs(row['total_score'] - criteria_sum) < 0.01
                    })
                except json.JSONDecodeError:
                    continue
        
        if all_criteria_names:
            print(f"Total unique criteria found: {len(all_criteria_names)}")
            print("\nTop 5 most common criteria:")
            sorted_criteria = sorted(criteria_count.items(), key=lambda x: x[1], reverse=True)
            for name, count in sorted_criteria[:5]:
                print(f"  '{name}': {count} occurrences")
            
            if sum_validation:
                matches = sum(1 for v in sum_validation if v['match'])
                print(f"\nScore validation:")
                print(f"  Criteria sum matches total score: {matches}/{len(sum_validation)} "
                      f"({matches/len(sum_validation)*100:.1f}%)")
        else:
            print("No JSON criteria data found")
    
    def extract_18_student_performance_distribution(self):
        """Extract 18: Analyze student performance distribution."""
        print("\n" + "="*60)
        print("EXTRACTION 18: Student Performance Distribution")
        print("="*60)
        
        query = """
        SELECT 
            sr.student_id,
            COUNT(DISTINCT sr.question_id) as questions_answered,
            AVG(e.score) as avg_score,
            MIN(e.score) as min_score,
            MAX(e.score) as max_score
        FROM student_responses sr
        JOIN evaluations e ON sr.id = e.student_response_id
        GROUP BY sr.student_id
        ORDER BY avg_score DESC
        LIMIT 10
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        if results:
            print("Top 10 students by average score:")
            for i, row in enumerate(results, 1):
                print(f"{i}. Student {row['student_id']}:")
                print(f"   Questions: {row['questions_answered']}")
                print(f"   Avg Score: {row['avg_score']:.2f}" if row['avg_score'] else "   Avg Score: N/A")
                print(f"   Score Range: {row['min_score']:.2f} - {row['max_score']:.2f}" if row['min_score'] else "   Score Range: N/A")
        else:
            print("No student performance data found")
    
    def extract_19_rubric_effectiveness(self):
        """Extract 19: Analyze effectiveness of different rubric sources."""
        print("\n" + "="*60)
        print("EXTRACTION 19: Rubric Effectiveness Analysis")
        print("="*60)
        
        query = """
        SELECT 
            e.source_question_criteria,
            COUNT(DISTINCT e.student_response_id) as responses_evaluated,
            AVG(e.score) as avg_score,
            STD(e.score) as score_std,
            AVG(LENGTH(e.feedback)) as avg_feedback_length,
            CASE e.source_question_criteria
                WHEN 1 THEN 'Human'
                WHEN 2 THEN 'LLMs structured'
                WHEN 3 THEN 'LLMs free'
                WHEN 4 THEN 'LLM reasoning structured'
                WHEN 5 THEN 'LLM reasoning free'
            END as source_name
        FROM evaluations e
        WHERE e.evaluator_type = 'llm'
        GROUP BY e.source_question_criteria
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        for row in results:
            print(f"\n{row['source_name']} (Type {row['source_question_criteria']}):")
            print(f"  Responses evaluated: {row['responses_evaluated']}")
            print(f"  Average score: {row['avg_score']:.2f}" if row['avg_score'] else "  Average score: N/A")
            print(f"  Score std dev: {row['score_std']:.2f}" if row['score_std'] else "  Score std dev: N/A")
            print(f"  Avg feedback length: {row['avg_feedback_length']:.0f} chars" if row['avg_feedback_length'] else "  No feedback data")
    
    def extract_20_complete_evaluation_export(self, limit=5):
        """Extract 20: Export complete evaluation data with parsed JSON."""
        print("\n" + "="*60)
        print(f"EXTRACTION 20: Complete Evaluation Export (First {limit} LLM evaluations)")
        print("="*60)
        
        query = """
        SELECT 
            e.*,
            sr.question_id,
            sr.response,
            q.question,
            q.type as question_type,
            l.model_name,
            l.temperature
        FROM evaluations e
        JOIN student_responses sr ON e.student_response_id = sr.id
        JOIN questions q ON sr.question_id = q.id
        LEFT JOIN llms l ON e.evaluator_id = l.id AND e.evaluator_type = 'llm'
        WHERE e.evaluator_type = 'llm' 
        AND e.criteria_evaluations_by_llm IS NOT NULL
        LIMIT %s
        """
        
        self.cursor.execute(query, (limit,))
        results = self.cursor.fetchall()
        
        export_data = []
        for row in results:
            # Parse JSON criteria
            criteria_details = []
            if row['criteria_evaluations_by_llm']:
                try:
                    criteria_evals = json.loads(row['criteria_evaluations_by_llm'])
                    for criterion in criteria_evals:
                        criteria_details.append({
                            'criterion_name': criterion.get('criterion'),
                            'criterion_score': criterion.get('score'),
                            'criterion_justification': criterion.get('justification')
                        })
                except json.JSONDecodeError:
                    continue
            
            export_data.append({
                'evaluation_id': row['id'],
                'response_id': row['student_response_id'],
                'question': row['question'][:50] + '...' if len(row['question']) > 50 else row['question'],
                'question_type': row['question_type'],
                'model': f"{row['model_name']} (temp={row['temperature']})",
                'total_score': row['score'],
                'feedback': row['feedback'][:100] + '...' if row['feedback'] and len(row['feedback']) > 100 else row['feedback'],
                'criteria_count': len(criteria_details),
                'criteria_details': criteria_details,
                'rubric_source': row['source_question_criteria'],
                'created_at': row['created_at']
            })
        
        # Display summary
        for i, data in enumerate(export_data, 1):
            print(f"\n--- Evaluation {i} ---")
            print(f"ID: {data['evaluation_id']}")
            print(f"Question: {data['question']}")
            print(f"Type: {data['question_type']}")
            print(f"Model: {data['model']}")
            print(f"Total Score: {data['total_score']}")
            print(f"Number of Criteria: {data['criteria_count']}")
            print("Criteria Breakdown:")
            for criterion in data['criteria_details']:
                print(f"  • {criterion['criterion_name']}: {criterion['criterion_score']} points")
        
        print(f"\n✓ Exported {len(export_data)} complete evaluations")
        return export_data
    
    def extract_21_question_criteria_analysis(self):
        """Extract 21: Analyze predefined question criteria."""
        print("\n" + "="*60)
        print("EXTRACTION 21: Question Criteria Analysis")
        print("="*60)
        
        query = """
        SELECT 
            qc.source,
            COUNT(*) as criteria_count,
            AVG(qc.score) as avg_criteria_score,
            CASE qc.source
                WHEN 1 THEN 'Human'
                WHEN 2 THEN 'OpenAI Hybrid LLMs structured'
                WHEN 3 THEN 'OpenAI Hybrid LLMs free'
                WHEN 4 THEN 'DeepSeek Hybrid LLM structured'
                WHEN 5 THEN 'DeepSeek Hybrid LLM free'
            END as source_name
        FROM question_criterias qc
        GROUP BY qc.source
        ORDER BY qc.source
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        for row in results:
            print(f"\nSource {row['source']}: {row['source_name']}")
            print(f"  Total Criteria: {row['criteria_count']}")
            print(f"  Avg Criteria Score: {row['avg_criteria_score']:.2f}" if row['avg_criteria_score'] else "  Avg Criteria Score: N/A")
    
    def extract_22_evaluation_reports_summary(self):
        """Extract 22: Summarize evaluation reports."""
        print("\n" + "="*60)
        print("EXTRACTION 22: Evaluation Reports Summary")
        print("="*60)
        
        query = """
        SELECT 
            er.evaluator_type,
            COUNT(*) as report_count,
            AVG(LENGTH(er.short_balance)) as avg_balance_length,
            AVG(LENGTH(er.strengths)) as avg_strengths_length,
            AVG(LENGTH(er.weaknesses)) as avg_weaknesses_length,
            AVG(LENGTH(er.suggestions)) as avg_suggestions_length
        FROM evaluation_reports er
        GROUP BY er.evaluator_type
        """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        
        for row in results:
            print(f"\n{row['evaluator_type'].upper()} Reports:")
            print(f"  Count: {row['report_count']}")
            print(f"  Avg Balance Length: {row['avg_balance_length']:.0f} chars" if row['avg_balance_length'] else "  No balance data")
            print(f"  Avg Strengths Length: {row['avg_strengths_length']:.0f} chars" if row['avg_strengths_length'] else "  No strengths data")
            print(f"  Avg Weaknesses Length: {row['avg_weaknesses_length']:.0f} chars" if row['avg_weaknesses_length'] else "  No weaknesses data")
            print(f"  Avg Suggestions Length: {row['avg_suggestions_length']:.0f} chars" if row['avg_suggestions_length'] else "  No suggestions data")
    
    def extract_23_complete_evaluation_record(self, evaluation_id=17602):
        """Extract 23: Get COMPLETE evaluation record with full JSON parsing."""
        print("\n" + "="*60)
        print(f"EXTRACTION 23: COMPLETE Evaluation Record (ID={evaluation_id})")
        print("="*60)
        
        # Get the complete evaluation record
        query = """
        SELECT * FROM evaluations WHERE id = %s
        """
        
        self.cursor.execute(query, (evaluation_id,))
        evaluation = self.cursor.fetchone()
        
        if not evaluation:
            print(f"No evaluation found with ID {evaluation_id}")
            return
        
        print("="*40)
        print("EVALUATION TABLE FIELDS:")
        print("="*40)
        print(f"ID: {evaluation['id']}")
        print(f"Student Response ID: {evaluation['student_response_id']}")
        print(f"Evaluator Type: {evaluation['evaluator_type']}")
        print(f"Evaluator ID: {evaluation['evaluator_id']}")
        print(f"Total Score: {evaluation['score']}")
        print(f"RAG ID: {evaluation['rag_id']}")
        print(f"Source Question Criteria: {evaluation['source_question_criteria']}")
        
        # Map source to description
        source_map = {
            1: 'Human',
            2: 'LLMs structured',
            3: 'LLMs free',
            4: 'LLM reasoning structured',
            5: 'LLM reasoning free'
        }
        print(f"Source Description: {source_map.get(evaluation['source_question_criteria'], 'Unknown')}")
        print(f"Is Active: {evaluation['is_active']}")
        print(f"Created At: {evaluation['created_at']}")
        print(f"Updated At: {evaluation['updated_at']}")
        
        # Display feedback
        print("\n" + "="*40)
        print("FEEDBACK:")
        print("="*40)
        if evaluation['feedback']:
            print(evaluation['feedback'])
        else:
            print("No feedback provided")
        
        # Parse and display JSON criteria if it's an LLM evaluation
        if evaluation['evaluator_type'] == 'llm' and evaluation['criteria_evaluations_by_llm']:
            print("\n" + "="*40)
            print("CRITERIA EVALUATIONS BY LLM (Parsed JSON):")
            print("="*40)
            
            try:
                criteria_list = json.loads(evaluation['criteria_evaluations_by_llm'])
                
                print(f"Number of criteria: {len(criteria_list)}")
                print("-" * 40)
                
                total_from_criteria = 0
                for i, criterion in enumerate(criteria_list, 1):
                    print(f"\nCRITERION {i}:")
                    print(f"  Criterion Name: {criterion.get('criterion', 'Not specified')}")
                    print(f"  Score: {criterion.get('score', 0)}")
                    print(f"  Justification: {criterion.get('justification', 'No justification provided')}")
                    
                    total_from_criteria += criterion.get('score', 0)
                
                print("\n" + "-" * 40)
                print(f"Sum of Criteria Scores: {total_from_criteria}")
                print(f"Total Score in Evaluation: {evaluation['score']}")
                print(f"Difference: {abs(evaluation['score'] - total_from_criteria):.2f}")
                
                if abs(evaluation['score'] - total_from_criteria) < 0.01:
                    print("✓ Criteria scores sum matches total score")
                else:
                    print("⚠ Warning: Criteria scores sum does not match total score")
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
        else:
            print("\n" + "="*40)
            print("No LLM criteria evaluations (Human evaluation or no JSON data)")
        
        # Get related information
        print("\n" + "="*40)
        print("RELATED INFORMATION:")
        print("="*40)
        
        # Get student response info
        query = """
        SELECT sr.*, q.question, q.type, q.score as max_score
        FROM student_responses sr
        JOIN questions q ON sr.question_id = q.id
        WHERE sr.id = %s
        """
        self.cursor.execute(query, (evaluation['student_response_id'],))
        response_info = self.cursor.fetchone()
        
        if response_info:
            print(f"Question Type: {response_info['type']}")
            print(f"Max Possible Score: {response_info['max_score']}")
            print(f"Student Response (first 200 chars): {response_info['response'][:200]}...")
        
        # If LLM evaluation, get model info
        if evaluation['evaluator_type'] == 'llm':
            query = "SELECT * FROM llms WHERE id = %s"
            self.cursor.execute(query, (evaluation['evaluator_id'],))
            llm_info = self.cursor.fetchone()
            if llm_info:
                print(f"LLM Model: {llm_info['model_name']}")
                print(f"Temperature: {llm_info['temperature']}")
                print(f"Type: {llm_info['type']}")
    
    def extract_24_complete_evaluation_report(self, report_id=1):
        """Extract 24: Get complete evaluation report by ID."""
        print("\n" + "="*60)
        print(f"EXTRACTION 24: Complete Evaluation Report (ID={report_id})")
        print("="*60)
        
        query = """
        SELECT 
            er.*,
            a.title as assignment_title,
            a.total_score as assignment_total_score
        FROM evaluation_reports er
        LEFT JOIN assignments a ON er.assignment_id = a.id
        WHERE er.id = %s
        """
        
        self.cursor.execute(query, (report_id,))
        report = self.cursor.fetchone()
        
        if not report:
            print(f"No evaluation report found with ID {report_id}")
            return
        
        print("="*40)
        print("EVALUATION REPORT DETAILS:")
        print("="*40)
        
        # Basic information
        print(f"Report ID: {report['id']}")
        print(f"Assignment ID: {report['assignment_id']}")
        print(f"Assignment Title: {report['assignment_title']}")
        print(f"Assignment Total Score: {report['assignment_total_score']}")
        print(f"Student ID: {report['student_id']}")
        print(f"Evaluator Type: {report['evaluator_type']}")
        print(f"Evaluator ID: {report['evaluator_id']}")
        
        if report['source_question_criteria']:
            source_map = {
                1: 'Human',
                2: 'LLMs structured', 
                3: 'LLMs free',
                4: 'LLM reasoning structured',
                5: 'LLM reasoning free'
            }
            print(f"Source Question Criteria: {report['source_question_criteria']} ({source_map.get(report['source_question_criteria'], 'Unknown')})")
        
        if report['source_evaluator_id']:
            print(f"Source Evaluator ID: {report['source_evaluator_id']}")
        
        print(f"Created At: {report['created_at']}")
        print(f"Updated At: {report['updated_at']}")
        
        # Report content sections
        print("\n" + "="*40)
        print("SHORT BALANCE:")
        print("="*40)
        print(report['short_balance'] if report['short_balance'] else "No balance provided")
        
        print("\n" + "="*40)
        print("STRENGTHS:")
        print("="*40)
        print(report['strengths'] if report['strengths'] else "No strengths provided")
        
        print("\n" + "="*40)
        print("WEAKNESSES:")
        print("="*40)
        print(report['weaknesses'] if report['weaknesses'] else "No weaknesses provided")
        
        print("\n" + "="*40)
        print("SUGGESTIONS:")
        print("="*40)
        print(report['suggestions'] if report['suggestions'] else "No suggestions provided")
        
        # Get evaluator information
        print("\n" + "="*40)
        print("EVALUATOR INFORMATION:")
        print("="*40)
        
        if report['evaluator_type'] == 'llm':
            query = "SELECT * FROM llms WHERE id = %s"
            self.cursor.execute(query, (report['evaluator_id'],))
            llm_info = self.cursor.fetchone()
            if llm_info:
                print(f"LLM Model: {llm_info['model_name']}")
                print(f"Temperature: {llm_info['temperature']}")
                print(f"Model Type: {llm_info['type']}")
        else:
            print(f"Human evaluator (ID: {report['evaluator_id']})")
        
        # Get related evaluations count for this student and assignment
        query = """
        SELECT COUNT(*) as eval_count
        FROM evaluations e
        JOIN student_responses sr ON e.student_response_id = sr.id
        JOIN questions q ON sr.question_id = q.id
        WHERE sr.student_id = %s AND q.assignment_id = %s
        """
        self.cursor.execute(query, (report['student_id'], report['assignment_id']))
        result = self.cursor.fetchone()
        
        if result:
            print(f"\nRelated evaluations for this student/assignment: {result['eval_count']}")
        else:
            print(f"\nNo related evaluations found for this student/assignment")
    
    def run_all_extractions(self):
        """Run all extraction demonstrations."""
        print("\n" + "="*80)
        print(" HARMOGEN-R DATASET EXTRACTION DEMONSTRATION ".center(80, "="))
        print("="*80)
        
        if not self.connect():
            return
        
        try:
            # Run all extractions
            self.extract_1_database_overview()
            self.extract_2_evaluation_by_id(evaluation_id=1)
            self.extract_3_llm_criteria_analysis()
            self.extract_4_score_distribution_by_evaluator_type()
            self.extract_5_rubric_source_comparison()
            self.extract_6_question_performance_analysis()
            self.extract_7_llm_model_performance()
            self.extract_8_temporal_analysis()
            self.extract_9_agreement_between_evaluators()
            self.extract_10_feedback_length_analysis()
            self.extract_11_rag_usage_statistics()
            self.extract_12_assignment_statistics()
            self.extract_13_criteria_consistency()
            self.extract_14_json_criteria_extraction()
            self.extract_15_final_evaluations_analysis()
            self.extract_16_question_type_performance()
            self.extract_17_comprehensive_json_analysis()
            self.extract_18_student_performance_distribution()
            self.extract_19_rubric_effectiveness()
            self.extract_20_complete_evaluation_export(limit=3)
            self.extract_21_question_criteria_analysis()
            self.extract_22_evaluation_reports_summary()
            self.extract_23_complete_evaluation_record(evaluation_id=17602)
            self.extract_24_complete_evaluation_report(report_id=1)
            
            print("\n" + "="*80)
            print(" EXTRACTION DEMONSTRATION COMPLETE ".center(80, "="))
            print("="*80)
            
        except Exception as e:
            print(f"\n✗ Error during extraction: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.disconnect()


def main():
    """Main execution function."""
    # Configuration
    config = {
        'host': 'localhost',
        'database': 'dataset_article',
        'user': 'root',
        'password': '',  # Update with your password
        'port': 3306
    }
    
    # Create extractor and run demonstrations
    extractor = HARMOGENDataExtractor(**config)
    extractor.run_all_extractions()
    
    # Example of running specific extractions
    print("\n" + "="*80)
    print(" RUNNING SPECIFIC EXTRACTION EXAMPLE ".center(80, "="))
    print("="*80)
    
    if extractor.connect():
        extractor.extract_2_evaluation_by_id(evaluation_id=10)
        extractor.disconnect()


if __name__ == "__main__":
    main()