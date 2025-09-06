CREATE DATABASE IF NOT EXISTS ecofind;
USE ecofind;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_email (email),
    INDEX idx_username (username)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL, -- Precise for currency
    image_url VARCHAR(500) DEFAULT '/static/placeholder.jpg',
    is_active TINYINT(1) DEFAULT 1, -- Soft delete: 1 = active, 0 = deleted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraint
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Indexes for critical queries: browsing, filtering, searching
    INDEX idx_user_id (user_id),           -- For "My Listings"
    INDEX idx_category (category),         -- For category filtering
    INDEX idx_is_active (is_active),       -- To quickly find active products
    INDEX idx_price (price),               -- For potential future sorting by price
    FULLTEXT INDEX ft_title (title)        -- For efficient keyword search (MyISAM/InnoDB MySQL 5.6+)
) ENGINE=InnoDB;

-- Purchases Table
-- Optimized: Indexes on user_id and purchase_date for fast retrieval of purchase history
CREATE TABLE IF NOT EXISTS purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    purchase_price DECIMAL(10, 2) NOT NULL,
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_purchase_date (purchase_date)
) ENGINE=InnoDB;

INSERT INTO users (username, email, password) VALUES
('testuser', 'test@example.com', 'password123'),
('alice_green', 'alice@example.com', 'eco_friendly'),
('bob_brown', 'bob@example.com', 'reuse_reduce');

INSERT INTO products (user_id, title, description, category, price, image_url) VALUES
(1, 'Vintage Film Camera', 'Classic 35mm camera, perfect for photography enthusiasts.', 'Electronics', 120.00, '/static/camera.jpg'),
(1, 'Solid Oak Bookshelf', 'Handcrafted bookshelf with 5 spacious shelves.', 'Furniture', 85.50, '/static/bookshelf.jpg'),
(2, 'Mountain Bike', 'Lightly used mountain bike, great condition.', 'Sports', 200.00, '/static/bike.jpg'),
(2, 'Python Programming Book', 'Learn Python the Hard Way - Excellent condition.', 'Books', 15.99, '/static/book.jpg'),
(3, 'Designer Leather Jacket', 'Stylish black leather jacket, size M.', 'Clothing', 75.00, '/static/jacket.jpg');

ALTER TABLE products ADD COLUMN location VARCHAR(100) DEFAULT NULL AFTER image_url;

ALTER TABLE products ADD COLUMN eco_score FLOAT DEFAULT 0.0;