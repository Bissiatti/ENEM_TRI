from ProcessEnemDataClass import ProcessEnemData

penem = ProcessEnemData(ano=2019)
enem_df = penem.get_data()

competencias = ['CN', 'CH', 'LC', 'MT']
itens_anulados = {'CN': ["45168"],
                     'CH': [],
                     'LC': [],
                     'MT': []}

for comp in competencias:
    penem.process_competence(comp, itens_anulados[comp], all_p=True, concluintes=True)
    
df_grupo = penem.get_group_features()

penem.process_region_competence()

penem.process_group_competence(gp_feat='TP_COR_RACA', gp_name='raca', 
                               gp_map={0:'ND', 1: 'Branca', 2: 'Preta', 3:'Parda', 4:'Amarela', 5:'Indigena'})