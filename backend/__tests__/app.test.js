const request = require('supertest');
const app = require('../app');

describe('POST /api/chat', () => {
  it('responds with chatbot reply', async () => {
    const res = await request(app)
      .post('/api/chat')
      .send({ message: 'Hola' });

    expect(res.statusCode).toBe(200);
    expect(res.body).toEqual({ response: 'Recibí: Hola' });
  });
});
