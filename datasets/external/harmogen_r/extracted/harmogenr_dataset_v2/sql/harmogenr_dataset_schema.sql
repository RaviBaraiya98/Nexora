-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: 07-Out-2025 às 01:10
-- Server version: 10.4.28-MariaDB
-- PHP version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `dataset_article`
--

-- --------------------------------------------------------

--
-- Table structure for `assignments`
--

CREATE TABLE `assignments` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `total_score` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  `uc_school_year_id` int(11) NOT NULL,
  `is_active` tinyint(4) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `evaluations`
--

CREATE TABLE `evaluations` (
  `id` int(11) NOT NULL,
  `student_response_id` int(11) NOT NULL,
  `evaluator_type` enum('teacher','llm') NOT NULL,
  `evaluator_id` int(11) NOT NULL COMMENT 'if its teacher will store the user_id if its a llm with store  the llm_id',
  `score` float NOT NULL,
  `feedback` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `criteria_evaluations_by_llm` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`criteria_evaluations_by_llm`)),
  `rag_id` int(11) DEFAULT NULL,
  `source_question_criteria` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1 - Human 2 - LLMs structured 3 - LLMs free 4 - LLM reasoning structured 5 - LLM reasoning free',
  `is_active` tinyint(4) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `evaluation_reports`
--

