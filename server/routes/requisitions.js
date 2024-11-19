import express from 'express';
import { 
  getRequisitions, 
  getRequisitionDetails, 
  createNewRequisition, 
  removeRequisition 
} from '../services/requisitions.js';

export const router = express.Router();

router.get('/', async (req, res) => {
  try {
    const requisitions = await getRequisitions();
    res.json(requisitions);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const details = await getRequisitionDetails(req.params.id);
    res.json(details);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const requisition = await createNewRequisition(req.body);
    res.json(requisition);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    await removeRequisition(req.params.id);
    res.status(204).send();
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});