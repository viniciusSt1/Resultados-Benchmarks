import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os

images_dir = 'imgs'
os.makedirs(images_dir, exist_ok=True)

# 1. Carregamento e Filtragem (Apenas v26.2.0)
df = pd.read_csv('./../summary_all_experiments.csv')

def extract_consensus(name):
    m = re.search(r'-(qbft|ibft)-v26\.2\.0_', name)
    return m.group(1).upper() if m else None

df['Consensus'] = df['Experiment'].apply(extract_consensus)
df_v26 = df[df['Consensus'].notnull()].copy()

# Estilos de Cores
styles = {
    'QBFT': {'color': 'lightcoral', 'dark': 'darkred', 'marker': 'o'},
    'IBFT': {'color': 'skyblue', 'dark': 'darkblue', 'marker': 's'}
}

def generate_comparison_plot(functions_list, metric_col, title_suffix, ylabel, filename):
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Dados filtrados e TPS ordenados
    data_subset = df_v26[df_v26['Function'].isin(functions_list)]
    ordered_tps = sorted(data_subset['TPS'].unique())
    x_indices = np.arange(len(ordered_tps))
    
    # Parâmetros de posicionamento
    width = 0.3
    offsets = [-0.2, 0.2]
    consensus_list = ['QBFT', 'IBFT']
    func_ranges = {}

    for i, consensus in enumerate(consensus_list):
        cons_df = data_subset[data_subset['Consensus'] == consensus]
        
        # Dados para os Boxplots por TPS
        boxplot_data = [cons_df[cons_df['TPS'] == tps][metric_col].values for tps in ordered_tps]
        
        # Desenha os Boxes
        bp = ax.boxplot(boxplot_data, positions=x_indices + offsets[i], widths=width,
                        patch_artist=True, showfliers=False)
        
        for patch in bp['boxes']:
            patch.set_facecolor(styles[consensus]['color'])
            patch.set_alpha(0.5)
        for median in bp['medians']:
            median.set(color=styles[consensus]['dark'], linewidth=2)
            
        # Linhas de Médias (por segmento de função)
        means = [np.mean(d) if len(d) > 0 else np.nan for d in boxplot_data]
        
        for func in functions_list:
            f_tps = sorted(cons_df[cons_df['Function'] == func]['TPS'].unique())
            if not f_tps: continue
            
            f_idx = np.array([ordered_tps.index(t) for t in f_tps])
            f_means = [means[idx] for idx in f_idx]
            
            ax.plot(f_idx + offsets[i], f_means, 
                    color=styles[consensus]['dark'], marker=styles[consensus]['marker'],
                    linestyle='-', linewidth=2, label=consensus if func == functions_list[0] else "")
            
            if i == 0: # Define range para o label de topo
                func_ranges[func] = (min(f_idx), max(f_idx))

    # Identificação Visual das Funções
    for func, (start, end) in func_ranges.items():
        ax.axvspan(start - 0.5, end + 0.5, color='gray', alpha=0.05)
        mid = (start + end) / 2
        ax.text(mid, ax.get_ylim()[1]*0.92, func.upper(), ha='center', fontsize=16, fontweight='bold', alpha=0.6)

    ax.set_xticks(x_indices)
    ax.set_xticklabels(ordered_tps, fontsize=20)
    ax.set_title(f'{ylabel} - {title_suffix} (v26.2.0)', fontsize=25, pad=20)
    ax.set_xlabel('Send Rate Configurado (TPS)', fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Legenda fixa no canto superior esquerdo
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize=14, frameon=True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()

# Execução dos Gráficos
generate_comparison_plot(['transfer', 'open'], 'Throughput_TPS', 'Open & Transfer', 'Vazão (TPS)', 'vazao_qbft_vs_ibft.png')
generate_comparison_plot(['transfer', 'open'], 'Avg_Latency_s', 'Open & Transfer', 'Latência (s)', 'latencia_qbft_vs_ibft.png')
#generate_comparison_plot(['query'], 'Throughput_TPS', 'Query', 'Vazão (TPS)', 'vazao_qbft_vs_ibft_query.png')
#generate_comparison_plot(['query'], 'Avg_Latency_s', 'Query', 'Latência (s)', 'latencia_qbft_vs_ibft_query.png')