-- ============================================================
-- seed.sql — Sample Data for Testing
-- Inserts 25 sample old graduation projects into the database
-- Run after schema.sql: mysql -u root -p similarity_checker < database/seed.sql
-- ============================================================

USE similarity_checker;

-- Insert sample old graduation projects (Computer Engineering focus)
INSERT INTO old_projects (title, description, department, year, keywords) VALUES

('Smart Home Automation System Using IoT',
 'A system that allows users to control home appliances remotely using a mobile application and IoT sensors. The system uses Arduino microcontrollers and ESP8266 WiFi modules to connect devices to the internet. Users can turn lights on or off, monitor temperature, and receive alerts through a Flutter mobile app connected to a Firebase backend.',
 'Computer Engineering', 2023, 'IoT, Arduino, smart home, mobile app, Firebase'),

('E-Commerce Website for Local Businesses',
 'A full-stack web application built with React and Node.js that enables small local businesses to create online stores. The platform includes product management, shopping cart, payment integration with PayPal, order tracking, and an admin dashboard. MySQL is used for data storage and JWT tokens for authentication.',
 'Computer Engineering', 2023, 'e-commerce, React, Node.js, web development, MySQL'),

('Student Attendance System Using Face Recognition',
 'An automated attendance tracking system that uses facial recognition to identify students in a classroom. The system uses OpenCV and DeepFace library in Python to detect and recognize faces from a webcam feed. Attendance records are stored in a MySQL database and teachers can view reports through a Flask web interface.',
 'Computer Engineering', 2022, 'face recognition, OpenCV, attendance, Python, Flask'),

('Hospital Management System',
 'A comprehensive web-based system for managing hospital operations including patient registration, doctor appointments, medical records, and billing. Built with PHP and MySQL, the system allows patients to book appointments online and doctors to manage their schedules. Reports can be exported as PDF files.',
 'Computer Engineering', 2022, 'hospital, management system, PHP, MySQL, appointments'),

('Online Learning Platform for University Students',
 'A web application similar to Moodle that allows professors to upload course materials, create quizzes, and track student progress. Students can watch video lectures, submit assignments, and communicate with instructors through a messaging system. Built with Django and PostgreSQL with a responsive Bootstrap frontend.',
 'Computer Engineering', 2023, 'e-learning, Django, education, online platform, quizzes'),

('Traffic Monitoring System Using Computer Vision',
 'A real-time traffic monitoring solution that analyzes video feeds from road cameras using YOLO object detection to count vehicles and estimate traffic density. The system generates hourly reports and can trigger alerts when traffic exceeds a threshold. Python and OpenCV are used for image processing.',
 'Computer Engineering', 2021, 'computer vision, YOLO, traffic, object detection, Python'),

('Mobile Banking Application',
 'A secure mobile banking app developed with Flutter that allows users to check balances, transfer money, pay bills, and view transaction history. The app uses AES encryption for data security and biometric authentication for login. The backend is built with Spring Boot and PostgreSQL.',
 'Computer Engineering', 2023, 'mobile app, banking, Flutter, security, biometric'),

('Inventory Management System for Warehouses',
 'A desktop application built with Python and Tkinter for managing warehouse inventory. The system tracks product quantities, generates reorder alerts when stock is low, and produces monthly inventory reports. A barcode scanner integration allows quick product lookup. SQLite is used for local data storage.',
 'Computer Engineering', 2021, 'inventory, warehouse, Python, barcode, management'),

('Social Media Platform for University Community',
 'A campus social network where students and faculty can share posts, join groups, and communicate through direct messages. Built with Vue.js frontend and Laravel backend, the platform includes a notification system and content moderation tools for administrators.',
 'Computer Engineering', 2022, 'social media, Vue.js, Laravel, community, campus'),

('Autonomous Robot Navigation System',
 'A mobile robot that can navigate indoor environments autonomously using ultrasonic sensors and a camera. The robot uses a Raspberry Pi for processing and implements a pathfinding algorithm to avoid obstacles. The robot can be monitored remotely through a web dashboard showing its camera feed and sensor data.',
 'Electrical Engineering', 2022, 'robot, navigation, Raspberry Pi, autonomous, sensors'),

('Smart Library Management System',
 'A web-based library system that manages book borrowing, returns, and reservations. The system sends automatic email reminders for due dates and overdue books. QR codes are used for quick book check-in and check-out. Built with Flask and MySQL with a clean Bootstrap interface.',
 'Computer Engineering', 2021, 'library, management, QR code, Flask, email notifications'),

('Real-Time Chat Application',
 'A real-time messaging application built with Node.js and Socket.io that supports private messages and group chat rooms. Features include message history, online status indicators, file sharing, and emoji support. The frontend uses React and messages are stored in MongoDB.',
 'Computer Engineering', 2023, 'chat, real-time, Socket.io, Node.js, React'),

