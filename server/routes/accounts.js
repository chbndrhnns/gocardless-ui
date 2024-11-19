import express from 'express';
import { getAccountDetails } from '../services/accounts.js';

export const router = express.Router();

router.get('/:id', async (req, res) => {
  try {
    const account = await getAccountDetails(req.params.id);
    res.json(account);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});