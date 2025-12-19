🎯 Quiz Master – Web Application

Quiz Master is a role-based quiz management and quiz-taking web application built using Flask, Jinja2, and SQLite.
It allows Teachers to create and manage quiz content and Students to take quizzes and track their performance through dashboards and summary charts.

This project is developed based on a detailed Software Requirements Specification (SRS) and wireframes.

📌 Project Purpose

The purpose of Quiz Master is to provide:

A simple and efficient quiz creation platform for teachers.

An interactive quiz-taking system for students.

Role-based dashboards with performance tracking and summaries.

A lightweight, database-backed web application using Python technologies.

🚀 Features Overview
👤 User Roles

Admin

Teacher / Faculty / Question Setter

Student / User

Each role has access to specific features and pages.

🧑‍🏫 Teacher / Admin Features

Create, view, edit, and delete:

Subjects

Chapters

Quizzes

Questions

Schedule quizzes with date and duration

Manage quiz content using full CRUD operations

View summary charts and quiz statistics

Monitor user quiz attempts and scores

🧑‍🎓 Student / User Features

Register and log in securely

View upcoming available quizzes

Take timed quizzes with multiple-choice questions

Submit quizzes and receive scores automatically

View quiz history and past scores

Access summary charts of performance

🔐 Authentication & Security

User registration with:

Email (username)

Password

Full name

Qualification

Date of birth

Secure login and session management

Role-based access control

Password hashing (recommended)

🛠️ Technology Stack
Layer	Technology
Backend	Flask (Python)
Frontend	HTML, CSS, Jinja2
Database	SQLite
Charts	Chart.js / similar (optional)
Styling	CSS / Bootstrap (optional)
🗂️ Project Structure (Suggested)
quiz-master/
│
├── app.py
├── database.db
├── requirements.txt
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── subjects.html
│   ├── chapters.html
│   ├── quizzes.html
│   ├── questions.html
│   ├── start_quiz.html
│   ├── results.html
│   └── summary.html
│
├── static/
│   ├── css/
│   └── js/
│
└── README.md

🧩 Functional Highlights (Mapped to SRS)

FR-1 to FR-5 → User Registration & Authentication

FR-6 to FR-8 → Role-based Access Control

FR-9 to FR-17 → Content Management (Teacher)

FR-18 to FR-22 → Quiz Taking Logic

FR-23 to FR-25 → Results & Summary Charts

FR-26 to FR-28 → Navigation & UI Flow

🗃️ Database Design

Key tables:

Users

Subjects

Chapters

Quizzes

Questions

Quiz_Attempts

User_Answers

Supports:

Foreign key constraints

User role management

Quiz scheduling

Attempt tracking and scoring

🌐 Application Routes
Route	Description
/register	User registration
/login	User login
/logout	Logout
/dashboard	Role-based dashboard
/teacher/subjects	Manage subjects
/teacher/subjects/<id>/chapters	Manage chapters
/teacher/chapters/<id>/quizzes	Manage quizzes
/teacher/quizzes/<id>/questions	Manage questions
/quizzes	Available quizzes (user)
/quizzes/<id>/start	Start quiz
/quizzes/<id>/submit	Submit quiz
/results	Quiz history
/summary	Performance charts
🎨 UI & Wireframe Reference

The application UI is based on the provided Figma wireframe:
🔗 Quiz Master Wireframe
https://www.figma.com/proto/ubisvNl4mupJHwxQnCoEvc