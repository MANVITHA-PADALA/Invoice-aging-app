CREATE TABLE customers (
  customer_id INT AUTO_INCREMENT PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE invoices (
  invoice_id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  invoice_date DATE NOT NULL,
  due_date DATE NOT NULL,
  amount DECIMAL(12,2) NOT NULL CHECK (amount >= 0),
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE payments (
  payment_id INT AUTO_INCREMENT PRIMARY KEY,
  invoice_id INT NOT NULL,
  payment_date DATE NOT NULL,
  amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
  FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
);

DELIMITER //
CREATE FUNCTION compute_aging_bucket(due_date DATE, today DATE)
RETURNS VARCHAR(10)
DETERMINISTIC
BEGIN
  DECLARE days_overdue INT;
  IF due_date >= today THEN RETURN 'Current'; END IF;
  SET days_overdue = DATEDIFF(today, due_date);
  IF days_overdue BETWEEN 1 AND 30 THEN RETURN '0-30';
  ELSEIF days_overdue BETWEEN 31 AND 60 THEN RETURN '31-60';
  ELSEIF days_overdue BETWEEN 61 AND 90 THEN RETURN '61-90';
  ELSEIF days_overdue > 90 THEN RETURN '90+'; END IF;
  RETURN 'Current';
END//
DELIMITER ;
