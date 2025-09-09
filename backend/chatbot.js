function getResponse(message) {
  if (!message) {
    return 'No entendí tu mensaje.';
  }
  return `Recibí: ${message}`;
}

module.exports = { getResponse };
