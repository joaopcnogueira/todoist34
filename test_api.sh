#!/bin/bash

# Script de teste da API do Todoist
# Testa todos os endpoints principais da aplicação

echo "======================================"
echo "   TESTE DA API - TODOIST"
echo "======================================"
echo ""

API_URL="http://localhost:8000"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para printar resultados
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

# 1. Testar Health Check
echo -e "${BLUE}1. Testando Health Check...${NC}"
RESPONSE=$(curl -s "$API_URL/health")
if echo "$RESPONSE" | grep -q "healthy"; then
    print_result 0 "Health check OK"
else
    print_result 1 "Health check falhou"
fi
echo ""

# 2. Registrar novo usuário
echo -e "${BLUE}2. Registrando novo usuário...${NC}"
USERNAME="usuario_$(date +%s)"
EMAIL="$USERNAME@example.com"
PASSWORD="senha123456"

RESPONSE=$(curl -s -X POST "$API_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$USERNAME\", \"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

if echo "$RESPONSE" | grep -q "\"id\""; then
    print_result 0 "Usuário registrado: $USERNAME"
else
    print_result 1 "Falha ao registrar usuário"
    echo "$RESPONSE"
fi
echo ""

# 3. Fazer Login
echo -e "${BLUE}3. Fazendo login...${NC}"
RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    print_result 0 "Login realizado com sucesso"
else
    print_result 1 "Falha no login"
    echo "$RESPONSE"
    exit 1
fi
echo ""

# 4. Obter informações do usuário
echo -e "${BLUE}4. Obtendo informações do usuário...${NC}"
RESPONSE=$(curl -s -X GET "$API_URL/api/auth/me" \
    -H "Authorization: Bearer $TOKEN")

if echo "$RESPONSE" | grep -q "\"username\""; then
    print_result 0 "Dados do usuário obtidos"
else
    print_result 1 "Falha ao obter dados do usuário"
fi
echo ""

# 5. Criar tarefa
echo -e "${BLUE}5. Criando primeira tarefa...${NC}"
RESPONSE=$(curl -s -X POST "$API_URL/api/tasks" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"title": "Tarefa de Teste 1", "description": "Descrição da tarefa de teste"}')

TASK_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ ! -z "$TASK_ID" ]; then
    print_result 0 "Tarefa criada (ID: $TASK_ID)"
else
    print_result 1 "Falha ao criar tarefa"
fi
echo ""

# 6. Criar segunda tarefa
echo -e "${BLUE}6. Criando segunda tarefa...${NC}"
RESPONSE=$(curl -s -X POST "$API_URL/api/tasks" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"title": "Tarefa de Teste 2"}')

if echo "$RESPONSE" | grep -q "\"id\""; then
    print_result 0 "Segunda tarefa criada"
else
    print_result 1 "Falha ao criar segunda tarefa"
fi
echo ""

# 7. Listar tarefas
echo -e "${BLUE}7. Listando todas as tarefas...${NC}"
RESPONSE=$(curl -s -X GET "$API_URL/api/tasks" \
    -H "Authorization: Bearer $TOKEN")

TASK_COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)

if [ "$TASK_COUNT" -ge "2" ]; then
    print_result 0 "Tarefas listadas ($TASK_COUNT tarefas encontradas)"
else
    print_result 1 "Falha ao listar tarefas"
fi
echo ""

# 8. Atualizar tarefa
echo -e "${BLUE}8. Marcando tarefa como concluída...${NC}"
RESPONSE=$(curl -s -X PUT "$API_URL/api/tasks/$TASK_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"is_completed": true}')

if echo "$RESPONSE" | grep -q '"is_completed":true'; then
    print_result 0 "Tarefa marcada como concluída"
else
    print_result 1 "Falha ao atualizar tarefa"
fi
echo ""

# 9. Obter tarefa específica
echo -e "${BLUE}9. Obtendo tarefa específica...${NC}"
RESPONSE=$(curl -s -X GET "$API_URL/api/tasks/$TASK_ID" \
    -H "Authorization: Bearer $TOKEN")

if echo "$RESPONSE" | grep -q "\"id\":$TASK_ID"; then
    print_result 0 "Tarefa obtida com sucesso"
else
    print_result 1 "Falha ao obter tarefa"
fi
echo ""

# 10. Deletar tarefa
echo -e "${BLUE}10. Deletando tarefa...${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_URL/api/tasks/$TASK_ID" \
    -H "Authorization: Bearer $TOKEN")

if [ "$HTTP_CODE" = "204" ]; then
    print_result 0 "Tarefa deletada com sucesso"
else
    print_result 1 "Falha ao deletar tarefa (HTTP $HTTP_CODE)"
fi
echo ""

echo "======================================"
echo "   TESTES CONCLUÍDOS"
echo "======================================"
echo ""
echo "Acesse a aplicação em: http://localhost:8000"
echo ""
