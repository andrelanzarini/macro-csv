
// Compatível com iOS 10 Safari (sem fetch, sem let/const, sem arrow functions)

// --- Controle do coletor ---
function controlarColetor(acao) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/coletor", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            var elemento = document.getElementById("status-coletor");
            if (xhr.status === 200) {
                try {
                    var resposta = JSON.parse(xhr.responseText);
                    elemento.textContent = "Coletor " + resposta.status;
                    if (resposta.status === "iniciado") {
                        document.getElementById('status-indicador').textContent = 'Ativo';
                        document.getElementById('status-indicador').style.color = 'green';
                    } else if (resposta.status === "parado") {
                        document.getElementById('status-indicador').textContent = 'Inativo';
                        document.getElementById('status-indicador').style.color = 'red';
                    }
                } catch (e) {
                    elemento.textContent = "Erro ao interpretar resposta.";
                }
            } else {
                elemento.textContent = "Erro ao enviar comando.";
            }
        }
    };

    xhr.send(JSON.stringify({ acao: acao }));
}

// --- Atualiza status do coletor ---
function atualizarStatusColetor() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/status", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            var indicador = document.getElementById('status-indicador');
            if (!indicador) return;
            if (data.ativo) {
                indicador.textContent = 'Ativo';
                indicador.style.color = 'green';
            } else {
                indicador.textContent = 'Inativo';
                indicador.style.color = 'red';
            }
        }
    };
    xhr.send();
}

// --- Carrega dados do backend ---
function carregarDados() {
    console.log("Atualizando gráfico...");

    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/dados", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            atualizarGrafico(data);
        }
    };
    xhr.send();
}

// --- Criação e atualização do gráfico ---
function atualizarGrafico(data) {
    var ctx = document.getElementById('grafico');
    if (!ctx) {
        console.warn("Canvas #grafico não encontrado.");
        return;
    }
    var context = ctx.getContext('2d');

    if (window.chart) {
        window.chart.destroy();
    }
    // Gera labels extras até 17:00
    var now = new Date();
    var currentMinutes = now.getHours() * 60 + now.getMinutes();
    var endMinutes = 17 * 60;
    var step = 5;
    var extraLabels = [];

    for (var t = currentMinutes + step; t <= endMinutes; t += step) {
        var h = String(Math.floor(t / 60));
        var m = String(t % 60);
        if (h.length < 2) h = "0" + h;
        if (m.length < 2) m = "0" + m;
        extraLabels.push(h + ":" + m);
    }

    var allLabels = data.labels.concat(extraLabels);

    function fillWithNulls(arr) {
        var filled = arr.slice();
        for (var i = 0; i < extraLabels.length; i++) {
            filled.push(null);
        }
        return filled;
    }

    // Criação do gráfico
    window.chart = new Chart(context, {
        type: 'line',
        data: {
            labels: allLabels,
            datasets: [
                {
                    label: 'Alta',
                    data: fillWithNulls(data.alta),
                    borderColor: 'green',
                    backgroundColor: 'rgba(0,128,0,0.1)',
                    fill: false
                },
                {
                    label: 'Queda',
                    data: fillWithNulls(data.queda),
                    borderColor: 'red',
                    backgroundColor: 'rgba(255,0,0,0.1)',
                    fill: false
                },
                {
                    label: 'Neutro',
                    data: fillWithNulls(data.neutro),
                    borderColor: 'gray',
                    backgroundColor: 'rgba(128,128,128,0.1)',
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        min: -10,   // posição inicial ajustada
                        max: 30
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Quantidade'
                    }
                }],
                xAxes: [{
                    ticks: {
                        autoSkip: true,
                        maxRotation: 90,
                        minRotation: 90
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Hora'
                    }
                }]
            },
            legend: {
                position: 'top'
            }
        }
    });
}

// --- Inicialização ---
window.onload = function() {
    carregarDados();
    atualizarStatusColetor();

    // Atualiza gráfico a cada 5 min
    setInterval(function() {
        carregarDados();
    }, 5 * 60 * 1000);

    // Atualiza status do coletor a cada 5 s
    setInterval(function() {
        atualizarStatusColetor();
    }, 5000);
};


