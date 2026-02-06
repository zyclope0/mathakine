#!/usr/bin/env python3
"""Script de vérification de la gestion auth et logout"""
import sys
from pathlib import Path

print("=== VERIFICATION AUTH & LOGOUT ===\n")

# 1. Vérifier le code de logout
print("[1/3] Verification du code de logout...")

logout_file = Path("server/views.py")
if logout_file.exists():
    content = logout_file.read_text(encoding='utf-8')
    
    # Chercher la fonction logout
    if "async def logout" in content:
        print("  ✓ Fonction logout trouvée")
        
        # Vérifier si elle gère correctement samesite et secure
        if 'samesite="none"' in content[content.find("async def logout"):content.find("async def logout")+500]:
            print("  ✓ Logout gère samesite='none'")
        else:
            print("  ✗ PROBLEME: Logout ne gère pas samesite='none' lors de delete_cookie")
            print("    → Les cookies cross-domain ne seront pas supprimés correctement")
    else:
        print("  ✗ Fonction logout non trouvée")
else:
    print("  ✗ Fichier server/views.py non trouvé")

print()

# 2. Vérifier le refresh token
print("[2/3] Verification du refresh token...")

if "async def api_refresh_token" in content:
    print("  ✓ Fonction refresh_token trouvée")
    refresh_section = content[content.find("async def api_refresh_token"):content.find("async def api_refresh_token")+2000]
    
    if "secure=True" in refresh_section:
        print("  ✓ Refresh token utilise secure=True")
    if 'samesite="none"' in refresh_section:
        print("  ✓ Refresh token utilise samesite='none'")
else:
    print("  ✗ Fonction refresh_token non trouvée")

print()

# 3. Vérifier les routes API
print("[3/3] Verification des routes API...")

routes_file = Path("server/routes.py")
if routes_file.exists():
    routes_content = routes_file.read_text(encoding='utf-8')
    
    if '"/api/auth/logout"' in routes_content or "'/api/auth/logout'" in routes_content:
        print("  ✓ Route POST /api/auth/logout existe")
    else:
        print("  ⚠ Route POST /api/auth/logout pourrait manquer")
        print("    → Vérifier que le frontend peut appeler cette route")
else:
    print("  ✗ Fichier server/routes.py non trouvé")

print("\n=== RESUME ===")
print("""
PROBLEMES IDENTIFIES:
1. La fonction logout doit spécifier samesite='none' et secure=True lors du delete_cookie
2. Vérifier que la route POST /api/auth/logout existe

SOLUTIONS:
- Corriger server/views.py fonction logout
- Vérifier server/routes.py pour la route logout
""")

