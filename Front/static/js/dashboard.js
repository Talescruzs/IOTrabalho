// ============================================================================
// Dashboard IoT - JavaScript
// ============================================================================

// Força execução imediata ao carregar o script
console.log('🚀 Dashboard JavaScript iniciado!');

let chartEsps, chartSensores;
let timelineCharts = {}; // Armazena múltiplos gráficos de timeline
const API_BASE = 'http://localhost:5000';  // API separada da porta 5000
let currentESP = null; // ESP atualmente filtrada

// Configurações padrão dos gráficos
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.color = '#666';

// Teste imediato se os containers existem
console.log('📍 Verificando containers...');
setTimeout(() => {
    const containers = {
        'readingsTableContainer': document.getElementById('readingsTableContainer'),
        'valoresRecentesContainer': document.getElementById('valoresRecentesContainer'),
        'chartTimeline': document.getElementById('chartTimeline')
    };
    console.log('📦 Containers encontrados:', containers);
}, 100);

// ============================================================================
// FUNÇÕES DE FILTRO POR ESP
// ============================================================================

function filterByESP(espName) {
    console.log(`🔍 Filtrando por ESP: ${espName}`);
    currentESP = espName;
    
    // Salva no localStorage para persistir entre reloads
    localStorage.setItem('dashboard_filter_esp', espName);
    
    // Atualiza UI do filtro
    document.getElementById('currentFilter').textContent = espName;
    document.getElementById('statusDetail').textContent = `Visualizando apenas ${espName}`;
    document.getElementById('clearFilterBtn').style.display = 'block';
    
    // Destaca o botão ativo
    document.querySelectorAll('.esp-filter-btn').forEach(btn => {
        if (btn.textContent.includes(espName)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Recarrega dados filtrados
    loadESPData(espName);
}

function clearFilter() {
    console.log('🔄 Removendo filtro, mostrando todas as ESPs');
    currentESP = null;
    
    // Remove do localStorage
    localStorage.removeItem('dashboard_filter_esp');
    
    // Atualiza UI do filtro
    document.getElementById('currentFilter').textContent = 'Todos';
    document.getElementById('statusDetail').textContent = 'Visualizando todas as ESPs';
    document.getElementById('clearFilterBtn').style.display = 'none';
    
    // Remove destaque dos botões
    document.querySelectorAll('.esp-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Recarrega todos os dados
    loadAllData();
}

async function loadESPData(espName) {
    const btn = document.querySelector('.refresh-btn');
    btn.disabled = true;
    btn.textContent = '⏳ Carregando...';

    try {
        const response = await fetch(`${API_BASE}/api/esp-data?esp=${encodeURIComponent(espName)}`);
        const result = await response.json();

        if (result.ok) {
            console.log(`📦 Dados da ESP ${espName}:`, result.data);
            
            // Atualiza estatísticas (apenas desta ESP)
            updateStatsFiltered(result.data);
            
            // Atualiza gráfico de sensores (apenas desta ESP)
            updateChartSensores(result.data.leituras_por_sensor);
            
            // Atualiza timeline com dados desta ESP
            updateTimelineFiltered(result.data.ultimas_leituras);
            
            // Atualiza valores recentes
            updateValoresRecentesFiltered(result.data.valores_recentes);
            
            // Atualiza tabela de leituras detalhadas
            updateDetailedReadingsFiltered(result.data.ultimas_leituras);
            
            // Atualiza UI do filtro (caso tenha sido restaurado)
            document.getElementById('currentFilter').textContent = espName;
            document.getElementById('statusDetail').textContent = `Visualizando apenas ${espName}`;
            document.getElementById('clearFilterBtn').style.display = 'block';
            
            document.getElementById('lastUpdate').textContent = 
                `Última atualização: ${new Date().toLocaleTimeString('pt-BR')} (filtrado: ${espName})`;
        } else {
            alert(`Erro ao carregar dados da ESP: ${result.error}`);
            clearFilter();
        }
    } catch (error) {
        console.error('Erro ao carregar dados da ESP:', error);
        alert('Erro ao conectar com a API');
        clearFilter();
    } finally {
        btn.disabled = false;
        btn.textContent = '🔄 Atualizar Dados';
    }
}

function updateStatsFiltered(data) {
    document.getElementById('totalEsps').textContent = '1';
    document.getElementById('totalSensores').textContent = data.leituras_por_sensor.length;
    const totalLeituras = data.leituras_por_sensor.reduce((sum, item) => sum + item.total_leituras, 0);
    document.getElementById('totalLeituras').textContent = totalLeituras;
    
    // Não atualiza os botões de filtro aqui, apenas as estatísticas
    // Os botões são criados apenas na visualização completa
}

function updateTimelineFiltered(leituras) {
    console.log('⏱️ Atualizando timeline (filtrado)...', leituras);
    updateTimelineFromLeituras(leituras);
}

function updateValoresRecentesFiltered(valores) {
    const container = document.getElementById('valoresRecentesContainer');
    console.log('🔢 Atualizando valores recentes (filtrado)...', valores);
    
    if (!valores || valores.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>Nenhum valor recente para esta ESP</p>
            </div>
        `;
        return;
    }

    // Agrupa por sensor
    const porSensor = {};
    valores.forEach(v => {
        if (!porSensor[v.sensor]) {
            porSensor[v.sensor] = {
                sensor: v.sensor,
                timestamp: v.timestamp,
                campos: []
            };
        }
        porSensor[v.sensor].campos.push({
            campo: v.campo,
            valor: v.valor
        });
    });

    let html = '<div class="valores-grid">';
    
    for (const [sensor, dados] of Object.entries(porSensor)) {
        const timestamp = new Date(dados.timestamp).toLocaleString('pt-BR');
        
        html += `
            <div class="valor-card">
                <div class="valor-card-header">
                    <span class="sensor-badge">${sensor}</span>
                    <span class="valor-timestamp">${timestamp}</span>
                </div>
                <div class="valor-fields">
        `;
        
        dados.campos.forEach(campo => {
            html += `
                <div class="valor-field">
                    <span class="valor-field-name">${campo.campo}:</span>
                    <span class="valor-field-value">${Number(campo.valor).toFixed(2)}</span>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function updateDetailedReadingsFiltered(leituras) {
    const container = document.getElementById('readingsTableContainer');
    
    if (!leituras || leituras.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>Nenhuma leitura encontrada para esta ESP</p>
            </div>
        `;
        return;
    }

    let html = '<table class="readings-table">';
    html += '<thead><tr>';
    html += '<th>ID</th>';
    html += '<th>Sensor</th>';
    html += '<th>Valores</th>';
    html += '<th>Timestamp</th>';
    html += '</tr></thead>';
    html += '<tbody>';

    for (const reading of leituras) {
        const timestamp = new Date(reading.timestamp).toLocaleString('pt-BR');
        
        const valores = reading.valores.map(v => 
            `<span class="value-item">${v.campo}: ${Number(v.valor).toFixed(2)}</span>`
        ).join(' ');

        html += `<tr>
            <td><strong>#${reading.leitura_id}</strong></td>
            <td><span class="sensor-badge">${reading.sensor}</span></td>
            <td class="value-cell">${valores}</td>
            <td class="timestamp-cell">${timestamp}</td>
        </tr>`;
    }

    html += '</tbody></table>';
    container.innerHTML = html;
}

function updateTimelineFromLeituras(leituras) {
    // Converte leituras para o formato esperado pela função de timeline
    const valores = [];
    leituras.forEach(leitura => {
        leitura.valores.forEach(v => {
            valores.push({
                leitura_id: leitura.leitura_id,
                sensor: leitura.sensor,
                timestamp: leitura.timestamp,
                campo: v.campo,
                valor: v.valor
            });
        });
    });
    
    // Chama função de timeline existente com dados convertidos
    createTimelineCharts(leituras);
}

// ============================================================================
// FUNÇÕES PRINCIPAIS
// ============================================================================

async function loadAllData() {
    const btn = document.querySelector('.refresh-btn');
    btn.disabled = true;
    btn.textContent = '⏳ Carregando...';

    try {
        const response = await fetch(`${API_BASE}/api/chart-data`);
        const result = await response.json();

        if (result.ok) {
            console.log('📦 Dados recebidos da API:', result.data);
            
            updateStats(result.data);
            updateChartEsps(result.data.leituras_por_esp);
            updateChartSensores(result.data.leituras_por_sensor);
            updateTimeline(result.data.valores_recentes);
            updateValoresRecentes(result.data.valores_recentes);
            updateDetailedReadings(result.data.ultimas_leituras);
            
            document.getElementById('lastUpdate').textContent = 
                `Última atualização: ${new Date().toLocaleTimeString('pt-BR')}`;
        } else {
            console.error('Erro na resposta da API:', result.error);
        }
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = '🔄 Atualizar Dados';
    }
}

function updateDetailedReadings(leituras) {
    const container = document.getElementById('readingsTableContainer');
    console.log('🔍 Atualizando leituras detalhadas...', leituras);
    
    if (!leituras || leituras.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>Nenhuma leitura encontrada ainda</p>
                <p style="font-size: 12px; margin-top: 10px;">
                    Execute o simulador para gerar dados de teste
                </p>
            </div>
        `;
        return;
    }

    fetch(`${API_BASE}/api/detailed-readings?limit=50`)
        .then(response => response.json())
        .then(result => {
            if (result.ok && result.data.length > 0) {
                let html = '<table class="readings-table">';
                html += '<thead><tr>';
                html += '<th>ID</th>';
                html += '<th>ESP</th>';
                html += '<th>Sensor</th>';
                html += '<th>Valores</th>';
                html += '<th>Timestamp</th>';
                html += '</tr></thead>';
                html += '<tbody>';

                for (const reading of result.data) {
                    const timestamp = new Date(reading.timestamp).toLocaleString('pt-BR');
                    
                    const valores = reading.valores.map(v => 
                        `<span class="value-item">${v.campo}: ${v.valor.toFixed(2)}</span>`
                    ).join(' ');

                    html += `<tr>
                        <td><strong>#${reading.leitura_id}</strong></td>
                        <td><span class="esp-badge">${reading.esp}</span></td>
                        <td><span class="sensor-badge">${reading.sensor}</span></td>
                        <td class="value-cell">${valores}</td>
                        <td class="timestamp-cell">${timestamp}</td>
                    </tr>`;
                }

                html += '</tbody></table>';
                container.innerHTML = html;
                console.log('✅ Tabela de leituras detalhadas renderizada!');
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>Nenhuma leitura encontrada</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('❌ Erro ao carregar leituras detalhadas:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <p>Erro ao carregar leituras</p>
                    <p style="font-size: 12px; margin-top: 10px;">${error.message}</p>
                </div>
            `;
        });
}

function updateStats(data) {
    const totalEsps = data.leituras_por_esp.length;
    const totalSensores = data.leituras_por_sensor.length;
    const totalLeituras = data.leituras_por_esp.reduce((sum, item) => sum + item.total_leituras, 0);

    document.getElementById('totalEsps').textContent = totalEsps;
    document.getElementById('totalSensores').textContent = totalSensores;
    document.getElementById('totalLeituras').textContent = totalLeituras;
    
    // Cria botões de filtro por ESP
    const espsList = document.getElementById('espsList');
    espsList.style.display = 'block';
    
    let html = '<div style="margin-top: 10px;">';
    html += '<div style="font-size: 12px; color: #666; margin-bottom: 8px;">Clique para filtrar:</div>';
    
    data.leituras_por_esp.forEach(esp => {
        const isActive = currentESP === esp.esp ? 'active' : '';
        html += `
            <button class="esp-filter-btn ${isActive}" onclick="filterByESP('${esp.esp}')">
                ${esp.esp} (${esp.total_leituras})
            </button>
        `;
    });
    
    html += '</div>';
    espsList.innerHTML = html;
}

function updateChartEsps(data) {
    const ctx = document.getElementById('chartEsps').getContext('2d');
    
    const labels = data.map(item => item.esp);
    const values = data.map(item => item.total_leituras);

    if (chartEsps) {
        chartEsps.destroy();
    }

    chartEsps = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Leituras',
                data: values,
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

function updateChartSensores(data) {
    const ctx = document.getElementById('chartSensores').getContext('2d');
    
    const labels = data.map(item => item.sensor);
    const values = data.map(item => item.total_leituras);

    const colors = [
        '#667eea', '#764ba2', '#f093fb', '#4facfe',
        '#43e97b', '#fa709a', '#fee140', '#30cfd0',
        '#a8edea', '#fbc2eb', '#f6d365'
    ];

    if (chartSensores) {
        chartSensores.destroy();
    }

    chartSensores = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

function updateTimeline(valores) {
    console.log('⏱️ Criando gráficos separados por campo...');
    
    const container = document.getElementById('timelineChartsContainer');
    if (!container) {
        console.error('❌ Container timelineChartsContainer não encontrado!');
        return;
    }
    
    fetch(`${API_BASE}/api/detailed-readings?limit=50`)
        .then(response => response.json())
        .then(result => {
            if (!result.ok || !result.data || result.data.length === 0) {
                console.log('⚠️ Nenhum dado histórico para timeline');
                container.innerHTML = `
                    <div class="chart-card">
                        <div class="empty-state">
                            <div class="empty-state-icon">📊</div>
                            <p>Nenhum dado histórico disponível</p>
                        </div>
                    </div>
                `;
                return;
            }
            
            createTimelineCharts(result.data);
        })
        .catch(error => {
            console.error('❌ Erro ao buscar dados históricos:', error);
            container.innerHTML = `
                <div class="chart-card">
                    <div class="empty-state">
                        <div class="empty-state-icon">⚠️</div>
                        <p>Erro ao carregar dados</p>
                        <p style="font-size: 12px; margin-top: 10px;">${error.message}</p>
                    </div>
                </div>
            `;
        });
}

function updateValoresRecentes(valores) {
    const container = document.getElementById('valoresRecentesContainer');
    console.log('🔢 Atualizando valores recentes...', valores);
    
    if (!valores || valores.length === 0) {
        console.log('⚠️ Nenhum valor recente encontrado');
        container.innerHTML = `
            <div class="empty-state">
                <p>Nenhum valor recente disponível</p>
            </div>
        `;
        return;
    }

    // Agrupa valores por leitura
    const leiturasPorId = {};
    valores.forEach(valor => {
        if (!leiturasPorId[valor.leitura_id]) {
            leiturasPorId[valor.leitura_id] = {
                sensor: valor.sensor,
                timestamp: valor.timestamp,
                campos: []
            };
        }
        leiturasPorId[valor.leitura_id].campos.push({
            campo: valor.campo,
            valor: valor.valor
        });
    });

    console.log('📊 Leituras agrupadas:', leiturasPorId);

    let html = '<div class="valores-grid">';
    
    for (const [leituraId, dados] of Object.entries(leiturasPorId)) {
        const timestamp = new Date(dados.timestamp).toLocaleString('pt-BR');
        
        html += `
            <div class="valor-card">
                <div class="valor-card-header">
                    <span class="sensor-badge">${dados.sensor}</span>
                    <span class="valor-timestamp">${timestamp}</span>
                </div>
                <div class="valor-fields">
        `;
        
        dados.campos.forEach(campo => {
            html += `
                <div class="valor-field">
                    <span class="valor-field-name">${campo.campo}:</span>
                    <span class="valor-field-value">${Number(campo.valor).toFixed(2)}</span>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
    console.log('✅ Valores recentes renderizados!');
}

function createTimelineCharts(leituras) {
    const container = document.getElementById('timelineChartsContainer');
    if (!container) return;
    
    if (!leituras || leituras.length === 0) {
        container.innerHTML = `
            <div class="chart-card">
                <div class="empty-state">
                    <p>Nenhum dado para gráfico de timeline</p>
                </div>
            </div>
        `;
        return;
    }
    
    // Agrupa dados por campo
    const dadosPorCampo = {};
    
    leituras.forEach(leitura => {
        const sensorEsp = `${leitura.sensor} - ${leitura.esp}`;
        const timestamp = new Date(leitura.timestamp);
        
        leitura.valores.forEach(item => {
            const campo = item.campo;
            
            if (!dadosPorCampo[campo]) {
                dadosPorCampo[campo] = {};
            }
            
            if (!dadosPorCampo[campo][sensorEsp]) {
                dadosPorCampo[campo][sensorEsp] = {
                    label: sensorEsp,
                    data: []
                };
            }
            
            dadosPorCampo[campo][sensorEsp].data.push({
                x: timestamp,
                y: item.valor
            });
        });
    });
    
    console.log('📊 Campos encontrados:', Object.keys(dadosPorCampo));
    
    // Destroi gráficos anteriores
    Object.values(timelineCharts).forEach(chart => {
        if (chart) chart.destroy();
    });
    timelineCharts = {};
    
    container.innerHTML = '';
    
    // Cores e nomes
    const colors = {
        'rpm': '#667eea',
        'temp': '#43e97b',
        'voltage': '#fa709a',
        'current': '#fee140',
        'temperatura': '#43e97b',
        'umidade': '#30cfd0',
        'pressao': '#764ba2',
        'luminosidade': '#fbc2eb',
        'distancia': '#a8edea',
        'porta_aberta': '#f44336',
        'alerta': '#ff9800'
    };
    
    const nomeCampos = {
        'rpm': 'RPM (Rotações por Minuto)',
        'temp': 'Temperatura (°C)',
        'voltage': 'Tensão (V)',
        'current': 'Corrente (A)',
        'temperatura': 'Temperatura (°C)',
        'umidade': 'Umidade (%)',
        'pressao': 'Pressão (Pa)',
        'luminosidade': 'Luminosidade (lux)',
        'distancia': 'Distância (cm)',
        'porta_aberta': 'Estado da Porta',
        'alerta': 'Alertas'
    };
    
    // Cria gráfico para cada campo
    Object.entries(dadosPorCampo).forEach(([campo, sensores]) => {
        const chartId = `chart_${campo.replace(/[^a-zA-Z0-9]/g, '_')}`;
        const nomeAmigavel = nomeCampos[campo] || campo;
        
        const chartCard = document.createElement('div');
        chartCard.className = 'chart-card';
        chartCard.innerHTML = `
            <h2>📈 ${nomeAmigavel}</h2>
            <div class="chart-container" style="height: 350px;">
                <canvas id="${chartId}"></canvas>
            </div>
        `;
        container.appendChild(chartCard);
        
        const datasets = [];
        Object.entries(sensores).forEach(([sensorEsp, dados]) => {
            dados.data.sort((a, b) => a.x - b.x);
            
            datasets.push({
                label: sensorEsp,
                data: dados.data,
                borderColor: colors[campo] || '#667eea',
                backgroundColor: (colors[campo] || '#667eea') + '33',
                borderWidth: 3,
                tension: 0.4,
                fill: true
            });
        });
        
        const ctx = document.getElementById(chartId).getContext('2d');
        
        timelineCharts[chartId] = new Chart(ctx, {
            type: 'line',
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute',
                            displayFormats: {
                                minute: 'HH:mm'
                            }
                        }
                    },
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    });
    
    console.log(`✅ Total de ${Object.keys(timelineCharts).length} gráficos criados!`);
}

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

// Esconde o aviso se JS está funcionando
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('jsStatus').style.display = 'none';
    console.log('✅ JavaScript está executando!');
    
    // Restaura filtro salvo (se existir)
    const savedFilter = localStorage.getItem('dashboard_filter_esp');
    if (savedFilter) {
        console.log(`🔄 Restaurando filtro salvo: ${savedFilter}`);
        // Aguarda um pouco para garantir que os dados foram carregados
        setTimeout(() => {
            filterByESP(savedFilter);
        }, 500);
    } else {
        // Carrega dados ao iniciar (sem filtro)
        loadAllData();
    }
    
    // Atualiza automaticamente a cada 10 segundos
    setInterval(() => {
        // Mantém o filtro ativo durante auto-refresh
        const currentFilter = localStorage.getItem('dashboard_filter_esp');
        if (currentFilter) {
            loadESPData(currentFilter);
        } else {
            loadAllData();
        }
    }, 10000);
    
    // Fallback: Se após 3 segundos ainda estiver "Carregando...", mostrar mensagem
    setTimeout(() => {
        const containers = [
            { id: 'readingsTableContainer', name: 'Leituras Detalhadas' },
            { id: 'valoresRecentesContainer', name: 'Valores Recentes' }
        ];
        
        containers.forEach(container => {
            const element = document.getElementById(container.id);
            if (element && element.innerHTML.includes('Carregando')) {
                console.warn(`⚠️ ${container.name} ainda em carregamento após 3s`);
                element.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">🔄</div>
                        <p>Aguardando dados da API...</p>
                        <p style="font-size: 12px; margin-top: 10px;">
                            <button onclick="loadAllData()" style="padding: 8px 16px; cursor: pointer;">
                                Tentar novamente
                            </button>
                        </p>
                    </div>
                `;
            }
        });
    }, 3000);
});
