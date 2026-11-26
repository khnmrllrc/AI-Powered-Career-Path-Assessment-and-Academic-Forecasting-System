-- AI-Powered Career Path Assessment and Academic Forecasting System
-- Standalone reference schema derived from careerpath/career/models.py.
-- MySQL-compatible SQL for phpMyAdmin. Django's built-in auth tables are included
-- because StudentUser extends AbstractUser.

START TRANSACTION;

CREATE TABLE student_user (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser TINYINT(1) NOT NULL DEFAULT 0,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(30) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL UNIQUE,
    is_staff TINYINT(1) NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    student_id VARCHAR(20) NOT NULL UNIQUE,
    middle_name VARCHAR(50) NOT NULL DEFAULT '',
    suffix VARCHAR(10) NOT NULL DEFAULT '',
    qr_code CHAR(36) NULL UNIQUE
);

CREATE TABLE career_path (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT NOT NULL,
    courses TEXT NOT NULL,
    success_rate DOUBLE NOT NULL DEFAULT 0
        CHECK (success_rate >= 0 AND success_rate <= 100)
);

CREATE TABLE assessment_question (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    career_categories TEXT NOT NULL,
    options TEXT NOT NULL,
    `order` INTEGER NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT assessment_question_text_type_unique
        UNIQUE (question_text, question_type)
);

CREATE TABLE assessment_library_file (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    course_category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    file VARCHAR(100) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    uploaded_by_id BIGINT UNSIGNED NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT assessment_library_file_uploaded_by_fk FOREIGN KEY (uploaded_by_id) REFERENCES student_user(id) ON DELETE SET NULL
);

CREATE TABLE student_assessment (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT UNSIGNED NOT NULL,
    career_category VARCHAR(50) NOT NULL DEFAULT '',
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    total_score DOUBLE NULL,
    CONSTRAINT student_assessment_student_fk FOREIGN KEY (student_id) REFERENCES student_user(id) ON DELETE CASCADE
);

CREATE TABLE assessment_response (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    assessment_id BIGINT UNSIGNED NOT NULL,
    question_id BIGINT UNSIGNED NOT NULL,
    selected_option INTEGER NOT NULL,
    points_earned TEXT NOT NULL,
    CONSTRAINT assessment_response_assessment_fk FOREIGN KEY (assessment_id) REFERENCES student_assessment(id) ON DELETE CASCADE,
    CONSTRAINT assessment_response_question_fk FOREIGN KEY (question_id) REFERENCES assessment_question(id) ON DELETE CASCADE,
    CONSTRAINT assessment_response_assessment_question_unique
        UNIQUE (assessment_id, question_id)
);

CREATE TABLE career_recommendation (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT UNSIGNED NOT NULL UNIQUE,
    recommendation_text TEXT NOT NULL,
    compatibility_score DOUBLE NOT NULL
        CHECK (compatibility_score >= 0 AND compatibility_score <= 100),
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT career_recommendation_student_fk FOREIGN KEY (student_id) REFERENCES student_user(id) ON DELETE CASCADE
);

CREATE TABLE career_recommendation_career_paths (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    careerrecommendation_id BIGINT UNSIGNED NOT NULL,
    careerpath_id BIGINT UNSIGNED NOT NULL,
    CONSTRAINT recommendation_career_recommendation_fk FOREIGN KEY (careerrecommendation_id) REFERENCES career_recommendation(id) ON DELETE CASCADE,
    CONSTRAINT recommendation_career_path_fk FOREIGN KEY (careerpath_id) REFERENCES career_path(id) ON DELETE CASCADE,
    CONSTRAINT recommendation_career_path_unique
        UNIQUE (careerrecommendation_id, careerpath_id)
);

CREATE TABLE academic_forecast (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT UNSIGNED NOT NULL UNIQUE,
    selected_career_path_id BIGINT UNSIGNED NULL,
    predicted_success_rate DOUBLE NOT NULL
        CHECK (predicted_success_rate >= 0 AND predicted_success_rate <= 100),
    improvement_areas TEXT NOT NULL,
    recommended_subjects TEXT NOT NULL,
    forecast_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT academic_forecast_student_fk FOREIGN KEY (student_id) REFERENCES student_user(id) ON DELETE CASCADE,
    CONSTRAINT academic_forecast_career_path_fk FOREIGN KEY (selected_career_path_id) REFERENCES career_path(id) ON DELETE SET NULL
);

