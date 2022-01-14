import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

class GroupComparator():
    
    def __init__(self, comp, ano, gp_feat='TP_COR_RACA', gp_name='raca', gps=None,
                 gp_map={0:'ND', 1: 'Branca', 2: 'Preta', 3:'Parda', 4:'Amarela', 5:'Indigena'}):
        self.gp_feat = gp_feat
        self.gp_name = gp_name
        self.gp_map = gp_map

        self.comp = comp
        self.ano = ano

        if gps is None:
            self.gps = list(gp_map.keys())
        else:
            self.gps = gps
        self.gps.append('Geral')
        
        self.df_gp = {}
        self.auc_gp = pd.DataFrame()
        self.bin_gp = {}
        
        self.questoes_list = None
    
    def get_df_gp(self):
        for g in self.gps:
            if g=='Geral':
                df = pd.read_csv("../Data/Processed/ENEM"+self.ano+"/Concluintes_regulares_"+self.comp+".csv")
            else:
                df = pd.read_csv("../Data/Processed/ENEM"+self.ano+"/CR_"+self.gp_name+"_"+self.gp_map[g]+"_"+self.comp+".csv")

            self.df_gp[g] = df
        return self.df_gp
    
    def print_mean_std(self):
        print('Média e Std por '+self.gp_name+':')
        for g in self.gps:
            if g=='Geral':
                print(f"{g} - Média: {self.df_gp[g]['NU_NOTA_'+self.comp].mean():.2f};   Std: {self.df_gp[g]['NU_NOTA_'+self.comp].std():.2f}")
            else:
                print(f"{self.gp_map[g]} - Média: {self.df_gp[g]['NU_NOTA_'+self.comp].mean():.2f};   Std: {self.df_gp[g]['NU_NOTA_'+self.comp].std():.2f}")
      
    def plot_hist_scores(self, bins=20, 
                         colors=['gray', 'tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:brown',
                                'tab:pink', 'tab:olive', 'tab:cian']):
        rows = math.ceil(len(self.gps)/3)
        
        fig, axs = plt.subplots(nrows=rows, ncols=3, figsize=(15,4*rows), sharex=True)#, sharey=True)

        fig.suptitle('Histograma de notas - '+self.comp)

        for r in range(rows):
            for c in range(3):
                i = r*3+c
                
                if i>=len(self.gps):
                    break

                axs[r,c].hist(self.df_gp[self.gps[i]]['NU_NOTA_'+self.comp], bins=bins, color=colors[i])
                
                if i!=len(self.gps)-1:
                    axs[r,c].set_title(self.gp_map[i])
                else:
                    axs[r,c].set_title('Geral')
        
        for c in range(3):
            axs[rows-1,c].set_xlabel('Nota')

        for r in range(rows):
            axs[r,0].set_ylabel('Quantidade')

        plt.show()
    
    def bin_scores(self, nota_min=300, nota_max=760, step=20):
        if self.questoes_list is None:
            self.questoes_list = list(self.df_gp['Geral'].columns[2:])

        bins = np.arange(nota_min,nota_max,step)

        for g in self.gps:
            self.df_gp[g]['Range'+self.comp] = pd.cut(self.df_gp[g]['NU_NOTA_'+self.comp], bins, right=False)

            bin_r = self.df_gp[g][self.df_gp[g]['NU_NOTA_'+self.comp]!=0].groupby('Range'+self.comp).count()[['NU_INSCRICAO']]
            bin_r = bin_r.rename(columns={'NU_INSCRICAO': 'Total'})
            bin_r = bin_r.join(self.df_gp[g][self.df_gp[g]['NU_NOTA_'+self.comp]!=0].groupby('Range'+self.comp).sum()[self.questoes_list])

            for q in self.questoes_list:
                bin_r[q] = bin_r[q]/bin_r['Total']

            self.bin_gp[g] = bin_r

        return self.bin_gp

    def auc_groups(self):
        if self.questoes_list is None:
            self.questoes_list = list(self.bin_gp['Geral'].columns[1:])
        
        for g in self.gps:
            self.auc_gp[g] = self.bin_gp[g][self.questoes_list].sum()

        return self.auc_gp

    def sort_abs_auc_dif(self):
        sorted_auc_dif = self.auc_gp.diff(axis=1).abs().max(axis=1).sort_values()
        print(sorted_auc_dif)
        
        return sorted_auc_dif
    
    def plot_item_compar(self, item):
        bin_item = self.bin_gp['Geral'][[item]]
        bin_item = bin_item.rename(columns={item: 'Geral'})
        for g in self.gps[0:-1]:
            bin_item[self.gp_map[g]]  = self.bin_gp[g][item]

        bin_item.plot(figsize=(8,6), style=['k--'],
                      title='Proporção de acertos por nota por '+self.gp_name+' - '+self.comp+' '+item,
                      xlabel='Nota', ylabel='Proporção de acertos')
        plt.show()