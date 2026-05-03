-- 1. categories
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense'))
);

-- 2. users
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. transactions
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(category_id),
    amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    description VARCHAR(255) NOT NULL,
    tx_type VARCHAR(10) NOT NULL CHECK (tx_type IN ('income', 'expense')),
    transaction_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. budgets
CREATE TABLE budgets (
    budget_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(category_id),
    limit_amount NUMERIC(10,2) NOT NULL,
    month_year DATE NOT NULL,
    UNIQUE (user_id, category_id, month_year)
);

-- 5. budget_alerts
CREATE TABLE budget_alerts (
    alert_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(category_id),
    spent NUMERIC(10,2),
    limit_amount NUMERIC(10,2),
    alerted_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. ai_insights
CREATE TABLE ai_insights (
    insight_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    prompt_sent TEXT,
    insight_text TEXT,
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Views
CREATE VIEW monthly_summary AS
SELECT 
    user_id, 
    TO_CHAR(transaction_date, 'YYYY-MM') AS month,
    SUM(CASE WHEN tx_type = 'income' THEN amount ELSE 0 END) AS income,
    SUM(CASE WHEN tx_type = 'expense' THEN amount ELSE 0 END) AS expense
FROM transactions
GROUP BY user_id, month;

CREATE VIEW category_totals AS
SELECT 
    t.user_id, 
    c.name AS category, 
    t.tx_type, 
    SUM(t.amount) AS total
FROM transactions t
JOIN categories c ON t.category_id = c.category_id
GROUP BY t.user_id, c.name, t.tx_type;

-- Indexes
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_user_date ON transactions(user_id, transaction_date);

-- Functions
CREATE OR REPLACE FUNCTION add_transaction(
    p_user_id INTEGER, 
    p_cat_id INTEGER, 
    p_amount NUMERIC, 
    p_desc VARCHAR, 
    p_type VARCHAR, 
    p_date DATE
) RETURNS void AS $$
BEGIN
    INSERT INTO transactions (user_id, category_id, amount, description, tx_type, transaction_date)
    VALUES (p_user_id, p_cat_id, p_amount, p_desc, p_type, p_date);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_transaction(
    p_tx_id INTEGER, 
    p_user_id INTEGER
) RETURNS void AS $$
BEGIN
    DELETE FROM transactions 
    WHERE transaction_id = p_tx_id AND user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION set_budget(
    p_user_id INTEGER, 
    p_cat_id INTEGER, 
    p_limit NUMERIC, 
    p_month DATE
) RETURNS void AS $$
BEGIN
    INSERT INTO budgets (user_id, category_id, limit_amount, month_year)
    VALUES (p_user_id, p_cat_id, p_limit, p_month)
    ON CONFLICT (user_id, category_id, month_year) 
    DO UPDATE SET limit_amount = EXCLUDED.limit_amount;
END;
$$ LANGUAGE plpgsql;

-- Triggers
CREATE OR REPLACE FUNCTION check_budget_after_insert() RETURNS trigger AS $$
DECLARE
    v_limit NUMERIC;
    v_spent NUMERIC;
BEGIN
    IF NEW.tx_type = 'expense' THEN
        -- Get budget limit for this category and month
        SELECT limit_amount INTO v_limit 
        FROM budgets 
        WHERE user_id = NEW.user_id 
          AND category_id = NEW.category_id 
          AND month_year = DATE_TRUNC('month', NEW.transaction_date);

        IF v_limit IS NOT NULL THEN
            -- Sum spending for this category and month
            SELECT SUM(amount) INTO v_spent 
            FROM transactions 
            WHERE user_id = NEW.user_id 
              AND category_id = NEW.category_id 
              AND DATE_TRUNC('month', transaction_date) = DATE_TRUNC('month', NEW.transaction_date);

            IF v_spent > v_limit THEN
                INSERT INTO budget_alerts (user_id, category_id, spent, limit_amount)
                VALUES (NEW.user_id, NEW.category_id, v_spent, v_limit);
            END IF;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_budget
AFTER INSERT ON transactions
FOR EACH ROW EXECUTE FUNCTION check_budget_after_insert();

CREATE OR REPLACE FUNCTION limit_insight_history() RETURNS trigger AS $$
BEGIN
    DELETE FROM ai_insights 
    WHERE user_id = NEW.user_id 
      AND insight_id NOT IN (
          SELECT insight_id 
          FROM ai_insights 
          WHERE user_id = NEW.user_id 
          ORDER BY generated_at DESC 
          LIMIT 10
      );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_limit_insights
AFTER INSERT ON ai_insights
FOR EACH ROW EXECUTE FUNCTION limit_insight_history();
