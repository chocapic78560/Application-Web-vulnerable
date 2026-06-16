-- MyEduConnect Database Schema

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    -- VULN: passwords stored as MD5 (weak cryptography)
    password_hash VARCHAR(64) NOT NULL,
    role VARCHAR(20) DEFAULT 'student',
    full_name VARCHAR(200),
    phone VARCHAR(20),
    ic_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(10,2) DEFAULT 0.00,
    instructor_id INTEGER REFERENCES users(id),
    thumbnail VARCHAR(300),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    course_id INTEGER REFERENCES courses(id),
    enrolled_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    course_id INTEGER REFERENCES courses(id),
    amount DECIMAL(10,2),
    card_last4 VARCHAR(4),
    -- VULN: storing partial card data in plaintext
    card_holder VARCHAR(200),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    -- VULN: admin password stored as MD5("admin123") = 0192023a7bbd73250516f069df18b500
    password_hash VARCHAR(64) NOT NULL,
    email VARCHAR(200)
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(200),
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sample data

-- VULN: MD5 hashes (md5("password123") = 482c811da5d5b4bc6d497ffa98491e38)
INSERT INTO users (username, email, password_hash, role, full_name, ic_number) VALUES
('ali_hassan',    'ali.hassan@student.edu.my',    '482c811da5d5b4bc6d497ffa98491e38', 'student',  'Ali Hassan',    '001234-56-7890'),
('siti_rahman',   'siti.rahman@student.edu.my',   '482c811da5d5b4bc6d497ffa98491e38', 'student',  'Siti Rahman',   '002345-67-8901'),
('john_tan',      'john.tan@teacher.edu.my',       '482c811da5d5b4bc6d497ffa98491e38', 'teacher',  'John Tan',      '003456-78-9012'),
('nurul_aziz',    'nurul.aziz@student.edu.my',     '482c811da5d5b4bc6d497ffa98491e38', 'student',  'Nurul Aziz',    '004567-89-0123'),
('raj_kumar',     'raj.kumar@teacher.edu.my',      '482c811da5d5b4bc6d497ffa98491e38', 'teacher',  'Raj Kumar',     '005678-90-1234');

-- admin password = "admin123" (MD5)
INSERT INTO admins (username, password_hash, email) VALUES
('admin', '0192023a7bbd73250516f069df18b500', 'admin@myeduconnect.com.my'),
('user', '482c811da5d5b4bc6d497ffa98491e38', 'user@myeduconnect.com.ny');

INSERT INTO courses (title, description, category, price, instructor_id, thumbnail) VALUES
('SPM Mathematics Form 4 & 5',       'Complete SPM prep covering algebra, geometry and statistics.', 'Mathematics', 49.90, 3, 'math_spm.jpg'),
('STPM Chemistry Full Course',        'In-depth STPM Chemistry with practicals and past year papers.', 'Science',     79.90, 5, 'chem_stpm.jpg'),
('English Language Mastery',          'MUET & SPM English — writing, reading, speaking components.',  'Language',    39.90, 3, 'english.jpg'),
('Sejarah SPM — Tingkatan 4 & 5',     'Comprehensive coverage of Malaysian history syllabus.',        'Humanities',  34.90, 5, 'sejarah.jpg'),
('Additional Mathematics (Add Maths)', 'Step-by-step Add Maths from basics to advanced topics.',      'Mathematics', 59.90, 3, 'addmath.jpg'),
('Biology Form 4 & 5',               'SPM Biology with diagrams, experiments and exam tips.',        'Science',     44.90, 5, 'bio.jpg');

INSERT INTO enrollments (student_id, course_id) VALUES (1,1),(1,3),(2,2),(2,4),(4,1),(4,5),(4,6);

INSERT INTO payments (user_id, course_id, amount, card_last4, card_holder, status) VALUES
(1, 1, 49.90, '4242', 'Ali Hassan',   'completed'),
(2, 2, 79.90, '1234', 'Siti Rahman',  'completed'),
(4, 5, 59.90, '5678', 'Nurul Aziz',   'completed');
