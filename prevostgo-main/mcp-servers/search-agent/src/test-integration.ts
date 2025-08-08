import axios from 'axios';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

async function testSearchFunctionality() {
  console.log('🧪 Testing PrevostGo Search MCP Server Integration\n');
  
  try {
    // Test 1: Check if backend is running
    console.log('1️⃣ Testing backend connectivity...');
    try {
      const healthCheck = await axios.get(`${API_BASE_URL}/api/inventory/summary`);
      console.log('✅ Backend is running\n');
    } catch (error) {
      console.error('❌ Backend is not accessible. Make sure it\'s running on', API_BASE_URL);
      process.exit(1);
    }
    
    // Test 2: Search with filters
    console.log('2️⃣ Testing search with filters...');
    const searchFilters = {
      price_min: 200000,
      price_max: 500000,
      year_min: 2020,
      models: ['H3-45'],
      page: 1,
      per_page: 5
    };
    
    const searchResponse = await axios.post(`${API_BASE_URL}/api/search/coaches`, searchFilters);
    console.log(`✅ Found ${searchResponse.data.total} coaches matching filters`);
    console.log(`   Showing ${searchResponse.data.coaches.length} on page 1\n`);
    
    // Test 3: Get coach details (if we have results)
    if (searchResponse.data.coaches.length > 0) {
      console.log('3️⃣ Testing coach details retrieval...');
      const coachId = searchResponse.data.coaches[0].id;
      const detailsResponse = await axios.get(`${API_BASE_URL}/api/inventory/coaches/${coachId}`);
      console.log(`✅ Retrieved details for: ${detailsResponse.data.title}\n`);
      
      // Test 4: Find similar coaches
      console.log('4️⃣ Testing similar coaches...');
      const similarResponse = await axios.post(`${API_BASE_URL}/api/search/similar/${coachId}?limit=3`);
      console.log(`✅ Found ${similarResponse.data.length} similar coaches\n`);
    }
    
    // Test 5: Get search suggestions
    console.log('5️⃣ Testing search suggestions...');
    const suggestionsResponse = await axios.get(`${API_BASE_URL}/api/search/suggestions?q=Marathon&field=converter`);
    console.log(`✅ Got ${suggestionsResponse.data.suggestions.length} suggestions\n`);
    
    // Test 6: Get facets
    console.log('6️⃣ Testing search facets...');
    const facetsResponse = await axios.get(`${API_BASE_URL}/api/search/facets`);
    const facets = facetsResponse.data;
    console.log('✅ Retrieved facets:');
    console.log(`   - ${Object.keys(facets.models || {}).length} models`);
    console.log(`   - ${Object.keys(facets.converters || {}).length} converters`);
    console.log(`   - ${Object.keys(facets.years || {}).length} years`);
    console.log(`   - ${Object.keys(facets.dealer_states || {}).length} states\n`);
    
    console.log('🎉 All tests passed! The MCP server should work correctly with Claude Desktop.');
    console.log('\n📝 Next steps:');
    console.log('1. Run: npm run build');
    console.log('2. Run: npm run setup-claude');
    console.log('3. Restart Claude Desktop');
    
  } catch (error) {
    console.error('❌ Test failed:', error instanceof Error ? error.message : 'Unknown error');
    if (axios.isAxiosError(error)) {
      console.error('Response:', error.response?.data);
    }
    process.exit(1);
  }
}

// Run the tests
testSearchFunctionality();
