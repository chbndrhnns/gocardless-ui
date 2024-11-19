import express from 'express';
import { getInstitutions } from '../services/institutions.js';

export const router = express.Router();

router.get('/', async (req, res) => {
  try {
    const institutions = await getInstitutions(req.query.country);
    res.json(institutions);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});