INSERT INTO customers (name) VALUES
('Acme Corp'), ('Globex Inc'), ('Soylent Co'), ('Initech'), ('Umbrella LLC');

INSERT INTO invoices (customer_id, invoice_date, due_date, amount) VALUES
(1, '2025-07-01', '2025-07-15', 8000.00),
(2, '2025-06-10', '2025-06-25', 12500.00),
(3, '2025-05-05', '2025-05-20', 4750.00),
(4, '2025-04-15', '2025-04-30', 15200.00),
(5, '2025-02-01', '2025-02-15', 10700.00);

INSERT INTO payments (invoice_id, payment_date, amount) VALUES
(1, '2025-07-10', 5000.00),
(3, '2025-05-18', 4750.00),
(4, '2025-05-10', 7000.00);
