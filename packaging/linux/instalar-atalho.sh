#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ICON_DIR="${HOME}/.local/share/icons/hicolor/512x512/apps"
APPS_DIR="${HOME}/.local/share/applications"

mkdir -p "${ICON_DIR}" "${APPS_DIR}"
cp "${APP_DIR}/logo.png" "${ICON_DIR}/docentia.png"

cat > "${APPS_DIR}/docentia.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Docentia
Comment=Revisao academica de TCC e validacao ABNT
Exec="${APP_DIR}/Docentia"
Icon=docentia
Terminal=false
Categories=Education;Office;
EOF

chmod +x "${APP_DIR}/Docentia" "${APPS_DIR}/docentia.desktop"
echo "Atalho do Docentia instalado em ${APPS_DIR}/docentia.desktop"
