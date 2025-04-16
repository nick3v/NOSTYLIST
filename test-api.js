// Test script to verify API connectivity
import fetch from 'node-fetch';

async function testAPI() {
  try {
    console.log('Testing API connection...');
    const response = await fetch('http://localhost:5001/api/test');
    
    if (!response.ok) {
      console.error(`API responded with status: ${response.status}`);
      return;
    }
    
    const data = await response.json();
    console.log('API test successful!', data);
  } catch (error) {
    console.error('Error connecting to API:', error.message);
  }
}

testAPI(); 