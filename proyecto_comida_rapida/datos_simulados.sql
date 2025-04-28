-- Eliminar tablas si existen para empezar limpio
DROP TABLE IF EXISTS product_template;
DROP TABLE IF EXISTS sale_order;
DROP TABLE IF EXISTS sale_order_line;
DROP TABLE IF EXISTS stock_quant;
DROP TABLE IF EXISTS res_partner;

-- Crear tabla de productos
CREATE TABLE product_template (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    list_price REAL NOT NULL,
    cost_price REAL NOT NULL,
    category TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

-- Crear tabla de pedidos
CREATE TABLE sale_order (
    id INTEGER PRIMARY KEY,
    date_order TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    total_amount REAL NOT NULL
);

-- Crear tabla de líneas de pedido
CREATE TABLE sale_order_line (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price_unit REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES sale_order(id),
    FOREIGN KEY (product_id) REFERENCES product_template(id)
);

-- Crear tabla de existencias
CREATE TABLE stock_quant (
    product_id INTEGER PRIMARY KEY,
    quantity_available INTEGER NOT NULL,
    FOREIGN KEY (product_id) REFERENCES product_template(id)
);

-- Crear tabla de clientes
CREATE TABLE res_partner (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    city TEXT NOT NULL,
    number_of_orders INTEGER NOT NULL DEFAULT 0
);

-- Insertar datos en product_template
INSERT INTO product_template (id, name, list_price, cost_price, category, is_active) VALUES
-- Hamburguesas
(1, 'Hamburguesa Clásica', 5.99, 2.20, 'hamburguesas', 1),
(2, 'Hamburguesa con Queso', 6.49, 2.50, 'hamburguesas', 1),
(3, 'Hamburguesa Doble', 7.99, 3.40, 'hamburguesas', 1),
(4, 'Hamburguesa Vegana', 8.49, 4.10, 'hamburguesas', 1),
(5, 'Hamburguesa Picante', 7.49, 2.80, 'hamburguesas', 1),
(6, 'Hamburguesa XL', 9.99, 4.50, 'hamburguesas', 1),
(7, 'Hamburguesa BBQ', 7.99, 3.20, 'hamburguesas', 1),
-- Wraps
(8, 'Wrap de Pollo', 5.49, 2.10, 'wraps', 1),
(9, 'Wrap Vegetariano', 4.99, 1.80, 'wraps', 1),
(10, 'Wrap César', 5.99, 2.30, 'wraps', 1),
(11, 'Wrap BBQ', 5.99, 2.25, 'wraps', 1),
(12, 'Wrap Mexicano', 6.49, 2.40, 'wraps', 0),  -- Producto descontinuado
-- Patatas
(13, 'Patatas Fritas Pequeñas', 2.49, 0.60, 'patatas', 1),
(14, 'Patatas Fritas Medianas', 3.49, 0.80, 'patatas', 1),
(15, 'Patatas Fritas Grandes', 4.49, 1.10, 'patatas', 1),
(16, 'Patatas Deluxe', 4.99, 1.50, 'patatas', 1),
(17, 'Patatas con Queso', 5.49, 1.80, 'patatas', 1),
-- Bebidas
(18, 'Refresco Cola Pequeño', 1.99, 0.40, 'bebidas', 1),
(19, 'Refresco Cola Mediano', 2.49, 0.50, 'bebidas', 1),
(20, 'Refresco Cola Grande', 2.99, 0.60, 'bebidas', 1),
(21, 'Agua Mineral', 1.49, 0.30, 'bebidas', 1),
(22, 'Cerveza', 3.49, 1.20, 'bebidas', 1),
(23, 'Zumo de Naranja', 2.49, 0.90, 'bebidas', 1),
-- Postres
(24, 'Helado de Vainilla', 2.99, 1.10, 'postres', 1),
(25, 'Brownie con Helado', 4.99, 1.80, 'postres', 1),
(26, 'Tarta de Queso', 3.99, 1.50, 'postres', 1),
(27, 'Sundae de Chocolate', 3.49, 1.30, 'postres', 1),
-- Complementos
(28, 'Nuggets de Pollo (6uds)', 4.99, 1.90, 'complementos', 1),
(29, 'Aros de Cebolla', 3.99, 1.40, 'complementos', 1),
(30, 'Ensalada César', 5.99, 2.50, 'complementos', 1),
-- Promociones
(31, 'Menú Hamburguesa Clásica', 9.99, 4.00, 'promociones', 1),
(32, 'Menú Hamburguesa con Queso', 10.49, 4.30, 'promociones', 1),
(33, 'Menú Infantil', 6.99, 3.10, 'promociones', 1),
(34, 'Combo Familiar', 24.99, 11.50, 'promociones', 1),
(35, 'Desayuno Completo', 7.99, 3.80, 'promociones', 0);  -- Promoción descontinuada

-- Insertar datos en res_partner
INSERT INTO res_partner (id, name, email, city, number_of_orders) VALUES
(1, 'Juan Pérez', 'juan.perez@gmail.com', 'Madrid', 8),
(2, 'María López', 'maria.lopez@hotmail.com', 'Barcelona', 5),
(3, 'Carlos Rodríguez', 'carlos.rod@empresa.com', 'Madrid', 12),
(4, 'Laura Martínez', 'laura.m@gmail.com', 'Valencia', 3),
(5, 'Pedro Sánchez', 'pedro.s@outlook.com', 'Sevilla', 2),
(6, 'Ana García', 'ana.garcia@gmail.com', 'Barcelona', 7),
(7, 'Miguel Torres', 'miguel.torres@empresa.com', 'Madrid', 4),
(8, 'Sofía Ruiz', 'sofia.r@hotmail.com', 'Valencia', 9),
(9, 'Javier Fernández', 'javier.f@gmail.com', 'Sevilla', 6),
(10, 'Carmen Moreno', 'carmen.m@empresa.com', 'Madrid', 3),
(11, 'Restaurante Sabor', 'info@sabor.com', 'Barcelona', 15),
(12, 'Hotel Gran Vía', 'eventos@granvia.com', 'Madrid', 20),
(13, 'Oficinas Central', 'compras@central.com', 'Valencia', 18),
(14, 'Colegio San José', 'comedor@sanjose.edu', 'Sevilla', 25),
(15, 'Empresa Tecnología', 'pedidos@tecnologia.com', 'Madrid', 10);

-- Insertar datos en sale_order y sale_order_line
-- Pedidos de enero
INSERT INTO sale_order (id, date_order, customer_name, total_amount) VALUES
(1, '2025-01-05', 'Juan Pérez', 17.97),
(2, '2025-01-08', 'María López', 29.97),
(3, '2025-01-12', 'Carlos Rodríguez', 15.47),
(4, '2025-01-15', 'Restaurante Sabor', 124.50),
(5, '2025-01-18', 'Laura Martínez', 10.48),
(6, '2025-01-22', 'Pedro Sánchez', 9.99),
(7, '2025-01-25', 'Ana García', 39.96),
(8, '2025-01-28', 'Miguel Torres', 21.97),
(9, '2025-01-30', 'Colegio San José', 153.75);

-- Pedidos de febrero
INSERT INTO sale_order (id, date_order, customer_name, total_amount) VALUES
(10, '2025-02-03', 'Sofía Ruiz', 14.97),
(11, '2025-02-05', 'Javier Fernández', 24.99),
(12, '2025-02-08', 'Carmen Moreno', 15.47),
(13, '2025-02-10', 'Hotel Gran Vía', 87.35),
(14, '2025-02-14', 'Juan Pérez', 27.47),
(15, '2025-02-18', 'Oficinas Central', 63.92),
(16, '2025-02-20', 'María López', 10.48),
(17, '2025-02-23', 'Carlos Rodríguez', 34.97),
(18, '2025-02-26', 'Empresa Tecnología', 49.98);

-- Pedidos de marzo
INSERT INTO sale_order (id, date_order, customer_name, total_amount) VALUES
(19, '2025-03-02', 'Laura Martínez', 20.97),
(20, '2025-03-05', 'Pedro Sánchez', 13.48),
(21, '2025-03-08', 'Restaurante Sabor', 97.85),
(22, '2025-03-12', 'Ana García', 24.99),
(23, '2025-03-15', 'Juan Pérez', 17.47),
(24, '2025-03-18', 'Miguel Torres', 9.99),
(25, '2025-03-21', 'Sofía Ruiz', 42.95),
(26, '2025-03-24', 'Hotel Gran Vía', 79.98),
(27, '2025-03-27', 'Javier Fernández', 13.47),
(28, '2025-03-30', 'Carmen Moreno', 15.97);

-- Pedidos de abril (mes actual)
INSERT INTO sale_order (id, date_order, customer_name, total_amount) VALUES
(29, '2025-04-01', 'Carlos Rodríguez', 28.47),
(30, '2025-04-03', 'Colegio San José', 174.93),
(31, '2025-04-05', 'Laura Martínez', 17.97),
(32, '2025-04-08', 'Juan Pérez', 24.99),
(33, '2025-04-10', 'Oficinas Central', 89.94),
(34, '2025-04-12', 'María López', 12.98),
(35, '2025-04-14', 'Pedro Sánchez', 9.99),
(36, '2025-04-16', 'Empresa Tecnología', 54.97),
(37, '2025-04-18', 'Ana García', 19.47),
(38, '2025-04-20', 'Restaurante Sabor', 108.75),
(39, '2025-04-22', 'Juan Pérez', 32.97),
(40, '2025-04-24', 'Carlos Rodríguez', 24.99);

-- Líneas de pedido para los pedidos (solo mostramos algunas, el resto serían similares)
INSERT INTO sale_order_line (id, order_id, product_id, quantity, price_unit) VALUES
-- Pedido 1
(1, 1, 1, 1, 5.99),  -- Hamburguesa Clásica
(2, 1, 14, 1, 3.49), -- Patatas Medianas
(3, 1, 19, 1, 2.49), -- Refresco Cola Mediano
(4, 1, 24, 1, 2.99), -- Helado de Vainilla
(5, 1, 13, 1, 2.49), -- Patatas Pequeñas

-- Pedido 2
(6, 2, 3, 2, 7.99),  -- 2 Hamburguesas Dobles
(7, 2, 15, 1, 4.49), -- Patatas Grandes
(8, 2, 20, 2, 2.99), -- 2 Refrescos Grandes
(9, 2, 25, 1, 4.99), -- Brownie con Helado

-- Pedido 3
(10, 3, 8, 1, 5.49), -- Wrap de Pollo
(11, 3, 13, 1, 2.49), -- Patatas Pequeñas
(12, 3, 18, 1, 1.99), -- Refresco Pequeño
(13, 3, 21, 1, 1.49), -- Agua Mineral
(14, 3, 24, 1, 2.99), -- Helado

-- Pedido 4 (pedido grande de restaurante)
(15, 4, 1, 5, 5.99),  -- 5 Hamburguesas Clásicas
(16, 4, 3, 3, 7.99),  -- 3 Hamburguesas Dobles
(17, 4, 8, 4, 5.49),  -- 4 Wraps de Pollo
(18, 4, 14, 6, 3.49), -- 6 Patatas Medianas
(19, 4, 19, 8, 2.49), -- 8 Refrescos Medianos

-- Más líneas de pedido 
(20, 5, 9, 1, 4.99),  -- Wrap Vegetariano
(21, 5, 13, 1, 2.49), -- Patatas Pequeñas
(22, 5, 23, 1, 2.49), -- Zumo de Naranja

-- Pedido 6
(23, 6, 31, 1, 9.99), -- Menú Hamburguesa Clásica

-- Pedido 7
(24, 7, 6, 2, 9.99),  -- 2 Hamburguesas XL
(25, 7, 15, 2, 4.49), -- 2 Patatas Grandes
(26, 7, 20, 2, 2.99), -- 2 Refrescos Grandes
(27, 7, 25, 2, 4.99), -- 2 Brownies con Helado

-- Pedidos recientes (abril)
(100, 38, 1, 5, 5.99), -- 5 Hamburguesas Clásicas
(101, 38, 2, 4, 6.49), -- 4 Hamburguesas con Queso
(102, 38, 13, 10, 2.49), -- 10 Patatas Pequeñas
(103, 38, 19, 15, 2.49), -- 15 Refrescos Medianos

(104, 39, 3, 2, 7.99), -- 2 Hamburguesas Dobles
(105, 39, 14, 2, 3.49), -- 2 Patatas Medianas
(106, 39, 25, 2, 4.99), -- 2 Brownies con Helado

(107, 40, 31, 1, 9.99), -- Menú Hamburguesa Clásica
(108, 40, 33, 1, 6.99), -- Menú Infantil
(109, 40, 25, 1, 4.99); -- Brownie con Helado

-- Insertar más líneas de pedido relacionadas con wraps para mostrar tendencias
INSERT INTO sale_order_line (id, order_id, product_id, quantity, price_unit) VALUES
(110, 10, 8, 1, 5.49),  -- Wrap de Pollo (febrero)
(111, 12, 9, 1, 4.99),  -- Wrap Vegetariano (febrero)
(112, 14, 10, 2, 5.99), -- 2 Wraps César (febrero)
(113, 17, 8, 1, 5.49),  -- Wrap de Pollo (febrero)
(114, 19, 11, 1, 5.99), -- Wrap BBQ (marzo)
(115, 22, 8, 2, 5.49),  -- 2 Wraps de Pollo (marzo)
(116, 25, 9, 1, 4.99),  -- Wrap Vegetariano (marzo)
(117, 27, 10, 1, 5.99), -- Wrap César (marzo)
(118, 29, 8, 2, 5.49),  -- 2 Wraps de Pollo (abril)
(119, 31, 9, 1, 4.99),  -- Wrap Vegetariano (abril)
(120, 34, 10, 1, 5.99), -- Wrap César (abril)
(121, 37, 11, 1, 5.99); -- Wrap BBQ (abril)

-- Insertar datos de stock
INSERT INTO stock_quant (product_id, quantity_available) VALUES
(1, 35),   -- Hamburguesa Clásica (buen stock)
(2, 28),   -- Hamburguesa con Queso (buen stock)
(3, 15),   -- Hamburguesa Doble (stock moderado)
(4, 8),    -- Hamburguesa Vegana (stock bajo)
(5, 12),   -- Hamburguesa Picante (stock moderado)
(6, 5),    -- Hamburguesa XL (stock bajo)
(7, 18),   -- Hamburguesa BBQ (stock moderado)
(8, 4),    -- Wrap de Pollo (stock crítico)
(9, 7),    -- Wrap Vegetariano (stock bajo)
(10, 9),   -- Wrap César (stock bajo)
(11, 11),  -- Wrap BBQ (stock moderado)
(12, 0),   -- Wrap Mexicano (sin stock, descontinuado)
(13, 45),  -- Patatas Pequeñas (buen stock)
(14, 38),  -- Patatas Medianas (buen stock)
(15, 25),  -- Patatas Grandes (buen stock)
(16, 10),  -- Patatas Deluxe (stock moderado)
(17, 6),   -- Patatas con Queso (stock bajo)
(18, 55),  -- Refresco Pequeño (muy buen stock)
(19, 48),  -- Refresco Mediano (muy buen stock)
(20, 40),  -- Refresco Grande (muy buen stock)
(21, 60),  -- Agua Mineral (muy buen stock)
(22, 30),  -- Cerveza (buen stock)
(23, 12),  -- Zumo Naranja (stock moderado)
(24, 15),  -- Helado de Vainilla (stock moderado)
(25, 3),   -- Brownie con Helado (stock crítico)
(26, 8),   -- Tarta de Queso (stock bajo)
(27, 11),  -- Sundae de Chocolate (stock moderado)
(28, 2),   -- Nuggets de Pollo (stock crítico)
(29, 9),   -- Aros de Cebolla (stock bajo)
(30, 7),   -- Ensalada César (stock bajo)
(31, 20),  -- Menú Hamburguesa Clásica (buen stock)
(32, 18),  -- Menú Hamburguesa con Queso (buen stock)
(33, 25),  -- Menú Infantil (buen stock)
(34, 7),   -- Combo Familiar (stock bajo)
(35, 0);   -- Desayuno Completo (sin stock, descontinuado) 