CREATE TABLE in_demand_career (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `rank` INTEGER NOT NULL UNIQUE,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT NOT NULL,
    average_salary VARCHAR(100) NOT NULL,
    job_growth VARCHAR(50) NOT NULL
);

CREATE TABLE in_demand_career_related_careers (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    indemandcareer_id BIGINT UNSIGNED NOT NULL,
    careerpath_id BIGINT UNSIGNED NOT NULL,
    CONSTRAINT in_demand_career_fk FOREIGN KEY (indemandcareer_id) REFERENCES in_demand_career(id) ON DELETE CASCADE,
    CONSTRAINT in_demand_career_path_fk FOREIGN KEY (careerpath_id) REFERENCES career_path(id) ON DELETE CASCADE,
    CONSTRAINT in_demand_career_related_unique
        UNIQUE (indemandcareer_id, careerpath_id)
);

CREATE TABLE student_skill_profile (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT UNSIGNED NOT NULL UNIQUE,
    skills TEXT NOT NULL,
    strengths TEXT NOT NULL,
    weaknesses TEXT NOT NULL,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT student_skill_profile_student_fk FOREIGN KEY (student_id) REFERENCES student_user(id) ON DELETE CASCADE
);

CREATE TABLE student_report (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT UNSIGNED NOT NULL UNIQUE,
    assessment_score DOUBLE NULL,
    counselor_notes TEXT NOT NULL,
    is_flagged TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT student_report_student_fk FOREIGN KEY (student_id) REFERENCES student_user(id) ON DELETE CASCADE
);

CREATE TABLE student_report_recommended_paths (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    studentreport_id BIGINT UNSIGNED NOT NULL,
    careerpath_id BIGINT UNSIGNED NOT NULL,
    CONSTRAINT student_report_fk FOREIGN KEY (studentreport_id) REFERENCES student_report(id) ON DELETE CASCADE,
    CONSTRAINT student_report_path_fk FOREIGN KEY (careerpath_id) REFERENCES career_path(id) ON DELETE CASCADE,
    CONSTRAINT student_report_career_path_unique
        UNIQUE (studentreport_id, careerpath_id)
);

CREATE TABLE django_content_type (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    CONSTRAINT django_content_type_app_model_unique UNIQUE (app_label, model)
);

CREATE TABLE auth_permission (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id BIGINT UNSIGNED NOT NULL,
    codename VARCHAR(100) NOT NULL,
    CONSTRAINT auth_permission_content_type_codename_unique
        UNIQUE (content_type_id, codename)
);

CREATE TABLE auth_group (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE auth_group_permissions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    group_id BIGINT UNSIGNED NOT NULL,
    permission_id BIGINT UNSIGNED NOT NULL,
    CONSTRAINT auth_group_fk FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
    CONSTRAINT auth_group_permission_fk FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
    CONSTRAINT auth_group_permission_unique UNIQUE (group_id, permission_id)
);

CREATE TABLE student_user_groups (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    studentuser_id BIGINT UNSIGNED NOT NULL,
    group_id BIGINT UNSIGNED NOT NULL,
    CONSTRAINT student_user_fk FOREIGN KEY (studentuser_id) REFERENCES student_user(id) ON DELETE CASCADE,
    CONSTRAINT student_group_fk FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
    CONSTRAINT student_user_group_unique UNIQUE (studentuser_id, group_id)
);

CREATE TABLE student_user_user_permissions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    studentuser_id BIGINT UNSIGNED NOT NULL,
    permission_id BIGINT UNSIGNED NOT NULL,
    CONSTRAINT student_user_permission_fk FOREIGN KEY (studentuser_id) REFERENCES student_user(id) ON DELETE CASCADE,
    CONSTRAINT student_permission_fk FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
    CONSTRAINT student_user_permission_unique UNIQUE (studentuser_id, permission_id)
);

CREATE INDEX assessment_library_file_course_category_idx
    ON assessment_library_file(course_category);
CREATE INDEX student_assessment_student_status_idx
    ON student_assessment(student_id, status);
CREATE INDEX assessment_response_assessment_idx
    ON assessment_response(assessment_id);
CREATE INDEX assessment_response_question_idx
    ON assessment_response(question_id);
CREATE INDEX assessment_question_order_idx
    ON assessment_question(`order`);

COMMIT;
