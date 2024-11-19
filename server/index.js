import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { router as authRouter } from './routes/auth.js';
import { router as requisitionsRouter } from './routes/requisitions.js';
import { router as institutionsRouter } from './routes/institutions.js';
import { router as accountsRouter } from './routes/accounts.js';

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Routes
app.use('/api/auth', authRouter);
app.use('/api/requisitions', requisitionsRouter);
app.use('/api/institutions', institutionsRouter);
app.use('/api/accounts', accountsRouter);

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});