// Script de vérification de la connexion au backend
// À exécuter dans la console du navigateur (F12)

async function testBackendConnection() {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  console.log("🔍 Test de connexion au backend...");
  console.log(`📍 URL: ${API_BASE_URL}`);

  try {
    // Test 1: Endpoint de base
    console.log("\n1️⃣ Test endpoint /api/docs...");
    const docsResponse = await fetch(`${API_BASE_URL}/api/docs`, {
      method: "GET",
      credentials: "include",
    });
    console.log(`   Status: ${docsResponse.status} ${docsResponse.statusText}`);

    // Test 2: Endpoint de login (sans credentials)
    console.log("\n2️⃣ Test endpoint /api/auth/login...");
    const loginResponse = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ username: "test", password: "test" }),
    });
    console.log(`   Status: ${loginResponse.status} ${loginResponse.statusText}`);

    if (loginResponse.status === 401) {
      console.log("   ✅ Backend accessible (401 = normal pour identifiants incorrects)");
    } else {
      const data = await loginResponse.json();
      console.log("   Réponse:", data);
    }

    console.log("\n✅ Backend accessible !");
    return true;
  } catch (error) {
    console.error("\n❌ Erreur de connexion:", error);
    console.error("\n💡 Vérifications à faire:");
    console.error("   1. Le backend est-il démarré sur http://localhost:8000 ?");
    console.error("   2. Vérifiez les logs du backend");
    console.error("   3. Vérifiez la configuration CORS");
    return false;
  }
}

// Exécuter le test
testBackendConnection();
