import sys

with open('enhanced_server.py', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Corriger la ligne 709 (index 708)
if '            cursor.execute' in lines[708]:
    lines[708] = lines[708].replace('            cursor.execute', '        cursor.execute')

# Corriger la ligne 733 (index 732)
if '            conn.commit' in lines[732]:
    lines[732] = lines[732].replace('            conn.commit', '        conn.commit')

with open('enhanced_server.py', 'w', encoding='utf-8') as file:
    file.writelines(lines)

print('Fichier corrigé avec succès') 