-- INSERT usuario. Es igual para estudiantes y profesores (a excepción de la columna type)
INSERT INTO usuario (email, contrasena, nombres, apellido, nro_documento, firebase_uid, created_at, type)
VALUES
('ingresante1@fce.uncu.edu.ar','$2b$12$stwQ68UL63DdWwjowE.sz.NLiwy/eaROOjcCNPoONKJFKFbcrMGm2', 'Estudiante', 'Ingreso', 47000000, 'LvxqMHuEpHbArCSeqgOBeZPFTBw2', NOW(), 'estudiante'),
('ingresante2@fce.uncu.edu.ar','$2b$12$stwQ68UL63DdWwjowE.sz.NLiwy/eaROOjcCNPoONKJFKFbcrMGm2', 'Estudiante', 'Ingreso', 47000000, 'yks9QgSlt4ayfg13zeDiKjhPNGz1', NOW(), 'estudiante'),
('ingresante3@fce.uncu.edu.ar','$2b$12$stwQ68UL63DdWwjowE.sz.NLiwy/eaROOjcCNPoONKJFKFbcrMGm2', 'Estudiante', 'Ingreso', 47000000, 'HKQyg5pR6JQhAwnvGWJT0UQdzuI3', NOW(), 'estudiante'),
('ingresante4@fce.uncu.edu.ar','$2b$12$stwQ68UL63DdWwjowE.sz.NLiwy/eaROOjcCNPoONKJFKFbcrMGm2', 'Estudiante', 'Ingreso', 47000000, 'RDugd58vbdWd5xW9QG3TCQNHMPQ2', NOW(), 'estudiante'),
('ingresante5@fce.uncu.edu.ar','$2b$12$stwQ68UL63DdWwjowE.sz.NLiwy/eaROOjcCNPoONKJFKFbcrMGm2', 'Estudiante', 'Ingreso', 47000000, 'L0OEdtApLJhMBTM7xIdmi8nrD8T2', NOW(), 'estudiante'),
('profesorsdc@itu.uncu.edu.ar','$2b$12$muyq6MOiMz4I9DbHYLaa.eqLjzwWivuoAzMFeQOcdsb4b8.9SoD4K', 'Guillermo', 'Sandez', 20000000, 'hR3GZr7zM8aoOj284yyEQkkHpKQ2', NOW(), 'profesor'),

INSERT INTO usuario (email, contrasena, nombres, apellido, nro_documento, firebase_uid, created_at, type)
VALUES
('profesorsdc@itu.uncu.edu.ar','$2b$12$muyq6MOiMz4I9DbHYLaa.eqLjzwWivuoAzMFeQOcdsb4b8.9SoD4K', 'Guillermo', 'Sandez', 20000000, 'hR3GZr7zM8aoOj284yyEQkkHpKQ2', NOW(), 'profesor'),

-- INSERT estudiantes
INSERT INTO estudiante (estudiante_id, mensajes_enviados, tiempo_interaccion)
VALUES
(8, 0, '0:00:00'),
(9, 0, '0:00:00'),
(10, 0, '0:00:00'),
(11, 0, '0:00:00'),
(12, 0, '0:00:00'),
(13, 0, '0:00:00'),
(14, 0, '0:00:00'),
(15, 0, '0:00:00'),
(16, 0, '0:00:00'),
(17, 0, '0:00:00'),
(18, 0, '0:00:00'),
(19, 0, '0:00:00'),
(20, 0, '0:00:00'),
(21, 0, '0:00:00'),
(22, 0, '0:00:00'),
(23, 0, '0:00:00'),
(24, 0, '0:00:00'),
(25, 0, '0:00:00'),
(26, 0, '0:00:00'),
(27, 0, '0:00:00'),
(28, 0, '0:00:00'),
(29, 0, '0:00:00'),
(30, 0, '0:00:00'),
(31, 0, '0:00:00'),
(32, 0, '0:00:00'),
(33, 0, '0:00:00'),
(34, 0, '0:00:00'),
(35, 0, '0:00:00'),
(36, 0, '0:00:00'),
(37, 0, '0:00:00'),
(38, 0, '0:00:00'),
(39, 0, '0:00:00'),
(40, 0, '0:00:00'),
(41, 0, '0:00:00'),
(42, 0, '0:00:00'),
(43, 0, '0:00:00'),
(44, 0, '0:00:00'),
(45, 0, '0:00:00');

