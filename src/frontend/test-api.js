// Simple script to test the /api/users/:userId/outfits endpoint
// Run with: node test-api.js

// Replace with an actual user ID from your database
const TEST_USER_ID = "your-user-id-here";

const testOutfitsEndpoint = async () => {
  try {
    console.log(`Testing outfits endpoint for user ID: ${TEST_USER_ID}`);
    const response = await fetch(`http://localhost:5001/api/users/${TEST_USER_ID}/outfits`);
    
    console.log("Response status:", response.status);
    const text = await response.text();
    console.log("Raw response:", text);
    
    try {
      const data = JSON.parse(text);
      console.log("Parsed data:", data);
      
      if (data.success && data.outfits) {
        console.log(`Found ${data.outfits.length} outfits`);
        if (data.outfits.length > 0) {
          console.log("First outfit:", data.outfits[0]);
        }
      }
    } catch (error) {
      console.error("Failed to parse response as JSON:", error);
    }
  } catch (error) {
    console.error("Error making request:", error);
  }
};

// Run the test
testOutfitsEndpoint(); 