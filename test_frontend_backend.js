// Script de prueba para verificar la comunicación frontend-backend
const API_BASE_URL = 'https://sistema-inversiones.onrender.com';

async function testBackend() {
    console.log('🧪 Probando backend...');
    
    try {
        // Test 1: Health check
        const healthResponse = await fetch(`${API_BASE_URL}/healthz`);
        const healthData = await healthResponse.json();
        console.log('✅ Health check:', healthData);
        
        // Test 2: Get price
        const priceResponse = await fetch(`${API_BASE_URL}/binance/price/BTCUSDT`);
        const priceData = await priceResponse.json();
        console.log('✅ Price data:', priceData);
        
        // Test 3: Get recommendation
        const recResponse = await fetch(`${API_BASE_URL}/binance/recommendation/BTCUSDT?horizonte=24h`);
        const recData = await recResponse.json();
        console.log('✅ Recommendation data:', recData);
        
        // Test 4: Add ticker to backend
        const addResponse = await fetch(`${API_BASE_URL}/tickers/add?symbol=BTCUSDT`, {
            method: 'POST'
        });
        const addData = await addResponse.json();
        console.log('✅ Add ticker response:', addData);
        
        return {
            success: true,
            price: priceData,
            recommendation: recData,
            addTicker: addData
        };
        
    } catch (error) {
        console.error('❌ Error testing backend:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

// Ejecutar la prueba
testBackend().then(result => {
    console.log('🎯 Resultado final:', result);
}); 