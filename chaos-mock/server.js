const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware to parse incoming JSON payloads
app.use(express.json());

// Root test endpoint
app.get('/', (req, res) => {
    res.json({
        status: 'success',
        message: 'Chaos mock server is online!'
    });
});

// Start listening for requests
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
