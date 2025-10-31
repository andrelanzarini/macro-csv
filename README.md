# macro-csv
Monitor de Ativos Financeiros

Programa desenvolvido para analisar a variação percentual de uma lista de ativos financeiros selecionados
no site investing.com com ajuda de uma extensão automatizando o download dos dados direto do site.
Com o resultado da análise, uma tabela simples em SQLite faz o armazenamento do resultado a cada 5 minutos.
Esse resultado é mostrado em um gráfico com valores positivos entre 0 e 30 duranto o dia desde o primeiro 
minuto que é iniciado até o final do dia quando é desligado manualmente.
