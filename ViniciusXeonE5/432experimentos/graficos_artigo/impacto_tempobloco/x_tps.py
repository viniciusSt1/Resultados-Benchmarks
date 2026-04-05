import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# 1. Carregamento e Preparação dos Dados
df = pd.read_csv('./../summary_all_experiments.csv')

def get_block_time(name):
    # Filtra 6 nós, versão v26.2.0 e extrai o tempo de bloco (5s, 10s, etc)
    m = re.match(r'^6n-(\d+)s-(qbft|ibft)-v26\.2\.0_', name)
    return int(m.group(1)) if m else None

df['BlockTime'] = df['Experiment'].apply(get_block_time)
df_filtered = df[df['BlockTime'].notnull()].copy()

# Ordenação dos tempos de bloco e definição de cores
block_times = sorted(df_filtered['BlockTime'].unique())
colors = ['lightcoral', 'skyblue', 'lightgreen', 'mediumpurple', 'gold']
dark_colors = ['red', 'blue', 'green', 'indigo', 'darkorange']
markers = ['o', 's', '^', 'D', 'v']
offsets = np.linspace(-0.35, 0.35, len(block_times))
width = 0.12

images_dir = 'imgs'
os.makedirs(images_dir, exist_ok=True)

def generate_bt_benchmark_plot(functions_list, metric_col, title_suffix, ylabel, filename):
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Ordem de TPS baseada nas funções selecionadas
    plot_tps = []
    for func in functions_list:
        tps_vals = sorted(df_filtered[df_filtered['Function'] == func]['TPS'].unique())
        plot_tps.extend(tps_vals)
    
    x_indices = np.arange(len(plot_tps))
    func_ranges = {}
    
    for i, bt in enumerate(block_times):
        bt_df = df_filtered[df_filtered['BlockTime'] == bt]
        
        for func in functions_list:
            func_df = bt_df[bt_df['Function'] == func]
            func_tps = sorted(func_df['TPS'].unique())
            indices = [plot_tps.index(t) for t in func_tps if t in plot_tps]
            
            if not indices: continue
                
            boxplot_data = [func_df[func_df['TPS'] == tps][metric_col].values for tps in func_tps]
            
            # Desenha os Boxplots consolidando QBFT/IBFT
            ax.boxplot(boxplot_data, positions=np.array(indices) + offsets[i], widths=width,
                        patch_artist=True, boxprops=dict(facecolor=colors[i], alpha=0.5),
                        medianprops=dict(color=dark_colors[i], linewidth=2), showfliers=False)
            
            # Linha de tendência das Médias
            means = [np.mean(data) if len(data) > 0 else np.nan for data in boxplot_data]
            ax.plot(np.array(indices) + offsets[i], means, linestyle='-', marker=markers[i], 
                     color=dark_colors[i], markersize=6, 
                     label=f'Bloco: {int(bt)}s' if func == functions_list[0] else "")
            
            if i == 0: func_ranges[func] = (min(indices), max(indices))

    # Sombreamento para identificar as Funções (Open, Transfer, Query)
    for func, (start, end) in func_ranges.items():
        ax.axvspan(start - 0.5, end + 0.5, color='gray', alpha=0.05)
        mid = (start + end) / 2
        ax.text(mid, ax.get_ylim()[1]*0.92, func.upper(), ha='center', fontsize=16, fontweight='bold', alpha=0.6)

    ax.set_xticks(ticks=x_indices)
    ax.set_xticklabels(plot_tps, fontsize=20)
    ax.set_title(f'{ylabel} - {title_suffix} (6 Nós, v26.2.0)', fontsize=20)
    ax.set_xlabel('Send Rate Configurado (TPS)', fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.tick_params(axis='both', labelsize=18)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Legenda interna no canto superior esquerdo
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), title='Tempo de Bloco', loc='upper left', fontsize=14, frameon=True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()

# Execução para gerar os 4 arquivos
generate_bt_benchmark_plot(['open'], 'Throughput_TPS', 'Open', 'Vazão (TPS)', 'vazao_bt_open.png')
generate_bt_benchmark_plot(['open'], 'Avg_Latency_s', 'Open', 'Latência Média (s)', 'latencia_bt_open.png')
generate_bt_benchmark_plot(['transfer'], 'Throughput_TPS', 'Transfer', 'Vazão (TPS)', 'vazao_bt_transfer.png')
generate_bt_benchmark_plot(['transfer'], 'Avg_Latency_s', 'Transfer', 'Latência Média (s)', 'latencia_bt_transfer.png')
generate_bt_benchmark_plot(['query'], 'Throughput_TPS', 'Query', 'Vazão (TPS)', 'vazao_bt_query.png')
generate_bt_benchmark_plot(['query'], 'Avg_Latency_s', 'Query', 'Latência Média (s)', 'latencia_bt_query.png')