-- INSERT materia
INSERT INTO materia (materia_id, nombre)
VALUES (2, 'Matemática - Ingreso');

-- INSERT profesor
INSERT INTO profesor (profesor_id, materia_id)
VALUES (2, 1)

-- INSERT de asistentes
INSERT INTO asistente (asistente_id, nombre, instructions, materia_id)
VALUES ('asst_LMnzwqHscAlIEBRRrWzB6myW', 'Tutor de Matemática V1', '-', 1);

-- INSERT relaciones entre alumno y asistente de Matemática I
INSERT INTO alumno_asistente (id, asistente_id)
VALUES
(17, 'asst_3KJfRBTDM0hNa6IQAgc9t818'),
(18, 'asst_3KJfRBTDM0hNa6IQAgc9t818'),
(19, 'asst_3KJfRBTDM0hNa6IQAgc9t818'),
(20, 'asst_3KJfRBTDM0hNa6IQAgc9t818'),
(21, 'asst_3KJfRBTDM0hNa6IQAgc9t818');

-- INSERT para tabla unidad
-- Matemática I
INSERT INTO unidad (unidad_id, nombre, materia_id)
VALUES (1, 'Lógica y Conjuntos', 1);
INSERT INTO unidad (unidad_id, nombre, materia_id)
VALUES (2, 'Vectores. Rectas y Planos', 1);
INSERT INTO unidad (unidad_id, nombre, materia_id)
VALUES (3, 'Matrices y Determinantes. Aplicaciones', 1);
INSERT INTO unidad (unidad_id, nombre, materia_id)
VALUES (4, 'Sistemas de Ecuaciones Lineales (SEL). Aplicaciones', 1);
INSERT INTO unidad (unidad_id, nombre, materia_id)
VALUES (5, 'Subespacios de Vectores de Rn. Aplicaciones a Matrices y Sistemas', 1);

-- Matemática - Ingreso
INSERT INTO unidad (unidad_id, nombre, materia_id)
VALUES 
(6, 'Unidad 1: Los números', 2);
(7, 'Unidad 2: Razones y proporciones. Porcentajes.', 2);
(8, 'Unidad 3: Expresiones algebraicas, polinomios y factorización', 2);
(9, 'Unidad 4: Geometría y trigonometría', 2);
(10, 'Unidad 5: Ecuaciones e inecuaciones', 2);
(11, 'Unidad 6: Funciones', 2);


-- INSERT para tabla tema
-- Matemática I
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (1, 'Proposición', 1);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (2, 'Operaciones lógicas', 1);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (3, 'Leyes lógicas', 1);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (4, 'Relaciones lógicas', 1);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (5, 'Predicados', 1);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (6, 'Cuantificadores', 1);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (7, 'Proposiciones universales', 1);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (8, 'Métodos de demostración', 1);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (9, 'Refutación', 1);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (10, 'Nociones básicas de la teoría de conjuntos', 1);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (11, 'Conjuntos numéricos', 1);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (12, 'Relación y función: nociones básicas', 1);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (13, 'Vectores en el espacio bidimensional, tridimensional y n-dimensional', 2);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (14, 'Operaciones con vectores', 2);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (15, 'Producto punto', 2);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (16, 'Longitud y ángulo entre vectores', 2);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (17, 'Propiedades de los vectores', 2);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (18, 'Rectas y planos en el espacio tridimensional', 2);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (19, 'Clasificación de matrices', 3);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (20, 'Operaciones y propiedades con matrices', 3);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (21, 'Rango', 3);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (22, 'Matriz inversa y propiedades', 3);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (23, 'Matrices elementales', 3);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (24, 'Cálculo de la inversa', 3);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (25, 'Determinantes y propiedades', 3);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (26, 'Aplicaciones', 3);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (27, 'Clasificación de los SEL', 4);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (28, 'Métodos de resolución de SEL: matricial', 4);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (29, 'Métodos de resolución de SEL: eliminación de Gauss', 4);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (30, 'Métodos de resolución de SEL: Gauss–Jordan', 4);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (31, 'SEL homogéneos', 4);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (32, 'Propiedades de los SEL', 4);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (33, 'Aplicaciones', 4);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (34, 'Subespacios', 5);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (35, 'Espacio generado y conjunto generador', 5);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (36, 'Dependencia e independencia lineal', 5);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (37, 'Propiedades de los subespacios', 5);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (38, 'Base', 5);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (39, 'Dimensión', 5);
INSERT INTO tema (tema_id, nombre, unidad_id)
VALUES (40, 'Aplicación a matrices y sistemas de ecuaciones lineales', 5);

