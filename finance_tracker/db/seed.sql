-- Insert default categories
INSERT INTO categories (name, type) VALUES 
('Salary', 'income'),
('Freelance', 'income'),
('Food', 'expense'),
('Transport', 'expense'),
('Utilities', 'expense'),
('Health', 'expense'),
('Entertainment', 'expense'),
('Other', 'expense');

-- Insert demo user
-- Note: password_hash 'pbkdf2:sha256:...' is a placeholder. 
-- It must be replaced with a real werkzeug.security.generate_password_hash output before use.
INSERT INTO users (username, email, password_hash) VALUES 
('demo_user', 'demo@test.com', 'pbkdf2:sha256:600000$placeholder$hash');
