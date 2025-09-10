const express = require('express');
const cors = require('cors');
const chatbot = require('./chatbot');
const app = express();
app.use(cors());
app.use(express.json());

app.post('/api/chat', (req, res) => {
    const { message } = req.body;
    const response = chatbot.getResponse(message);
    res.json({ response });
});

if (require.main === module) {
    app.listen(3001, () => console.log('Servidor en http://localhost:3001'));
}

module.exports = app;