-- Matemática - Ingreso
INSERT INTO tema (tema_id, nombre, unidad_id) VALUES
(41, 'Números naturales', 6),
(42, 'Propiedades', 6),
(43, 'Múltiplos y divisores', 6),
(44, 'Números primos y compuestos', 6),
(45, 'Descomposición en factores primos', 6),
(46, 'MCM y MCD', 6),
(47, 'Números enteros', 6),
(48, 'Operaciones', 6),
(49, 'Números racionales', 6),
(50, 'Amplificación y simplificación', 6),
(51, 'Expresiones fraccionarias y decimales', 6),
(52, 'Números irracionales', 6),
(53, 'Números reales', 6),
(54, 'Aproximación', 6),
(55, 'Intervalos reales', 6),
(56, 'Valor absoluto o módulo', 6),
(57, 'Unión e intersección de conjuntos', 6),
(58, 'Potenciación', 6),
(59, 'Radicación', 6),
(60, 'Logaritmos', 6),
(61, 'Razón aritmética', 7),
(62, 'Razón geométrica', 7),
(63, 'Teorema Fundamental de las Proporciones', 7),
(64, 'Series de razones', 7),
(65, 'Proporcionalidad directa e inversa', 7),
(66, 'Regla de tres simple', 7),
(67, 'Regla de tres compuesta', 7),
(68, 'Sistema Métrico Legal Argentino', 7),
(69, 'Longitud, masa, capacidad, superficie, volumen', 7),
(70, 'Porcentaje (%) y tanto por mil (‰)', 7),
(71, 'Expresiones algebraicas', 8),
(72, 'Polinomios', 8),
(73, 'Valor numérico', 8),
(74, 'Raíces', 8),
(75, 'Casos de factorización', 8),
(76, 'Expresiones algebraicas racionales', 8),
(77, 'Puntos y rectas', 9),
(78, 'Ángulos', 9),
(79, 'Sistemas de medición de ángulos', 9),
(80, 'Triángulos', 9),
(81, 'Teorema de Pitágoras', 9),
(82, 'Razones trigonométricas', 9),
(83, 'Perímetros y áreas', 9),
(84, 'Volumen de cuerpos geométricos', 9),
(85, 'Ecuaciones de primer grado', 10),
(86, 'Ecuaciones de segundo grado', 10),
(87, 'Ecuaciones exponenciales', 10),
(88, 'Ecuaciones logarítmicas', 10),
(89, 'Inecuaciones de primer grado', 10),
(90, 'Sistemas de dos ecuaciones lineales', 10),
(91, 'Funciones', 11),
(92, 'Dominio e imagen', 11),
(93, 'Funciones polinómicas', 11),
(94, 'Funciones racionales', 11),
(95, 'Funciones exponenciales', 11),
(96, 'Funciones logarítmicas', 11),
(97, 'Funciones trigonométricas', 11);

-- INSERT asistente de Matemática - Ingreso
INSERT INTO asistente(asistente_id, nombre, instructions, materia_id)
VALUES ('asst_3KJfRBTDM0hNa6IQAgc9t818', 'Tutor Virtual de Matemática - Ingreso', '', 2);