async function fetchData() {
  const response = await fetch("/data");
  const data = await response.json();
  return data;
}

function formatarDataExtenso() {
    const dias = ['Domingo', 'Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado'];
    const meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    
    const hoje = new Date();
    const diaSemana = dias[hoje.getDay()];
    const dia = String(hoje.getDate()).padStart(2, '0');
    const mes = meses[hoje.getMonth()];
    const ano = hoje.getFullYear();

    return `${diaSemana} ${dia} de ${mes} de ${ano}`;
}

function controlarColetor(acao) {
  fetch('/coletor', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ acao: acao })
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("status-coletor").innerText = `Coletor ${data.status}`;
    })
    .catch(error => {
      document.getElementById("status-coletor").innerText = "Erro ao controlar o coletor.";
      console.error(error);
    });
}

function atualizarStatusColetor() {
  fetch('/status')
    .then(response => response.json())
    .then(data => {
      const indicador = document.getElementById('status-indicador');
      if (data.ativo) {
        indicador.textContent = 'Ativo';
        indicador.style.color = 'green';
      } else {
        indicador.textContent = 'Inativo';
        indicador.style.color = 'red';
      }
    })
    .catch(() => {
      const indicador = document.getElementById('status-indicador');
      indicador.textContent = 'Erro ao verificar';
      indicador.style.color = 'gray';
    });
}

let chart = null;

async function carregarDados() {
    console.log("Atualizando gráfico...");

    try {
        const response = await fetch("/dados");
        const data = await response.json();

        // Gera labels extras até 17:00
        const now = new Date();
        const currentMinutes = now.getHours() * 60 + now.getMinutes();
        const endMinutes = 17 * 60;
        const step = 5;
        const extraLabels = [];

        for (let t = currentMinutes + step; t <= endMinutes; t += step) {
            const h = String(Math.floor(t / 60)).padStart(2, '0');
            const m = String(t % 60).padStart(2, '0');
            extraLabels.push(`${h}:${m}`);
        }

        // Junta os labels originais + extras
        const allLabels = [...data.labels, ...extraLabels];

        // Preenche os datasets com dados + nulls extras
        const fillWithNulls = (arr) => [...arr, ...Array(extraLabels.length).fill(null)];

        const datasets = [
            {
                label: 'Alta',
                data: fillWithNulls(data.alta),
                borderColor: 'green',
                backgroundColor: 'rgba(0,128,0,0.1)',
                fill: false,
                tension: 0.4
            },
            {
                label: 'Queda',
                data: fillWithNulls(data.queda),
                borderColor: 'red',
                backgroundColor: 'rgba(255,0,0,0.1)',
                fill: false,
                tension: 0.4
            },
            {
                label: 'Neutro',
                data: fillWithNulls(data.neutro),
                borderColor: 'gray',
                backgroundColor: 'rgba(128,128,128,0.1)',
                fill: false,
                tension: 0.4
            }
        ];

        const ctx = document.getElementById('grafico').getContext('2d');

        if (chart) {
            chart.destroy(); // atualiza o gráfico existente
        }

        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: allLabels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Hora'
                        },
                        ticks: {
                            maxRotation: 90,
                            minRotation: 90
                        }
                    },
                    y: {
                        beginAtZero: true,
                        min: -10,
                        max: 30,
                        title: {
                            display: false,
                            text: 'Quantidade'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    } catch (error) {
        console.error("Erro ao carregar dados:", error);
    }
}

// Inicializa tudo
window.addEventListener('DOMContentLoaded', () => {
    carregarDados();
    atualizarStatusColetor();
    setInterval(carregarDados, 5 * 60 * 1000);   // a cada 5 min
    setInterval(atualizarStatusColetor, 15000);   // a cada 15 seg
});
