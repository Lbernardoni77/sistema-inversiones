// Script para probar la comunicación entre frontend y backend
// Simula las llamadas que hace el frontend

const BACKEND_URL = 'https://sistema-inversiones.onrender.com';
const FRONTEND_URL = 'https://sistema-inversiones-frontend.onrender.com';

// Tickers para probar
const TICKERS = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'SANDUSDT'];

async function testBackendHealth() {
    console.log('🔍 Probando health check del backend...');
    try {
        const response = await fetch(`${BACKEND_URL}/healthz`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend saludable:', data);
            return true;
        } else {
            console.log('❌ Backend no responde:', response.status);
            return false;
        }
    } catch (error) {
        console.log('❌ Error conectando al backend:', error.message);
        return false;
    }
}

async function testPriceEndpoint(symbol) {
    console.log(`\n🔍 Probando precio para ${symbol}...`);
    try {
        const response = await fetch(`${BACKEND_URL}/binance/price/${symbol}?period=1d`);
        if (response.ok) {
            const data = await response.json();
            console.log(`✅ Precio obtenido: $${data.price} (${data.source})`);
            
            // Verificar formato del precio
            if (typeof data.price === 'number') {
                console.log(`✅ Precio es numérico: ${data.price}`);
                return true;
            } else if (typeof data.price === 'string') {
                console.log(`⚠️  Precio es string: ${data.price}`);
                // Intentar convertir
                const precioNumerico = parseFloat(data.price.replace(',', '.'));
                if (!isNaN(precioNumerico)) {
                    console.log(`✅ Conversión exitosa: ${precioNumerico}`);
                    return true;
                } else {
                    console.log(`❌ No se pudo convertir el precio`);
                    return false;
                }
            } else {
                console.log(`❌ Tipo de precio inesperado: ${typeof data.price}`);
                return false;
            }
        } else {
            console.log(`❌ Error obteniendo precio: ${response.status}`);
            return false;
        }
    } catch (error) {
        console.log(`❌ Error en precio: ${error.message}`);
        return false;
    }
}

async function testRecommendationEndpoint(symbol) {
    console.log(`\n🔍 Probando recomendación para ${symbol}...`);
    try {
        const response = await fetch(`${BACKEND_URL}/binance/recommendation/${symbol}?horizonte=24h`);
        if (response.ok) {
            const data = await response.json();
            console.log(`✅ Recomendación: ${data.recomendacion}`);
            
            // Verificar soportes y resistencias
            const detalle = data.detalle || {};
            const soportes = detalle.soportes || [];
            const resistencias = detalle.resistencias || [];
            console.log(`✅ Soportes: ${soportes.length}, Resistencias: ${resistencias.length}`);
            
            return true;
        } else {
            console.log(`❌ Error obteniendo recomendación: ${response.status}`);
            return false;
        }
    } catch (error) {
        console.log(`❌ Error en recomendación: ${error.message}`);
        return false;
    }
}

async function testFrontend() {
    console.log('\n🔍 Probando frontend...');
    try {
        const response = await fetch(FRONTEND_URL);
        if (response.ok) {
            console.log('✅ Frontend responde correctamente');
            return true;
        } else {
            console.log(`❌ Frontend no responde: ${response.status}`);
            return false;
        }
    } catch (error) {
        console.log('❌ Error conectando al frontend:', error.message);
        return false;
    }
}

async function main() {
    console.log('🚀 Probando Sistema de Inversiones');
    console.log('='.repeat(50));
    
    // Probar servicios
    const backendOk = await testBackendHealth();
    const frontendOk = await testFrontend();
    
    if (!backendOk || !frontendOk) {
        console.log('\n❌ Los servicios no están funcionando correctamente');
        return;
    }
    
    console.log('\n📊 Probando tickers...');
    console.log('='.repeat(50));
    
    const resultados = {};
    
    for (const ticker of TICKERS) {
        console.log(`\n🎯 ${ticker}`);
        console.log('-'.repeat(30));
        
        const precioOk = await testPriceEndpoint(ticker);
        const recomendacionOk = await testRecommendationEndpoint(ticker);
        
        resultados[ticker] = {
            precio: precioOk,
            recomendacion: recomendacionOk,
            total: precioOk && recomendacionOk
        };
        
        // Pausa entre requests
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    // Resumen
    console.log('\n' + '='.repeat(50));
    console.log('📋 RESUMEN DE RESULTADOS');
    console.log('='.repeat(50));
    
    let exitosos = 0;
    const total = TICKERS.length;
    
    for (const [ticker, resultado] of Object.entries(resultados)) {
        const status = resultado.total ? '✅' : '❌';
        console.log(`${status} ${ticker}: Precio=${resultado.precio}, Recomendación=${resultado.recomendacion}`);
        if (resultado.total) exitosos++;
    }
    
    console.log(`\n📊 Resultado final: ${exitosos}/${total} tickers funcionando correctamente`);
    
    if (exitosos === total) {
        console.log('🎉 ¡Todos los tickers están funcionando perfectamente!');
        console.log('💡 El frontend debería poder agregar tickers sin problemas');
    } else {
        console.log('⚠️  Algunos tickers tienen problemas');
        console.log('💡 Revisa los logs para más detalles');
    }
}

// Ejecutar el test
main().catch(console.error); 