CREATE TABLE `evaluation_reports` (
  `id` int(11) NOT NULL,
  `assignment_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `evaluator_type` enum('teacher','llm') NOT NULL,
  `evaluator_id` int(11) NOT NULL,
  `short_balance` text NOT NULL,
  `strengths` text DEFAULT NULL,
  `weaknesses` text DEFAULT NULL,
  `suggestions` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `source_question_criteria` int(11) DEFAULT NULL,
  `source_evaluator_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `final_evaluations`
--

CREATE TABLE `final_evaluations` (
  `id` int(11) NOT NULL,
  `response_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `evaluator_id` int(11) DEFAULT NULL,
  `evaluator_type` enum('teacher','llm') NOT NULL,
  `final_score` float NOT NULL,
  `final_feedback` text DEFAULT NULL,
  `source_question_criteria` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1 - Human 2 - LLMs structured 3 - LLMs free 4 - LLM reasoning structured 5 - LLM reasoning free',
  `need_teacher_review` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 - no need for review  1 - need for review',
  `is_active` tinyint(4) NOT NULL DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `llms`
--

CREATE TABLE `llms` (
  `id` int(11) NOT NULL,
  `model_name` varchar(255) NOT NULL,
  `lanchain_class` varchar(100) NOT NULL,
  `type` enum('open-source','premium') NOT NULL,
  `is_active` tinyint(4) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp(),
  `temperature` float DEFAULT 0.2
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `questions`
--

CREATE TABLE `questions` (
  `id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  `question` text NOT NULL,
  `score` float NOT NULL,
  `type` enum('text','code','longtext') NOT NULL,
  `assignment_id` int(11) NOT NULL,
  `is_active` tinyint(4) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `question_criterias`
--

CREATE TABLE `question_criterias` (
  `id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `score_criteria` text NOT NULL,
  `score` float NOT NULL,
  `source` tinyint(4) NOT NULL DEFAULT 1 COMMENT '1 - Human 2 - Openai Hybrid LLMs structured 3 - Openai Hybrid LLMs free 4 - DeepSeek Hybrid LLM structured 5 - DeepSeek Hybrid LLM free',
  `is_active` tinyint(4) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `question_response_examples`
--

CREATE TABLE `question_response_examples` (
  `id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `example_response` text NOT NULL,
  `is_active` tinyint(4) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `rag`
--

CREATE TABLE `rag` (
  `id` int(11) NOT NULL,
  `teacher_id` int(11) NOT NULL,
  `assignment_id` int(11) NOT NULL,
  `collection` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `start_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `is_active` tinyint(4) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `school_years`
--

CREATE TABLE `school_years` (
  `id` int(11) NOT NULL,
  `school_year` varchar(9) NOT NULL,
  `is_active` tinyint(4) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `student_responses`
--

CREATE TABLE `student_responses` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `response` text DEFAULT NULL,
  `is_active` tinyint(4) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `ucs`
--

CREATE TABLE `ucs` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `year` tinyint(4) NOT NULL,
  `course_name` varchar(255) NOT NULL,
  `semester` tinyint(4) NOT NULL CHECK (`semester` in (1,2)),
  `is_active` tinyint(4) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `uc_school_year`
--

CREATE TABLE `uc_school_year` (
  `id` int(11) NOT NULL,
  `uc_id` int(11) NOT NULL,
  `school_year_id` int(11) NOT NULL,
  `is_active` tinyint(4) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `uc_students`
--

CREATE TABLE `uc_students` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `uc_school_year_id` int(11) NOT NULL,
  `is_active` tinyint(4) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for `uc_teachers`
--

CREATE TABLE `uc_teachers` (
  `id` int(11) NOT NULL,
  `teacher_id` int(11) NOT NULL,
  `uc_school_year_id` int(11) NOT NULL,
  `is_active` tinyint(4) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `assignments`
--
ALTER TABLE `assignments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `author_id` (`author_id`),
  ADD KEY `uc_school_year_id` (`uc_school_year_id`),
  ADD KEY `idx_assignments_start_date` (`start_date`),
  ADD KEY `idx_assignments_end_date` (`end_date`);

--
-- Indexes for table `evaluations`
--
ALTER TABLE `evaluations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_response_id` (`student_response_id`),
  ADD KEY `evaluator_id` (`evaluator_id`),
  ADD KEY `rag_id` (`rag_id`),
  ADD KEY `idx_evaluations_evaluator_type` (`evaluator_type`),
  ADD KEY `idx_evaluations_source_question_criteria` (`source_question_criteria`);

--
-- Indexes for table `evaluation_reports`
--
ALTER TABLE `evaluation_reports`
  ADD PRIMARY KEY (`id`),
  ADD KEY `assignment_id` (`assignment_id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `evaluator_id` (`evaluator_id`),
  ADD KEY `idx_evaluation_reports_evaluator_type` (`evaluator_type`);

--
-- Indexes for table `final_evaluations`
--
ALTER TABLE `final_evaluations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `response_id` (`response_id`),
  ADD KEY `idx_final_evaluations_evaluator_type` (`evaluator_type`),
  ADD KEY `idx_final_evaluations_source_question_criteria` (`source_question_criteria`);

--
-- Indexes for table `llms`
--
ALTER TABLE `llms`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `questions`
--
ALTER TABLE `questions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `assignment_id` (`assignment_id`),
  ADD KEY `author_id` (`author_id`);

--
-- Indexes for table `question_criterias`
--
ALTER TABLE `question_criterias`
  ADD PRIMARY KEY (`id`),
  ADD KEY `question_id` (`question_id`);

--
-- Indexes for table `question_response_examples`
--
ALTER TABLE `question_response_examples`
  ADD PRIMARY KEY (`id`),
  ADD KEY `question_id` (`question_id`),
  ADD KEY `author_id` (`author_id`);

--
-- Indexes for table `rag`
--
ALTER TABLE `rag`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `assignment_id` (`assignment_id`),
  ADD UNIQUE KEY `collection` (`collection`),
  ADD KEY `teacher_id` (`teacher_id`);

--
-- Indexes for table `school_years`
--
ALTER TABLE `school_years`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `student_responses`
--
ALTER TABLE `student_responses`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `student_id` (`student_id`,`question_id`),
  ADD KEY `question_id` (`question_id`);

--
-- Indexes for table `ucs`
--
ALTER TABLE `ucs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `uc_school_year`
--
ALTER TABLE `uc_school_year`
  ADD PRIMARY KEY (`id`),
  ADD KEY `uc_id` (`uc_id`),
  ADD KEY `school_year_id` (`school_year_id`);

--
-- Indexes for table `uc_students`
--
ALTER TABLE `uc_students`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `uc_school_year_id` (`uc_school_year_id`);

--
-- Indexes for table `uc_teachers`
--
ALTER TABLE `uc_teachers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `teacher_id` (`teacher_id`),
  ADD KEY `uc_school_year_id` (`uc_school_year_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `assignments`
--
ALTER TABLE `assignments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `evaluations`
--
ALTER TABLE `evaluations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `evaluation_reports`
--
ALTER TABLE `evaluation_reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `final_evaluations`
--
ALTER TABLE `final_evaluations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `llms`
--
ALTER TABLE `llms`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `questions`
--
ALTER TABLE `questions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `question_criterias`
--
ALTER TABLE `question_criterias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `question_response_examples`
--
ALTER TABLE `question_response_examples`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `rag`
--
ALTER TABLE `rag`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `school_years`
--
ALTER TABLE `school_years`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `student_responses`
--
ALTER TABLE `student_responses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ucs`
--
ALTER TABLE `ucs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `uc_school_year`
--
ALTER TABLE `uc_school_year`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `uc_students`
--
ALTER TABLE `uc_students`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `uc_teachers`
--
ALTER TABLE `uc_teachers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `assignments`
--
ALTER TABLE `assignments`
  ADD CONSTRAINT `fk_assignments_uc_school_year` FOREIGN KEY (`uc_school_year_id`) REFERENCES `uc_school_year` (`id`) ON UPDATE CASCADE;

--
-- Constraints for table `evaluations`
--
ALTER TABLE `evaluations`
  ADD CONSTRAINT `fk_evaluations_rag` FOREIGN KEY (`rag_id`) REFERENCES `rag` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_evaluations_student_response` FOREIGN KEY (`student_response_id`) REFERENCES `student_responses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `evaluation_reports`
--
ALTER TABLE `evaluation_reports`
  ADD CONSTRAINT `fk_evaluation_reports_assignment` FOREIGN KEY (`assignment_id`) REFERENCES `assignments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `final_evaluations`
--
ALTER TABLE `final_evaluations`
  ADD CONSTRAINT `fk_final_evaluations_response` FOREIGN KEY (`response_id`) REFERENCES `student_responses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `questions`
--
ALTER TABLE `questions`
  ADD CONSTRAINT `fk_questions_assignment` FOREIGN KEY (`assignment_id`) REFERENCES `assignments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `question_criterias`
--
ALTER TABLE `question_criterias`
  ADD CONSTRAINT `fk_question_criterias_question` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `question_response_examples`
--
ALTER TABLE `question_response_examples`
  ADD CONSTRAINT `fk_question_response_examples_question` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `rag`
--
ALTER TABLE `rag`
  ADD CONSTRAINT `fk_rag_assignment` FOREIGN KEY (`assignment_id`) REFERENCES `assignments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `student_responses`
--
ALTER TABLE `student_responses`
  ADD CONSTRAINT `fk_student_responses_question` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `uc_school_year`
--
ALTER TABLE `uc_school_year`
  ADD CONSTRAINT `fk_uc_school_year_school_year` FOREIGN KEY (`school_year_id`) REFERENCES `school_years` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_uc_school_year_uc` FOREIGN KEY (`uc_id`) REFERENCES `ucs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `uc_students`
--
ALTER TABLE `uc_students`
  ADD CONSTRAINT `fk_uc_students_uc_school_year` FOREIGN KEY (`uc_school_year_id`) REFERENCES `uc_school_year` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `uc_teachers`
--
ALTER TABLE `uc_teachers`
  ADD CONSTRAINT `fk_uc_teachers_uc_school_year` FOREIGN KEY (`uc_school_year_id`) REFERENCES `uc_school_year` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