('Power Grid Monitoring System',
 'A SCADA-style system for monitoring electrical power distribution networks. The system collects data from sensors at substations, displays real-time voltage and current readings on a dashboard, and triggers alarms for abnormal readings. Built with Python and a web dashboard using Chart.js for visualization.',
 'Electrical Engineering', 2022, 'power grid, SCADA, monitoring, electrical, sensors'),

('Graduation Project Evaluation Platform',
 'A web system for managing the graduation project evaluation process at universities. Faculty can submit evaluation scores, students can track their project status, and administrators can generate final grade reports. Built with ASP.NET and SQL Server.',
 'Computer Engineering', 2021, 'graduation project, evaluation, university, management'),

('Plagiarism Detection System for Academic Papers',
 'A system that checks submitted academic papers for plagiarism by comparing text against a database of known papers using cosine similarity and TF-IDF. The system highlights similar passages and provides a similarity percentage report. Built with Python and Flask.',
 'Computer Engineering', 2022, 'plagiarism, text similarity, TF-IDF, cosine similarity, academic'),

('Weather Forecasting Application',
 'A mobile application that provides weather forecasts using data from OpenWeatherMap API. The app displays current weather, 7-day forecasts, and weather maps. It uses GPS for automatic location detection and sends notifications for severe weather alerts. Built with React Native.',
 'Computer Engineering', 2023, 'weather, mobile app, API, forecast, React Native'),

('Online Examination System',
 'A secure web-based examination platform that allows instructors to create timed quizzes with multiple choice and essay questions. Anti-cheating measures include tab switching detection and randomized question order. Built with Angular frontend and Django REST API backend.',
 'Computer Engineering', 2022, 'online exam, quiz, Django, Angular, education'),

('Parking Management System',
 'An IoT-based smart parking system that uses sensors in each parking spot to detect occupancy. A mobile app shows real-time availability of parking spaces on a map. The system records parking duration and calculates fees automatically. Uses Raspberry Pi and a Flask API.',
 'Computer Engineering', 2021, 'parking, IoT, sensors, mobile app, smart city'),

('Supply Chain Management System',
 'A web application for tracking products through the supply chain from manufacturer to customer. The system tracks shipments in real-time, manages supplier relationships, and generates analytics reports. Built with React and Node.js with MongoDB for flexible data storage.',
 'Computer Engineering', 2023, 'supply chain, logistics, tracking, React, MongoDB'),

('Medical Image Analysis Using Deep Learning',
 'A deep learning system that analyzes X-ray images to detect signs of pneumonia using a Convolutional Neural Network trained on a labeled dataset. The model achieves 92% accuracy and is deployed as a web API where doctors can upload images and receive instant analysis results.',
 'Computer Engineering', 2023, 'deep learning, CNN, medical imaging, X-ray, TensorFlow'),

('University Bus Tracking System',
 'A real-time bus tracking application for university transportation. GPS devices on buses send location data to a server and students can see bus locations on a live map in the mobile app. Estimated arrival times are calculated automatically. Built with Flutter and Firebase.',
 'Computer Engineering', 2022, 'GPS tracking, bus, Flutter, Firebase, university'),

('Cybersecurity Vulnerability Scanner',
 'A network security tool that scans local networks for open ports, outdated software, and common vulnerabilities. The scanner generates detailed security reports with recommended fixes. Built with Python using the Nmap library and a Flask web interface for displaying results.',
 'Computer Engineering', 2022, 'cybersecurity, vulnerability, network scanner, Python, Nmap'),

('Food Ordering Application for Campus',
 'A mobile app that allows university students to order food from campus cafeterias with estimated preparation time. Features include menu browsing, order tracking, payment integration, and order history. Built with React Native and a Node.js backend.',
 'Computer Engineering', 2023, 'food ordering, mobile app, campus, React Native, delivery'),

('Digital Voting System',
 'A secure online voting system for student union elections. The system uses one-time tokens for authentication and blockchain-inspired hashing to ensure vote integrity. Results are displayed in real-time after voting closes. Built with Python Flask and MySQL.',
 'Computer Engineering', 2021, 'voting, security, blockchain, election, Flask'),

('AI Chatbot for University Help Desk',
 'An intelligent chatbot that answers common student questions about university services, registration, and schedules. The chatbot uses intent classification with a trained NLP model and falls back to human support for complex queries. Integrated into the university website using JavaScript.',
 'Computer Engineering', 2023, 'chatbot, NLP, AI, university, help desk');

-- NOTE: Admin user is NO longer seeded here
-- The first admin is created through the /admin/setup page
-- This ensures the university sets their own credentials
-- Visit localhost:5000 and you will be redirected to setup automatically

