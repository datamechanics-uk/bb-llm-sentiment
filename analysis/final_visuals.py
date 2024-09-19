import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use Agg backend to avoid Tcl
import matplotlib.pyplot as plt
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.paths import Paths

def read_excel_data(file_path):
    with pd.ExcelFile(file_path) as xls:
        df_with_controls = pd.read_excel(xls, 'With Controls')
        df_without_controls = pd.read_excel(xls, 'Without Controls')
    return df_with_controls, df_without_controls

def plot_average_pvalues(df_with_controls, df_without_controls):
    spx_tfs = ['1D', '3D', '7D', '14D']
    avg_pvalues_with = df_with_controls.groupby('Dependent Variable')['P-Value'].mean().reindex(['SPX1D', 'SPX3D', 'SPX7D', 'SPX14D'])
    avg_pvalues_without = df_without_controls.groupby('Dependent Variable')['P-Value'].mean().reindex(['SPX1D', 'SPX3D', 'SPX7D', 'SPX14D'])
    
    mse_with = df_with_controls.groupby('Dependent Variable')['MSE'].mean().reindex(['SPX1D', 'SPX3D', 'SPX7D', 'SPX14D'])
    mse_without = df_without_controls.groupby('Dependent Variable')['MSE'].mean().reindex(['SPX1D', 'SPX3D', 'SPX7D', 'SPX14D'])

    x = range(len(spx_tfs))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=(12, 7))

    # P-values plot
    rects1 = ax1.bar([i - width/2 for i in x], avg_pvalues_with, width, label='P-Value (With Controls)', color='royalblue', alpha=0.7)
    rects2 = ax1.bar([i + width/2 for i in x], avg_pvalues_without, width, label='P-Value (Without Controls)', color='lightgreen', alpha=0.7)

    ax1.set_ylabel('Average P-Value')
    ax1.set_title('Average P-Values and MSE Across Time Horizons')
    ax1.set_ylim(0, max(avg_pvalues_with.max(), avg_pvalues_without.max()) * 1.1)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax1.annotate(f'{height:.4f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', rotation=90, fontsize=8)

    autolabel(rects1)
    autolabel(rects2)

    # MSE plot on secondary y-axis
    ax2 = ax1.twinx()
    line1 = ax2.semilogy(x, mse_with, 'ro-', label='MSE (With Controls)', markersize=8)
    line2 = ax2.semilogy(x, mse_without, 'go-', label='MSE (Without Controls)', markersize=8)
    ax2.set_ylabel('Mean Squared Error (MSE)')

    # Shared x-axis settings
    ax1.set_xticks(x)
    ax1.set_xticklabels(spx_tfs)
    ax1.set_xlabel('Time Horizon')

    # Combine legends and place inside the plot
    lines_labels = [ax1.get_legend_handles_labels(), ax2.get_legend_handles_labels()]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    ax1.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)  # Make room for the legend
    plt.savefig(os.path.join(Paths().pls_results_folder(), 'average_pvalues_and_mse.png'))
    plt.close()

def main():
    paths = Paths()
    excel_file_path = paths.pls_results_file()
    df_with_controls, df_without_controls = read_excel_data(excel_file_path)
    plot_average_pvalues(df_with_controls, df_without_controls)
    print(f"Bar chart with MSE lines saved as PNG in '{paths.pls_results_folder()}'")

if __name__ == "__main__":
    main()