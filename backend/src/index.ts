// CRITICAL: Load .env BEFORE any other imports that might use process.env
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { existsSync, readFileSync } from 'node:fs';

console.log('=== DEBUGGING .ENV LOADING ===');
console.log('Current working directory (process.cwd()):', process.cwd());
console.log('__filename (import.meta.url):', import.meta.url);

// Load .env file from the backend directory
// Get the directory of this file (src/)
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
console.log('__dirname (this file location):', __dirname);

// Go up two levels: src/ -> backend/
const backendDir = resolve(__dirname, '..', '..');
const envPath = resolve(backendDir, '.env');
console.log('Calculated backend directory:', backendDir);
console.log('Calculated .env path:', envPath);
console.log('.env file exists?', existsSync(envPath));

// Try multiple paths
const pathsToTry = [
  envPath, // Calculated path
  resolve(process.cwd(), '.env'), // Current working directory
  resolve(process.cwd(), 'backend', '.env'), // If running from root
];

console.log('\n=== TRYING PATHS ===');
let loaded = false;
for (const path of pathsToTry) {
  console.log(`Trying: ${path}`);
  console.log(`  Exists: ${existsSync(path)}`);
  if (existsSync(path)) {
    try {
      const content = readFileSync(path, 'utf-8');
      console.log(`  File content preview: ${content.substring(0, 100)}...`);
      const result = dotenv.config({ path: path });
      if (result.error) {
        console.error(`  Error loading:`, result.error);
      } else {
        console.log(`  ✓ Successfully loaded from: ${path}`);
        loaded = true;
        break;
      }
    } catch (err) {
      console.error(`  Error reading file:`, err);
    }
  }
}

if (!loaded) {
  console.log('\n⚠ No .env file found, trying default dotenv.config()');
  dotenv.config();
}

console.log('\n=== ENVIRONMENT VARIABLES ===');
console.log('MONGODB_URI:', process.env.MONGODB_URI ? `✓ Loaded (${process.env.MONGODB_URI.substring(0, 50)}...)` : '✗ Not found');
console.log('JWT_SECRET:', process.env.JWT_SECRET ? '✓ Loaded' : '✗ Not found');
console.log('EVALUATOR_SERVICE_URL:', process.env.EVALUATOR_SERVICE_URL || 'Not found');
console.log('PORT:', process.env.PORT || 'Not found (using default 5000)');
console.log('All env vars:', Object.keys(process.env).filter(k => k.includes('MONGO') || k.includes('JWT') || k.includes('EVAL')));

if (!process.env.MONGODB_URI) {
  console.error('\n❌ ERROR: MONGODB_URI is required but not found in .env file');
  console.error('Please check that the .env file exists in the backend directory');
  process.exit(1);
}
console.log('=== END DEBUG ===\n');

// NOW import other modules after .env is loaded
import express from 'express';
import cors from 'cors';
import { connectDB } from './lib/db';
import authRoutes from './server/routes/auth';
import interviewRoutes from './server/routes/interviews';
import interviewResultsRoutes from './server/routes/interviewResults';

const app = express();
const PORT = process.env.PORT || 5000;

// Connect to MongoDB
connectDB();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/interviews', interviewRoutes);
app.use('/api/interview-results', interviewResultsRoutes);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Server is running' });
});

// 404 handler for API routes
app.use('/api/*', (req, res) => {
  res.status(404).json({ message: 'API endpoint not found' });
});

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ message: 'Something went wrong!', error: err.message });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
}); 