import express from 'express';
import { User } from './types/index';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware setup
app.use(express.json());

// Main application logic
app.get('/', (req, res) => {
    res.send('Welcome to the Luatsu Ki Show!');
});

// Example route using a type
app.post('/example', (req, res) => {
    const data: User = req.body;
    // Process data...
    res.status(201).send(data);
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});