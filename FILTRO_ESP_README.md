# Filtro por ESP no Dashboard

## 📋 Funcionalidades Implementadas

### 1. **Backend - Nova API**
- **`/api/esp-data?esp=<nome>`** - Retorna dados filtrados de uma ESP específica
  - Informações da ESP (ID, IP, datas)
  - Leituras por sensor (apenas desta ESP)
  - Últimas 50 leituras com todos os valores
  - Valores mais recentes de cada sensor

- **`/api/detailed-readings?esp=<nome>`** - Suporta filtro opcional por ESP
  - Retorna leituras detalhadas
  - Se parâmetro `esp` fornecido, filtra apenas aquela ESP

### 2. **Frontend - Dashboard Interativo**

#### Botões de Filtro
- Exibidos no card "Total de ESPs"
- Um botão para cada ESP registrada
- Mostra quantidade de leituras entre parênteses
- Exemplo: `ESP32_LAB_001 (45)`

#### Filtro Ativo
- Novo card "Filtro Ativo" substitui o card "Status"
- Mostra qual ESP está sendo visualizada
- Botão "🔄 Ver Todas" para limpar o filtro

#### Visualização Filtrada
Quando uma ESP é clicada:
- ✅ Estatísticas atualizadas (apenas desta ESP)
- ✅ Gráfico de sensores (apenas sensores desta ESP)
- ✅ Tabela de leituras detalhadas (apenas desta ESP)
- ✅ Valores recentes (apenas desta ESP)
- ✅ Gráficos de timeline (apenas dados desta ESP)
- ✅ Botão ativo destacado visualmente

## 🎨 Estilos Visuais

### Botões de ESP
```css
.esp-filter-btn - Botão padrão (azul claro)
.esp-filter-btn:hover - Efeito hover (azul escuro)
.esp-filter-btn.active - ESP selecionada (roxo)
```

### Estados
- **Todos os dados**: "Filtro Ativo" mostra "Todos"
- **Filtrado**: "Filtro Ativo" mostra nome da ESP
- **Botão limpar**: Aparece apenas quando filtro está ativo

## 🔄 Fluxo de Uso

1. **Dashboard carrega** → Mostra todos os dados de todas as ESPs
2. **Usuário clica em ESP** → `filterByESP('ESP32_DOOR')`
3. **Chamada API** → `GET /api/esp-data?esp=ESP32_DOOR`
4. **Dashboard atualiza** → Mostra apenas dados daquela ESP
5. **Botão "Ver Todas"** → `clearFilter()` → Volta ao estado inicial

## 📊 Exemplo de Dados Retornados

### `/api/esp-data?esp=ESP32_DOOR`
```json
{
  "ok": true,
  "data": {
    "esp_info": {
      "id": 2,
      "nome": "ESP32_DOOR",
      "ip": "192.168.1.100",
      "criado_em": "2025-11-19T10:30:00",
      "atualizado_em": "2025-11-19T15:45:00"
    },
    "leituras_por_sensor": [
      {"sensor": "encoder", "total_leituras": 125}
    ],
    "ultimas_leituras": [
      {
        "leitura_id": 450,
        "timestamp": "2025-11-19T15:45:00",
        "sensor": "encoder",
        "valores": [
          {"campo": "porta_aberta", "valor": 1},
          {"campo": "alerta", "valor": 0}
        ]
      }
    ],
    "valores_recentes": [
      {
        "sensor": "encoder",
        "campo": "porta_aberta",
        "valor": 1,
        "timestamp": "2025-11-19T15:45:00"
      }
    ]
  }
}
```

## 🚀 Como Testar

1. **Inicie o servidor API**:
   ```bash
   python API/Server.py
   ```

2. **Acesse o dashboard**:
   ```
   http://localhost:5000/dashboard
   ```

3. **Simule dados de múltiplas ESPs**:
   - Execute o sketch na ESP física
   - Ou use `python simular_esp32_door.py`

4. **Teste o filtro**:
   - Clique em qualquer botão de ESP no primeiro card
   - Observe os gráficos atualizarem
   - Clique em "Ver Todas" para voltar

## ✨ Melhorias Futuras

- [ ] Adicionar filtro por sensor também
- [ ] Persistir filtro selecionado no localStorage
- [ ] Adicionar comparação entre ESPs (múltipla seleção)
- [ ] Exportar dados filtrados para CSV/JSON
- [ ] Adicionar filtro por período de tempo
- [ ] Criar dashboard dedicado para cada ESP (rota separada)

## 🐛 Troubleshooting

### Botões não aparecem
- Verifique se há ESPs registradas no banco
- Confira console do navegador (F12)
- Verifique se `leituras_por_esp` não está vazio

### Filtro não funciona
- Confirme que `/api/esp-data` está respondendo
- Verifique se nome da ESP está correto (case-sensitive)
- Veja logs do servidor Python

### Gráficos não atualizam
- Limpe cache do navegador
- Force refresh (Ctrl+F5)
- Verifique erros no console JavaScript
