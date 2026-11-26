#!/usr/bin/env python3
"""
HARMOGEN Dataset - Exploratory Data Analysis (Fixed Version)
=============================================================
This script performs comprehensive exploratory data analysis on the HARMOGEN-R dataset,
specifically using the all_evaluations_wide_format_all_assignments_normalized.csv file.

Author: HARMOGEN-R Research Team
Date: 2025
License: CC BY 4.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import mannwhitneyu, kruskal, spearmanr, skew, kurtosis
import warnings
import os
from datetime import datetime
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class HARMOGENExploratoryAnalysis:
    """
    Comprehensive exploratory data analysis for HARMOGEN-R dataset.
    """
    
    def __init__(self, data_path='datasets/all_evaluations_wide_format_all_assignments_normalized.csv', 
                 output_dir='reports'):
        """
        Initialize the EDA class with data loading.
        
        Args:
            data_path: Path to the CSV file
            output_dir: Directory for output files (reports and plots)
        """
        self.data_path = data_path
        self.output_dir = output_dir
        self.df = None
        self.teacher_cols = ['teacher_1_score', 'teacher_2_score', 'teacher_3_score', 'teacher_4_score']
        self.llm1_cols = ['llm1_eval1_score', 'llm1_eval2_score', 'llm1_eval3_score']
        self.llm4_cols = ['llm4_eval1_score', 'llm4_eval2_score', 'llm4_eval3_score']
        self.llm13_cols = ['llm13_eval1_score', 'llm13_eval2_score', 'llm13_eval3_score']
        self.all_llm_cols = self.llm1_cols + self.llm4_cols + self.llm13_cols
        
        # Rubric source mapping
        self.rubric_sources = {
            1: 'Human',
            2: 'OpenAI Hybrid LLMs structured',
            3: 'OpenAI Hybrid LLMs free',
            4: 'DeepSeek Hybrid LLM structured',
            5: 'DeepSeek Hybrid LLM free'
        }
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"✓ Created output directory: {self.output_dir}/")
        
        # Initialize markdown report content
        self.report_content = []
        
    def add_to_report(self, content):
        """Add content to the markdown report."""
        self.report_content.append(content)
        print(content)  # Also print to console
    
    def load_data(self):
        """Load and perform initial data processing."""
        self.add_to_report("# HARMOGEN-R Dataset - Exploratory Data Analysis Report")
        self.add_to_report(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.add_to_report("---\n")
        
        self.add_to_report("## 1. Data Loading")
        
        try:
            self.df = pd.read_csv(self.data_path)
            self.add_to_report(f"\n✓ Data loaded successfully from `{self.data_path}`")
            self.add_to_report(f"\n- **Shape:** {self.df.shape[0]:,} rows × {self.df.shape[1]} columns")
            
            # Convert source_question_criteria to category with labels
            self.df['rubric_source_name'] = self.df['source_question_criteria'].map(self.rubric_sources)
            
            # Calculate mean scores for each evaluator group
            self.df['teacher_mean'] = self.df[self.teacher_cols].mean(axis=1)
            self.df['llm1_mean'] = self.df[self.llm1_cols].mean(axis=1)
            self.df['llm4_mean'] = self.df[self.llm4_cols].mean(axis=1)
            self.df['llm13_mean'] = self.df[self.llm13_cols].mean(axis=1)
            self.df['all_llm_mean'] = self.df[self.all_llm_cols].mean(axis=1)
            
            # Calculate standard deviations for consistency analysis
            self.df['teacher_std'] = self.df[self.teacher_cols].std(axis=1)
            self.df['llm1_std'] = self.df[self.llm1_cols].std(axis=1)
            self.df['llm4_std'] = self.df[self.llm4_cols].std(axis=1)
            self.df['llm13_std'] = self.df[self.llm13_cols].std(axis=1)
            
            # Calculate differences
            self.df['teacher_llm_diff'] = self.df['all_llm_mean'] - self.df['teacher_mean']
            
            return True
        except FileNotFoundError:
            self.add_to_report(f"\n✗ **Error:** File not found: `{self.data_path}`")
            self.add_to_report("\nPlease run the normalization script first.")
            return False
        except Exception as e:
            self.add_to_report(f"\n✗ **Error loading data:** {e}")
            return False
    
    def basic_statistics(self):
        """Generate basic statistics about the dataset."""
        self.add_to_report("\n## 2. Basic Dataset Statistics")
        
        # Dataset overview
        self.add_to_report("\n### 2.1 Dataset Overview")
        self.add_to_report(f"\n- Total rows: **{len(self.df):,}**")
        self.add_to_report(f"- Total columns: **{len(self.df.columns)}**")
        self.add_to_report(f"- Unique assignments: **{self.df['assignment_id'].nunique()}**")
        self.add_to_report(f"- Unique questions: **{self.df['question_id'].nunique()}**")
        self.add_to_report(f"- Unique responses: **{self.df['response_id'].nunique()}**")
        
        # Question types distribution
        self.add_to_report("\n### 2.2 Question Type Distribution")
        self.add_to_report("\n| Question Type | Count | Percentage |")
        self.add_to_report("|---------------|-------|------------|")
        question_types = self.df.groupby('question_type')['response_id'].count()
        for qtype, count in question_types.items():
            self.add_to_report(f"| {qtype} | {count:,} | {count/len(self.df)*100:.1f}% |")
        
        # Rubric source distribution
        self.add_to_report("\n### 2.3 Rubric Source Distribution")
        self.add_to_report("\n| Rubric Source | Count | Percentage |")
        self.add_to_report("|---------------|-------|------------|")
        rubric_dist = self.df.groupby('rubric_source_name')['response_id'].count()
        for source, count in rubric_dist.items():
            self.add_to_report(f"| {source} | {count:,} | {count/len(self.df)*100:.1f}% |")
        
        # Missing data analysis
        self.add_to_report("\n### 2.4 Missing Data Analysis")
        self.add_to_report("\n#### Teacher Scores")
        self.add_to_report("\n| Column | Missing | Percentage |")
        self.add_to_report("|--------|---------|------------|")
        for col in self.teacher_cols:
            missing = self.df[col].isna().sum()
            self.add_to_report(f"| {col} | {missing:,} | {missing/len(self.df)*100:.1f}% |")
        
        self.add_to_report("\n#### LLM Scores")
        self.add_to_report("\n| Column | Missing | Percentage |")
        self.add_to_report("|--------|---------|------------|")
        for col in self.all_llm_cols:
            missing = self.df[col].isna().sum()
            self.add_to_report(f"| {col} | {missing:,} | {missing/len(self.df)*100:.1f}% |")
    
    def score_distribution_analysis(self):
        """Analyze score distributions for different evaluators."""
        self.add_to_report("\n## 3. Score Distribution Analysis")
        
        self.add_to_report("\n### 3.1 Overall Score Statistics")
        self.add_to_report("\n| Evaluator | N | Mean | Median | Std Dev | Min | Max | Q1 | Q3 |")
        self.add_to_report("|-----------|---|------|--------|---------|-----|-----|----|----|")
        
        evaluator_groups = {
            'Teachers': 'teacher_mean',
            'LLM-1 (GPT-4.1)': 'llm1_mean',
            'LLM-4 (GPT-4o)': 'llm4_mean',
            'LLM-13 (DeepSeek-V3)': 'llm13_mean',
            'All LLMs': 'all_llm_mean'
        }
        
        for name, col in evaluator_groups.items():
            scores = self.df[col].dropna()
            if len(scores) > 0:
                self.add_to_report(f"| {name} | {len(scores):,} | {scores.mean():.2f} | {scores.median():.2f} | "
                                 f"{scores.std():.2f} | {scores.min():.2f} | {scores.max():.2f} | "
                                 f"{scores.quantile(0.25):.2f} | {scores.quantile(0.75):.2f} |")
        
        # Statistical comparisons
        self.add_to_report("\n### 3.2 Statistical Comparisons (Mann-Whitney U tests)")
        self.add_to_report("\n| Comparison | U Statistic | p-value | Significant? |")
        self.add_to_report("|------------|-------------|---------|--------------|")
        
        teacher_scores = self.df['teacher_mean'].dropna()
        for name, col in [('LLM-1', 'llm1_mean'), ('LLM-4', 'llm4_mean'), ('LLM-13', 'llm13_mean')]:
            llm_scores = self.df[col].dropna()
            if len(teacher_scores) > 0 and len(llm_scores) > 0:
                common_idx = teacher_scores.index.intersection(llm_scores.index)
                if len(common_idx) > 0:
                    statistic, pvalue = mannwhitneyu(
                        teacher_scores.loc[common_idx],
                        llm_scores.loc[common_idx],
                        alternative='two-sided'
                    )
                    sig = "Yes ✓" if pvalue < 0.05 else "No"
                    self.add_to_report(f"| Teachers vs {name} | {statistic:.0f} | {pvalue:.4f} | {sig} |")
    
    def agreement_metrics(self):
        """Calculate agreement metrics appropriate for dataset description."""
        self.add_to_report("\n## 4. Agreement and Consistency Metrics")
        
        # Calculate mean absolute differences
        self.add_to_report("\n### 4.1 Mean Absolute Differences (MAD)")
        self.add_to_report("\n| Comparison | MAD | Std Dev |")
        self.add_to_report("|------------|-----|---------|")
        
        for name, col in [('LLM-1', 'llm1_mean'), ('LLM-4', 'llm4_mean'), ('LLM-13', 'llm13_mean')]:
            valid_pairs = self.df[['teacher_mean', col]].dropna()
            if len(valid_pairs) > 0:
                mad = np.abs(valid_pairs['teacher_mean'] - valid_pairs[col]).mean()
                mad_std = np.abs(valid_pairs['teacher_mean'] - valid_pairs[col]).std()
                self.add_to_report(f"| Teachers vs {name} | {mad:.2f}% | {mad_std:.2f}% |")
        
        # Agreement within tolerance bands
        self.add_to_report("\n### 4.2 Agreement Within Tolerance Bands")
        self.add_to_report("\n| Tolerance | LLM-1 | LLM-4 | LLM-13 | Overall |")
        self.add_to_report("|-----------|-------|-------|--------|---------|")
        
        for tolerance in [5, 10, 15, 20]:
            agreements = []
            for col in ['llm1_mean', 'llm4_mean', 'llm13_mean']:
                valid_pairs = self.df[['teacher_mean', col]].dropna()
                if len(valid_pairs) > 0:
                    within_tolerance = (np.abs(valid_pairs['teacher_mean'] - valid_pairs[col]) <= tolerance).sum()
                    pct = (within_tolerance / len(valid_pairs)) * 100
                    agreements.append(pct)
            
            # Overall average
            overall = np.mean(agreements) if agreements else 0
            
            self.add_to_report(f"| ±{tolerance}% | {agreements[0]:.1f}% | {agreements[1]:.1f}% | "
                             f"{agreements[2]:.1f}% | {overall:.1f}% |")
        
        # Within-group consistency (standard deviations)
        self.add_to_report("\n### 4.3 Within-Group Consistency")
        self.add_to_report("\n| Evaluator Group | Mean SD | Median SD | IQR |")
        self.add_to_report("|-----------------|---------|-----------|-----|")
        
        for name, col in [('Teachers (n=4)', 'teacher_std'), 
                          ('LLM-1 (n=3)', 'llm1_std'),
                          ('LLM-4 (n=3)', 'llm4_std'), 
                          ('LLM-13 (n=3)', 'llm13_std')]:
            std_scores = self.df[col].dropna()
            if len(std_scores) > 0:
                mean_sd = std_scores.mean()
                median_sd = std_scores.median()
                q1 = std_scores.quantile(0.25)
                q3 = std_scores.quantile(0.75)
                iqr = q3 - q1
                self.add_to_report(f"| {name} | {mean_sd:.2f} | {median_sd:.2f} | {iqr:.2f} |")
        
        # Correlation analysis
        self.add_to_report("\n### 4.4 Inter-Evaluator Correlations")
        self.add_to_report("\n| Comparison | Spearman r | p-value | Interpretation |")
        self.add_to_report("|------------|------------|---------|----------------|")
        
        for name, col in [('Teachers vs LLM-1', 'llm1_mean'), 
                          ('Teachers vs LLM-4', 'llm4_mean'), 
                          ('Teachers vs LLM-13', 'llm13_mean')]:
            valid_pairs = self.df[['teacher_mean', col]].dropna()
            if len(valid_pairs) > 1:
                corr, p = spearmanr(valid_pairs['teacher_mean'], valid_pairs[col])
                if corr >= 0.9:
                    interp = "Very Strong"
                elif corr >= 0.7:
                    interp = "Strong"
                elif corr >= 0.5:
                    interp = "Moderate"
                else:
                    interp = "Weak"
                self.add_to_report(f"| {name} | {corr:.3f} | {p:.4f} | {interp} |")
    
    def rubric_source_analysis(self):
        """Analyze performance across different rubric sources."""
        self.add_to_report("\n## 5. Rubric Source Analysis")
        
        self.add_to_report("\n### 5.1 Score Statistics by Rubric Source")
        self.add_to_report("\n| Rubric Source | N | Teacher Mean (±SD) | LLM Mean (±SD) | Mean Diff |")
        self.add_to_report("|---------------|---|-------------------|----------------|-----------|")
        
        for source_id, source_name in self.rubric_sources.items():
            subset = self.df[self.df['source_question_criteria'] == source_id]
            if len(subset) > 0:
                teacher_scores = subset['teacher_mean'].dropna()
                llm_scores = subset['all_llm_mean'].dropna()
                
                teacher_str = f"{teacher_scores.mean():.2f} (±{teacher_scores.std():.2f})" if len(teacher_scores) > 0 else "N/A"
                llm_str = f"{llm_scores.mean():.2f} (±{llm_scores.std():.2f})" if len(llm_scores) > 0 else "N/A"
                
                diff_str = "N/A"
                if len(teacher_scores) > 0 and len(llm_scores) > 0:
                    common_idx = teacher_scores.index.intersection(llm_scores.index)
                    if len(common_idx) > 0:
                        diff = (subset.loc[common_idx, 'all_llm_mean'] - subset.loc[common_idx, 'teacher_mean']).mean()
                        diff_str = f"{diff:+.2f}"
                
                # Shorten name for table
                short_name = source_name.replace('OpenAI Hybrid LLMs', 'OpenAI').replace('DeepSeek Hybrid LLM', 'DeepSeek')
                self.add_to_report(f"| {short_name} | {len(subset):,} | {teacher_str} | {llm_str} | {diff_str} |")
        
        # Statistical test
        self.add_to_report("\n### 5.2 Kruskal-Wallis Test")
        self.add_to_report("\n| Evaluator Type | H Statistic | p-value | Significant? |")
        self.add_to_report("|----------------|-------------|---------|--------------|")
        
        # For teachers
        teacher_groups = []
        for source_id in self.rubric_sources.keys():
            scores = self.df[self.df['source_question_criteria'] == source_id]['teacher_mean'].dropna()
            if len(scores) > 0:
                teacher_groups.append(scores.values)
        
        if len(teacher_groups) >= 3:
            h_stat, p_value = kruskal(*teacher_groups)
            sig = "Yes ✓" if p_value < 0.05 else "No"
            self.add_to_report(f"| Teacher scores | {h_stat:.2f} | {p_value:.4f} | {sig} |")
        
        # For LLMs
        llm_groups = []
        for source_id in self.rubric_sources.keys():
            scores = self.df[self.df['source_question_criteria'] == source_id]['all_llm_mean'].dropna()
            if len(scores) > 0:
                llm_groups.append(scores.values)
        
        if len(llm_groups) >= 3:
            h_stat, p_value = kruskal(*llm_groups)
            sig = "Yes ✓" if p_value < 0.05 else "No"
            self.add_to_report(f"| LLM scores | {h_stat:.2f} | {p_value:.4f} | {sig} |")
    
    def question_type_analysis(self):
        """Analyze performance by question type."""
        self.add_to_report("\n## 6. Question Type Performance Analysis")
        
        question_types = self.df['question_type'].unique()
        
        self.add_to_report("\n### 6.1 Score Statistics by Question Type")
        self.add_to_report("\n| Question Type | N | Teacher Mean (±SD) | LLM Mean (±SD) | Teacher-LLM r |")
        self.add_to_report("|---------------|---|-------------------|----------------|---------------|")
        
        for qtype in sorted(question_types):
            subset = self.df[self.df['question_type'] == qtype]
            teacher_scores = subset['teacher_mean'].dropna()
            llm_scores = subset['all_llm_mean'].dropna()
            valid_pairs = subset[['teacher_mean', 'all_llm_mean']].dropna()
            
            teacher_str = f"{teacher_scores.mean():.2f} (±{teacher_scores.std():.2f})" if len(teacher_scores) > 0 else "N/A"
            llm_str = f"{llm_scores.mean():.2f} (±{llm_scores.std():.2f})" if len(llm_scores) > 0 else "N/A"
            
            corr_str = "N/A"
            if len(valid_pairs) > 1:
                corr, _ = spearmanr(valid_pairs['teacher_mean'], valid_pairs['all_llm_mean'])
                corr_str = f"{corr:.3f}"
            
            self.add_to_report(f"| {qtype.upper()} | {len(subset):,} | {teacher_str} | {llm_str} | {corr_str} |")
    
    def dataset_quality_metrics(self):
        """Calculate dataset quality and completeness metrics."""
        self.add_to_report("\n## 7. Dataset Quality Metrics")
        
        # Coverage analysis
        self.add_to_report("\n### 7.1 Dataset Coverage")
        total_possible = self.df['response_id'].nunique() * 5  # responses × rubric sources
        actual_coverage = len(self.df)
        self.add_to_report(f"\n- **Expected evaluation sets:** {total_possible:,} (responses × 5 rubrics)")
        self.add_to_report(f"- **Actual evaluation sets:** {actual_coverage:,}")
        self.add_to_report(f"- **Coverage rate:** {(actual_coverage/total_possible)*100:.1f}%")
        
        # Balance analysis
        self.add_to_report("\n### 7.2 Dataset Balance")
        
        # By rubric source
        self.add_to_report("\n#### Distribution by Rubric Source")
        source_dist = self.df.groupby('rubric_source_name').size()
        expected_per_source = len(self.df) / 5
        
        self.add_to_report("\n| Rubric Source | Count | Expected | Deviation |")
        self.add_to_report("|---------------|-------|----------|-----------|")
        for source, count in source_dist.items():
            deviation = ((count - expected_per_source) / expected_per_source) * 100
            short_name = source.replace('OpenAI Hybrid LLMs', 'OpenAI').replace('DeepSeek Hybrid LLM', 'DeepSeek')
            self.add_to_report(f"| {short_name} | {count:,} | {expected_per_source:.0f} | {deviation:+.1f}% |")
        
        # By question type
        self.add_to_report("\n#### Distribution by Question Type")
        qtype_dist = self.df.groupby('question_type').size()
        self.add_to_report("\n| Question Type | Count | Percentage |")
        self.add_to_report("|---------------|-------|------------|")
        for qtype, count in qtype_dist.items():
            self.add_to_report(f"| {qtype} | {count:,} | {(count/len(self.df))*100:.1f}% |")
        
        # By assignment
        self.add_to_report("\n#### Distribution by Assignment")
        assignment_dist = self.df.groupby('assignment_id').size()
        self.add_to_report("\n| Assignment | Count | Percentage |")
        self.add_to_report("|------------|-------|------------|")
        for assignment, count in assignment_dist.items():
            self.add_to_report(f"| Assignment {assignment} | {count:,} | {(count/len(self.df))*100:.1f}% |")
        
        # Data completeness
        self.add_to_report("\n### 7.3 Data Completeness")
        
        all_score_cols = self.teacher_cols + self.all_llm_cols
        completeness_stats = {}
        
        for col in all_score_cols:
            non_missing = self.df[col].notna().sum()
            completeness_stats[col] = (non_missing / len(self.df)) * 100
        
        teacher_completeness = np.mean([completeness_stats[col] for col in self.teacher_cols])
        llm_completeness = np.mean([completeness_stats[col] for col in self.all_llm_cols])
        
        self.add_to_report(f"\n- **Teacher evaluations completeness:** {teacher_completeness:.1f}%")
        self.add_to_report(f"- **LLM evaluations completeness:** {llm_completeness:.1f}%")
        self.add_to_report(f"- **Overall completeness:** {np.mean(list(completeness_stats.values())):.1f}%")
        
        # Score distribution characteristics
        self.add_to_report("\n### 7.4 Score Distribution Characteristics")
        
        all_scores = pd.concat([self.df[col] for col in all_score_cols]).dropna()
        
        # Check for floor and ceiling effects
        at_floor = (all_scores == 0).sum()
        at_ceiling = (all_scores == 100).sum()
        total_scores = len(all_scores)
        
        self.add_to_report(f"\n- **Total score observations:** {total_scores:,}")
        self.add_to_report(f"- **Scores at floor (0%):** {at_floor:,} ({(at_floor/total_scores)*100:.1f}%)")
        self.add_to_report(f"- **Scores at ceiling (100%):** {at_ceiling:,} ({(at_ceiling/total_scores)*100:.1f}%)")
        
        # Distribution shape
        score_skew = skew(all_scores)
        score_kurt = kurtosis(all_scores)
        
        self.add_to_report(f"- **Skewness:** {score_skew:.3f} ({'right-skewed' if score_skew > 0 else 'left-skewed'})")
        self.add_to_report(f"- **Excess kurtosis:** {score_kurt:.3f} ({'heavy-tailed' if score_kurt > 0 else 'light-tailed'})")
    
    def generate_visualizations(self):
        """Generate comprehensive visualizations."""
        self.add_to_report("\n## 8. Visualizations")
        self.add_to_report("\nGenerating visualization plots...")
        
        # Plot 1: Score distributions comparison
        fig, ax = plt.subplots(figsize=(10, 6))
        data_to_plot = []
        labels = []
        for name, col in [('Teachers', 'teacher_mean'), ('LLM-1', 'llm1_mean'), 
                          ('LLM-4', 'llm4_mean'), ('LLM-13', 'llm13_mean')]:
            scores = self.df[col].dropna()
            if len(scores) > 0:
                data_to_plot.append(scores)
                labels.append(name)
        ax.boxplot(data_to_plot, labels=labels)
        ax.set_title('Score Distributions by Evaluator Type')
        ax.set_ylabel('Score (%)')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'plot_1_score_distributions.png'), dpi=300, bbox_inches='tight')
        plt.close()
        self.add_to_report("\n✓ Created: `plot_1_score_distributions.png`")
        
        # Plot 2: Teacher-LLM Agreement Scatter
        fig, ax = plt.subplots(figsize=(8, 8))
        valid_data = self.df[['teacher_mean', 'all_llm_mean']].dropna()
        if len(valid_data) > 0:
            ax.scatter(valid_data['teacher_mean'], valid_data['all_llm_mean'], alpha=0.5)
            ax.plot([0, 100], [0, 100], 'r--', alpha=0.5, label='Perfect Agreement')
            ax.set_xlabel('Teacher Mean Score (%)')
            ax.set_ylabel('LLM Mean Score (%)')
            ax.set_title('Teacher vs LLM Score Agreement')
            ax.legend()
            ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'plot_2_teacher_llm_agreement.png'), dpi=300, bbox_inches='tight')
        plt.close()
        self.add_to_report("✓ Created: `plot_2_teacher_llm_agreement.png`")
        
        # Plot 3: Score Distribution by Question Type
        fig, ax = plt.subplots(figsize=(12, 6))
        question_types = self.df['question_type'].unique()
        positions = []
        pos = 1
        for qtype in sorted(question_types):
            subset = self.df[self.df['question_type'] == qtype]
            teacher_scores = subset['teacher_mean'].dropna()
            llm_scores = subset['all_llm_mean'].dropna()
            
            if len(teacher_scores) > 0:
                ax.boxplot([teacher_scores], positions=[pos], widths=0.35, 
                          patch_artist=True, boxprops=dict(facecolor='lightblue'))
            if len(llm_scores) > 0:
                ax.boxplot([llm_scores], positions=[pos+0.4], widths=0.35, 
                          patch_artist=True, boxprops=dict(facecolor='lightcoral'))
            positions.append(pos + 0.2)
            pos += 1.5
        
        ax.set_xticks(positions)
        ax.set_xticklabels([qt for qt in sorted(question_types)])
        ax.set_title('Scores by Question Type')
        ax.set_ylabel('Score (%)')
        ax.legend([plt.Line2D([0], [0], color='lightblue', lw=4),
                  plt.Line2D([0], [0], color='lightcoral', lw=4)],
                 ['Teachers', 'LLMs'])
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'plot_3_scores_by_question_type.png'), dpi=300, bbox_inches='tight')
        plt.close()
        self.add_to_report("✓ Created: `plot_3_scores_by_question_type.png`")
        
        # Plot 4: Rubric Source Performance
        fig, ax = plt.subplots(figsize=(12, 6))
        rubric_means_teacher = []
        rubric_means_llm = []
        rubric_labels = []
        
        for source_id, source_name in self.rubric_sources.items():
            subset = self.df[self.df['source_question_criteria'] == source_id]
            if len(subset) > 0:
                teacher_mean = subset['teacher_mean'].dropna().mean()
                llm_mean = subset['all_llm_mean'].dropna().mean()
                if not np.isnan(teacher_mean) and not np.isnan(llm_mean):
                    rubric_means_teacher.append(teacher_mean)
                    rubric_means_llm.append(llm_mean)
                    # Shorten labels for better display
                    short_name = source_name.replace('OpenAI Hybrid LLMs', 'OpenAI').replace('DeepSeek Hybrid LLM', 'DeepSeek')
                    rubric_labels.append(short_name)
        
        if rubric_means_teacher:
            x = np.arange(len(rubric_labels))
            width = 0.35
            ax.bar(x - width/2, rubric_means_teacher, width, label='Teachers', color='skyblue')
            ax.bar(x + width/2, rubric_means_llm, width, label='LLMs', color='lightcoral')
            ax.set_xlabel('Rubric Source')
            ax.set_ylabel('Mean Score (%)')
            ax.set_title('Mean Scores by Rubric Source')
            ax.set_xticks(x)
            ax.set_xticklabels(rubric_labels, rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'plot_4_rubric_source_performance.png'), dpi=300, bbox_inches='tight')
        plt.close()
        self.add_to_report("✓ Created: `plot_4_rubric_source_performance.png`")
        
        # Plot 5: Consistency Analysis
        fig, ax = plt.subplots(figsize=(10, 6))
        consistency_data = []
        consistency_labels = []
        for name, col in [('Teachers', 'teacher_std'), ('LLM-1', 'llm1_std'),
                          ('LLM-4', 'llm4_std'), ('LLM-13', 'llm13_std')]:
            std_scores = self.df[col].dropna()
            if len(std_scores) > 0:
                consistency_data.append(std_scores)
                consistency_labels.append(name)
        
        if consistency_data:
            ax.violinplot(consistency_data, positions=range(1, len(consistency_data)+1))
            ax.set_xticks(range(1, len(consistency_labels)+1))
            ax.set_xticklabels(consistency_labels)
            ax.set_ylabel('Standard Deviation')
            ax.set_title('Evaluation Consistency (Lower is Better)')
            ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'plot_5_consistency_analysis.png'), dpi=300, bbox_inches='tight')
        plt.close()
        self.add_to_report("✓ Created: `plot_5_consistency_analysis.png`")
        
        # Plot 6: Score Differences Distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        diff_scores = self.df['teacher_llm_diff'].dropna()
        if len(diff_scores) > 0:
            ax.hist(diff_scores, bins=30, edgecolor='black', alpha=0.7)
            ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='No Difference')
            ax.axvline(x=diff_scores.mean(), color='blue', linestyle='--', linewidth=2, 
                      label=f'Mean: {diff_scores.mean():.2f}')
            ax.set_xlabel('Score Difference (LLM - Teacher) (%)')
            ax.set_ylabel('Frequency')
            ax.set_title('Distribution of Score Differences')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'plot_6_score_differences.png'), dpi=300, bbox_inches='tight')
        plt.close()
        self.add_to_report("✓ Created: `plot_6_score_differences.png`")
        
        # Plot 7: Correlation Heatmap
        fig, ax = plt.subplots(figsize=(8, 8))
        corr_cols = ['teacher_mean', 'llm1_mean', 'llm4_mean', 'llm13_mean']
        corr_data = self.df[corr_cols].dropna()
        if len(corr_data) > 0:
            corr_matrix = corr_data.corr(method='spearman')
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                       square=True, ax=ax, cbar_kws={'label': 'Spearman Correlation'})
            ax.set_title('Evaluator Correlation Matrix')
            ax.set_xticklabels(['Teachers', 'LLM-1', 'LLM-4', 'LLM-13'], rotation=45)
            ax.set_yticklabels(['Teachers', 'LLM-1', 'LLM-4', 'LLM-13'], rotation=0)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'plot_7_correlation_heatmap.png'), dpi=300, bbox_inches='tight')
        plt.close()
        self.add_to_report("✓ Created: `plot_7_correlation_heatmap.png`")
        
        self.add_to_report("\nAll visualizations saved to the reports folder.")
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        self.add_to_report("\n## 9. Summary and Key Findings")
        
        # Calculate key metrics
        valid_pairs = self.df[['teacher_mean', 'all_llm_mean']].dropna()
        if len(valid_pairs) > 0:
            corr, _ = spearmanr(valid_pairs['teacher_mean'], valid_pairs['all_llm_mean'])
            mean_diff = (valid_pairs['all_llm_mean'] - valid_pairs['teacher_mean']).mean()
            
            self.add_to_report("\n### 9.1 Overall Agreement")
            self.add_to_report(f"\n- **Teacher-LLM correlation:** r = {corr:.3f}")
            self.add_to_report(f"- **Mean score difference (LLM - Teacher):** {mean_diff:+.2f}%")
        
        # Best performing LLM
        self.add_to_report("\n### 9.2 LLM Performance Comparison")
        llm_correlations = {}
        for name, col in [('LLM-1 (GPT-4)', 'llm1_mean'), ('LLM-4 (GPT-4-turbo)', 'llm4_mean'), 
                          ('LLM-13 (GPT-4o)', 'llm13_mean')]:
            valid = self.df[['teacher_mean', col]].dropna()
            if len(valid) > 0:
                corr, _ = spearmanr(valid['teacher_mean'], valid[col])
                llm_correlations[name] = corr
                self.add_to_report(f"- **{name} correlation with teachers:** r = {corr:.3f}")
        
        if llm_correlations:
            best_llm = max(llm_correlations, key=llm_correlations.get)
            self.add_to_report(f"\n**Best performing LLM:** {best_llm}")
        
        # Most consistent evaluator
        self.add_to_report("\n### 9.3 Evaluation Consistency")
        consistency_means = {}
        for name, col in [('Teachers', 'teacher_std'), ('LLM-1', 'llm1_std'),
                          ('LLM-4', 'llm4_std'), ('LLM-13', 'llm13_std')]:
            std_mean = self.df[col].dropna().mean()
            if not np.isnan(std_mean):
                consistency_means[name] = std_mean
                self.add_to_report(f"- **{name} mean SD:** {std_mean:.2f}")
        
        if consistency_means:
            most_consistent = min(consistency_means, key=consistency_means.get)
            self.add_to_report(f"\n**Most consistent evaluator:** {most_consistent}")
        
        # Question type insights
        self.add_to_report("\n### 9.4 Question Type Insights")
        for qtype in sorted(self.df['question_type'].unique()):
            subset = self.df[self.df['question_type'] == qtype]
            valid = subset[['teacher_mean', 'all_llm_mean']].dropna()
            if len(valid) > 0:
                corr, _ = spearmanr(valid['teacher_mean'], valid['all_llm_mean'])
                self.add_to_report(f"- **{qtype}:** N={len(subset)}, Teacher-LLM r={corr:.3f}")
        
        self.add_to_report("\n---")
        self.add_to_report("\n**End of Exploratory Data Analysis Report**")
    
    def save_report(self):
        """Save the markdown report to file."""
        report_path = os.path.join(self.output_dir, 'HARMOGENR_EDA_Report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.report_content))
        print(f"\n✓ Report saved to: {report_path}")
    
    def run_complete_analysis(self):
        """Run the complete exploratory data analysis pipeline."""
        if not self.load_data():
            return
        
        self.basic_statistics()
        self.score_distribution_analysis()
        self.agreement_metrics()
        self.rubric_source_analysis()
        self.question_type_analysis()
        self.dataset_quality_metrics()
        self.generate_visualizations()
        self.generate_summary_report()
        self.save_report()


def main():
    """Main execution function."""
    print("="*80)
    print(" HARMOGEN-R DATASET - EXPLORATORY DATA ANALYSIS ".center(80, "="))
    print("="*80)
    print("\nThis script performs comprehensive exploratory data analysis on the")
    print("HARMOGEN-R dataset and saves results to the 'reports' folder.\n")
    
    # Create analyzer instance
    analyzer = HARMOGENExploratoryAnalysis(
        data_path='datasets/all_evaluations_wide_format_all_assignments_normalized.csv',
        output_dir='reports'
    )
    
    # Run complete analysis
    analyzer.run_complete_analysis()
    
    print("\n" + "="*80)
    print(" ANALYSIS COMPLETE ".center(80, "="))
    print("="*80)
    print("\n✓ Check the 'reports' folder for:")
    print("  - HARMOGENR_EDA_Report.md (complete analysis report)")
    print("  - plot_1_score_distributions.png")
    print("  - plot_2_teacher_llm_agreement.png")
    print("  - plot_3_scores_by_question_type.png")
    print("  - plot_4_rubric_source_performance.png")
    print("  - plot_5_consistency_analysis.png")
    print("  - plot_6_score_differences.png")
    print("  - plot_7_correlation_heatmap.png")


if __name__ == "__main__":
    main()