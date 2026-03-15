// vulnerable_app.js
// WARNING: This application intentionally contains vulnerabilities
// Use only for security learning or testing environments

const express = require("express");
const fs = require("fs");
const sqlite3 = require("sqlite3").verbose();
const bodyParser = require("body-parser");
const { exec } = require("child_process");

const app = express();
const PORT = 3000;

// Hardcoded secret (bad practice)
const ADMIN_PASSWORD = "admin123";

// Database setup
const db = new sqlite3.Database(":memory:");

db.serialize(() => {
    db.run("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)");
    db.run("CREATE TABLE notes (id INTEGER PRIMARY KEY, username TEXT, note TEXT)");

    db.run(`INSERT INTO users (username,password) VALUES ('admin','${ADMIN_PASSWORD}')`);
});

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Basic homepage
app.get("/", (req, res) => {
    res.send(`
        <h1>Welcome to Vulnerable Notes App</h1>
        <form action="/login" method="POST">
        Username:<input name="username"><br>
        Password:<input name="password" type="password"><br>
        <button type="submit">Login</button>
        </form>
    `);
});

// Login route (SQL Injection vulnerability)
app.post("/login", (req, res) => {
    const username = req.body.username;
    const password = req.body.password;

    const query = `SELECT * FROM users WHERE username='${username}' AND password='${password}'`;

    db.get(query, (err, row) => {
        if (row) {
            res.send("Login successful! <a href='/notes?user=" + username + "'>View Notes</a>");
        } else {
            res.send("Login failed");
        }
    });
});

// Add note
app.post("/addNote", (req, res) => {
    const username = req.body.username;
    const note = req.body.note;

    const query = `INSERT INTO notes(username,note) VALUES('${username}','${note}')`;

    db.run(query);

    res.send("Note added");
});

// View notes (XSS vulnerability)
app.get("/notes", (req, res) => {
    const user = req.query.user;

    const query = `SELECT note FROM notes WHERE username='${user}'`;

    db.all(query, (err, rows) => {
        let output = "<h2>Your Notes</h2>";

        rows.forEach(r => {
            output += "<div>" + r.note + "</div>"; // no sanitization
        });

        res.send(output + `
            <form action="/addNote" method="POST">
            <input type="hidden" name="username" value="${user}">
            <input name="note">
            <button>Add</button>
            </form>
        `);
    });
});

// File read endpoint (Path Traversal vulnerability)
app.get("/readFile", (req, res) => {
    const file = req.query.file;

    fs.readFile("./files/" + file, "utf8", (err, data) => {
        if (err) {
            res.send("Error reading file");
        } else {
            res.send("<pre>" + data + "</pre>");
        }
    });
});

// Run system command (Command Injection)
app.get("/ping", (req, res) => {
    const host = req.query.host;

    exec("ping -c 1 " + host, (err, stdout, stderr) => {
        res.send("<pre>" + stdout + "</pre>");
    });
});

// Debug endpoint exposing secrets
app.get("/debug", (req, res) => {
    res.json({
        adminPassword: ADMIN_PASSWORD,
        environment: process.env
    });
});

// No authentication check
app.get("/admin", (req, res) => {
    res.send("Welcome admin. Sensitive dashboard here.");
});

// Logging sensitive information
app.post("/register", (req, res) => {
    const username = req.body.username;
    const password = req.body.password;

    console.log("Registering user:", username, password); // sensitive logging

    db.run(`INSERT INTO users(username,password) VALUES('${username}','${password}')`);

    res.send("User registered");
});

// Server start
app.listen(PORT, () => {
    console.log("Vulnerable app running on port " + PORT);
});
