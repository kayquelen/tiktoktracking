#!/bin/bash

echo "🔧 Fazendo commit da correção SQLite..."

git add .
git commit -m "Correção SQLite: usar memória como fallback"
git push origin main

echo "✅ Commit realizado! EasyPanel vai fazer redeploy automaticamente."
