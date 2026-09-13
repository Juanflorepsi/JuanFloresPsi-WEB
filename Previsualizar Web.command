#!/bin/bash
# Doble clic para previsualizar la web localmente.
# Levanta un servidor local en el puerto 8080 y abre el navegador.

cd "$(dirname "$0")"

PORT=8080

echo "Iniciando servidor local en http://localhost:$PORT ..."
echo "(Deja esta ventana abierta mientras navegas la web. Ciérrala para detener el servidor.)"
echo

open "http://localhost:$PORT/"

python3 -m http.server "$PORT"
