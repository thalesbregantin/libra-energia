#!/bin/bash

echo "========================================"
echo "    LIBRA ENERGIA - ATIVAR AMBIENTE"
echo "========================================"
echo

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo
    echo "Execute primeiro: python setup_environment.py"
    echo
    exit 1
fi

# Ativar ambiente virtual
echo "🚀 Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se foi ativado
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Falha ao ativar ambiente virtual!"
    exit 1
fi

echo "✅ Ambiente virtual ativado!"
echo
echo "🐍 Python: $VIRTUAL_ENV"
echo "📦 Pip: $VIRTUAL_ENV/bin/pip"
echo
echo "🚀 Comandos disponíveis:"
echo
echo "• Executar sistema: python scripts/start.py"
echo "• Dashboard HTML: open src/dashboard_simples.html"
echo "• Dashboard React: cd app && npm run dev"
echo "• Instalar pacotes: pip install nome_do_pacote"
echo "• Desativar: deactivate"
echo
echo "💡 Para desativar o ambiente, digite: deactivate"
echo

# Manter terminal aberto
exec $SHELL
