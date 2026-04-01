import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# 1. Carregamento e Preparação dos Dados
df = pd.read_csv('./../summary_all_experiments.csv')

def get_nodes(name):
    m = re.match(r'^(\d+)n-5s-(qbft|ibft)-v26\.2\.0_', name)
    return int(m.group(1)) if m else None

df['Nodes'] = df['Experiment'].apply(get_nodes)
df = df[df['Nodes'].notnull()].copy()

# Cores distintas: 4n (Vermelho), 6n (Azul), 8n (Verde), 10n (Roxo), 12n (Laranja/Ouro)
colors = ['lightcoral', 'skyblue', 'lightgreen', 'mediumpurple', 'gold']
dark_colors = ['red', 'blue', 'green', 'indigo', 'darkorange']
markers = ['o', 's', '^', 'D', 'v']
node_counts = sorted(df['Nodes'].unique())
offsets = np.linspace(-0.35, 0.35, len(node_counts))
width = 0.12
images_dir = 'imgs'
os.makedirs(images_dir, exist_ok=True)

def generate_benchmark_plot(functions_list, metric_col, title_suffix, ylabel, filename):
    # Ajuste de tamanho e remoção de margens iniciais
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Determinar a ordem de TPS para este gráfico
    plot_tps = []
    for func in functions_list:
        tps_vals = sorted(df[df['Function'] == func]['TPS'].unique())
        plot_tps.extend(tps_vals)
    
    x_indices = np.arange(len(plot_tps))
    func_ranges = {}
    
    for i, nodes in enumerate(node_counts):
        node_df = df[df['Nodes'] == nodes]
        
        for func in functions_list:
            func_df = node_df[node_df['Function'] == func]
            func_tps = sorted(func_df['TPS'].unique())
            indices = [plot_tps.index(t) for t in func_tps if t in plot_tps]
            
            if not indices: continue
                
            boxplot_data = [func_df[func_df['TPS'] == tps][metric_col].values for tps in func_tps]
            
            # Plot dos Boxes
            ax.boxplot(boxplot_data, positions=np.array(indices) + offsets[i], widths=width,
                        patch_artist=True, boxprops=dict(facecolor=colors[i], alpha=0.5),
                        medianprops=dict(color=dark_colors[i], linewidth=2), showfliers=False)
            
            # Plot das Linhas de Médias
            means = [np.mean(data) if len(data) > 0 else np.nan for data in boxplot_data]
            ax.plot(np.array(indices) + offsets[i], means, linestyle='-', marker=markers[i], 
                     color=dark_colors[i], markersize=6, 
                     label=f'{int(nodes)} Nós, 5s, v26.2.0' if func == functions_list[0] else "")
            
            if i == 0: func_ranges[func] = (min(indices), max(indices))

    # Identificação Visual das Funções (Sombreamento e Texto)
    for func, (start, end) in func_ranges.items():
        ax.axvspan(start - 0.5, end + 0.5, color='gray', alpha=0.05)
        mid = (start + end) / 2
        ax.text(mid, ax.get_ylim()[1]*0.92, func.upper(), ha='center', fontsize=16, fontweight='bold', alpha=0.6)

    ax.set_xticks(ticks=x_indices)
    ax.set_xticklabels(plot_tps, fontsize=20)
    ax.set_title(f'{ylabel} - {title_suffix} (v26.2.0)', fontsize=25, pad=20)
    ax.set_xlabel('Send Rate Configurado (TPS)', fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.tick_params(axis='both', labelsize=18)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Legenda no canto superior esquerdo (dentro do gráfico)
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), title='Rede', loc='upper left', fontsize=14, frameon=True)
    
    # Maximiza a área ocupada pelo gráfico (remove margens brancas)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()

# Geração dos 4 Gráficos ajustados
generate_benchmark_plot(['transfer', 'open'], 'Throughput_TPS', 'Open & Transfer', 'Vazão (TPS)', 'vazao_open_transfer.png')
generate_benchmark_plot(['transfer', 'open'], 'Avg_Latency_s', 'Open & Transfer', 'Latência Média (s)', 'latencia_open_transfer.png')
generate_benchmark_plot(['query'], 'Throughput_TPS', 'Query', 'Vazão (TPS)', 'vazao_query.png')
generate_benchmark_plot(['query'], 'Avg_Latency_s', 'Query', 'Latência Média (s)', 'latencia_query.png')