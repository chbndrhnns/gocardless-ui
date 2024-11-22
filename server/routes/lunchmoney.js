import express from 'express';
import { getAssets, linkAccounts, unlinkAccounts } from '../services/lunchmoney.js';

export const router = express.Router();

router.get('/assets', async (req, res) => {
  try {
    const assets = await getAssets();
    res.json({ assets });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/link', async (req, res) => {
  try {
    const { lunchmoneyId, gocardlessId } = req.body;
    await linkAccounts(lunchmoneyId, gocardlessId);
    res.status(200).json({ message: 'Accounts linked successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/unlink', async (req, res) => {
  try {
    const { lunchmoneyId } = req.body;
    await unlinkAccounts(lunchmoneyId);
    res.status(200).json({ message: 'Account unlinked successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});