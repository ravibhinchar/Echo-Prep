import mongoose from 'mongoose';

// Don't check MONGODB_URI at module load time - check it when connectDB is called
// This allows .env to be loaded first in index.ts

export const connectDB = async () => {
  const MONGODB_URI = process.env.MONGODB_URI;
  
  if (!MONGODB_URI) {
    console.error('❌ MONGODB_URI is not defined in .env file');
    console.error('Current env vars:', Object.keys(process.env).filter(k => k.includes('MONGO')));
    process.exit(1);
  }

  try {
    console.log('Attempting to connect to MongoDB...');
    console.log('Connection string (masked):', MONGODB_URI.replace(/:[^:@]+@/, ':****@'));
    
    await mongoose.connect(MONGODB_URI);
    console.log('✓ MongoDB connected successfully');
  } catch (error: any) {
    console.error('❌ MongoDB connection error:', error.message);
    if (error.code === 8000 || error.message.includes('authentication failed')) {
      console.error('\n⚠️  Authentication failed. Please verify:');
      console.error('   1. Go to MongoDB Atlas: https://cloud.mongodb.com');
      console.error('   2. Check Database Access - verify username: 221107_db_user');
      console.error('   3. Reset password if needed or verify password: ayush83028');
      console.error('   4. Check Network Access - ensure your IP is whitelisted (or use 0.0.0.0/0 for dev)');
      console.error('   5. Verify the connection string in your .env file matches Atlas');
    }
    console.error('\n💡 Tip: You can get a new connection string from MongoDB Atlas:');
    console.error('   Connect > Connect your application > Copy connection string');
    process.exit(1);
  }
};

export default connectDB; 