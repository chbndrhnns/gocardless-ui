import express from 'express';
import { getAccessToken } from '../services/auth.js';

export const router = express.Router();

router.post('/token', async (req, res) => {
  try {
    const token = await getAccessToken();
    res.json(token);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});