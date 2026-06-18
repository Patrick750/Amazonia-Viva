import os

readme_path = '/home/patrickortiz/Documentos/Amazonia-Viva/README.md'
changelog_path = '/home/patrickortiz/Documentos/Amazonia-Viva/CHANGELOG.md'

with open(readme_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if line.startswith('## 📦 Historial de Versiones'):
        start_idx = i
    if start_idx != -1 and line.startswith('## 🚀 Instalación y Ejecución'):
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    changelog_content = "".join(lines[start_idx:end_idx])
    
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write("# Changelog\n\n")
        f.write(changelog_content)
        
    new_readme_lines = lines[:start_idx + 1] + ["\nVer [CHANGELOG.md](./CHANGELOG.md) para el historial completo.\n\n"] + lines[end_idx:]
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.writelines(new_readme_lines)
    print("Changelog extraído correctamente.")
else:
    print("No se encontraron las secciones de historial.")
