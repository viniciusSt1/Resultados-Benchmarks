import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os

# 1. Carregamento e Preparação
df = pd.read_csv('./../summary_all_experiments.csv')

def get_version(name):
    m = re.match(r'^6n-5s-(?:qbft|ibft)-(v\d+\.\d+\.\d+)_', name)
    return m.group(1) if m else None

df['Version'] = df['Experiment'].apply(get_version)
df_comp = df[df['Version'].isin(['v24.6.0', 'v26.2.0'])].copy()
df_comp = df_comp[df_comp['Function'].isin(['open', 'transfer'])]

# Configurações de Estilo
versions = ['v24.6.0', 'v26.2.0']
styles = {
    'v24.6.0': {'color': 'gray', 'dark': '#555555', 'marker': 'o', 'label': 'Antiga (v24.6.0)'},
    'v26.2.0': {'color': 'lightgreen', 'dark': 'green', 'marker': 's', 'label': 'Nova (v26.2.0)'}
}
width, offsets = 0.25, [-0.15, 0.15]

images_dir = 'imgs'
os.makedirs(images_dir, exist_ok=True)

def generate_combined_plot(metric_col, ylabel, filename, title):
    plt.figure(figsize=(16, 9))
    
    # Ordem global dos TPS (primeiro transfer, depois open)
    all_funcs = ['transfer', 'open']
    ordered_tps = []
    for func in all_funcs:
        t_vals = sorted(df_comp[df_comp['Function'] == func]['TPS'].unique())
        ordered_tps.extend(t_vals)
    
    x_indices = np.arange(len(ordered_tps))
    func_ranges = {}
    
    for i, ver in enumerate(versions):
        ver_df = df_comp[df_comp['Version'] == ver]
        boxplot_data = [ver_df[ver_df['TPS'] == tps][metric_col].values for tps in ordered_tps]
        
        # Plot dos Boxes
        bp = plt.boxplot(boxplot_data, positions=x_indices + offsets[i], widths=width,
                        patch_artist=True, showfliers=False)
        for patch in bp['boxes']:
            patch.set_facecolor(styles[ver]['color'])
            patch.set_alpha(0.4)
        for median in bp['medians']:
            median.set(color=styles[ver]['dark'], linewidth=2)
            
        # Linha de Médias (por função)
        means = [np.mean(d) if len(d) > 0 else np.nan for d in boxplot_data]
        for func in all_funcs:
            f_tps = sorted(ver_df[ver_df['Function'] == func]['TPS'].unique())
            if f_tps:
                f_idx = np.array([ordered_tps.index(t) for t in f_tps])
                f_means = [means[idx] for idx in f_idx]
                plt.plot(f_idx + offsets[i], f_means, 
                        color=styles[ver]['dark'], marker=styles[ver]['marker'],
                        linestyle='-', linewidth=2.5, 
                        label=styles[ver]['label'] if func == 'transfer' else "")
                if i == 0: func_ranges[func] = (min(f_idx), max(f_idx))

    # Identificação das Funções
    for func, (start, end) in func_ranges.items():
        plt.axvspan(start - 0.5, end + 0.5, color='gray', alpha=0.05)
        mid = (start + end) / 2
        plt.text(mid, plt.ylim()[1]*0.92, func.upper(), ha='center', fontsize=18, fontweight='bold', alpha=0.6)

    plt.xticks(x_indices, ordered_tps, fontsize=14)
    plt.title(title, fontsize=24, pad=20)
    plt.xlabel('Send Rate Configurado (TPS)', fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.legend(loc='upper left', fontsize=14, frameon=True, shadow=True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()

# Geração
generate_combined_plot('Throughput_TPS', 'Vazão (TPS)', 'vazao_comp_versao_combined.png', 'Vazão: Antiga vs Nova (Transfer & Open)')
generate_combined_plot('Avg_Latency_s', 'Latência (s)', 'latencia_comp_versao_combined.png', 'Latência: Antiga vs Nova (Transfer & Open)')