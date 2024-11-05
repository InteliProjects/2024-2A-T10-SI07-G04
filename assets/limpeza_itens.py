import pandas as pd
import unicodedata

# 
def normalize_string(s):
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')

def remove_comma(df, column):
    df[column] = df[column].str.replace(',', '')
    return df
    
def remove_special_chars_of_df(df):
    for column in df.columns:
        if df[column].dtype == 'object':
            df[column] = df[column].str.replace(r'[^\w\s]', '')
    return df

# Converter valores em todas as colunas de SIM, sim, SIM para Y e de NÃO, não, NAO para N
def convert_to_yes_no(df):
    df = df.replace(to_replace=r'\b[Ss][Ii][Mm]\b', value='Y', regex=True)
    df = df.replace(to_replace=r'\b[Nn][ãã][Oo]\b', value='N', regex=True)
    return df

# Comparar e atualizar ItemsGroupCode
def update_item_group_code(template_df, itens_df):
    template_df['Nº do item'] = template_df['Nº do item'].str.strip()
    template_df['Grupo de itens'] = template_df['Grupo de itens'].str.strip()
    itens_df['ItemCode'] = itens_df['ItemCode'].str.strip()
    itens_df['ItemsGroupCode'] = 'UNMATCHED' 

    for i, item_row in itens_df.iterrows():
        item_code = normalize_string(str(item_row['ItemCode']).strip())
        mask = template_df['Nº do item'].str.strip().str.upper().apply(normalize_string) == item_code.upper()
        if mask.any():
            group_code = template_df.loc[mask, 'Grupo de itens'].values[0]
            itens_df.at[i, 'ItemsGroupCode'] = group_code
        else:
            itens_df.at[i, 'ItemsGroupCode'] = 'UNMATCHED'
            
    itens_df = itens_df[itens_df['ItemsGroupCode'] != 'UNMATCHED']
            
    return itens_df

# Atualizar ItemType
def update_item_type(itens_df):
    itens_df['ItemType'] = 'I'
    return itens_df

# Atualizar ItemClass só na coluna 'ItemClass' por ictMaterial onde ItemClass = "Material" e onde ItemClass = "Serviços" por ictService
def update_item_class(itens_df, column='ItemClass'):
    itens_df[column] = itens_df[column].replace(to_replace=['Material'], value='itcMaterial')
    itens_df[column] = itens_df[column].replace(to_replace=['Serviços'], value='itcService')
    itens_df[column] = itens_df[column].replace(to_replace=['Serviço'], value='itcService')
    
    
    return itens_df

# Atualizar MaterialType
def update_material_type(itens_df):
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Mercadoria para Revenda'], value='0')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Matéria-Prima'], value='1')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Matéria Prima'], value='1')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Embalagem'], value='2')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Produto em Processo'], value='3')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Produto Acabado'], value='4')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Subproduto'], value='5')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Produto Intermediário'], value='6')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Material de Uso e Consumo'], value='7')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Ativo Imobilizado'], value='8')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Serviços'], value='9')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Outros insumos'], value='10')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Outros Insumos'], value='10')
    itens_df["MaterialType"] = itens_df["MaterialType"].replace(to_replace=['Outras'], value='99')
    return itens_df

# Atualizar ProductSource
def update_product_source(itens_df):
    itens_df = itens_df.replace(to_replace=['Nacional, exceto as indicadas nos códigos 3 a 5'], value='0')
    itens_df = itens_df.replace(to_replace=['Estrangeira - Importação direta, exceto a indicada no código 6'], value='1')
    itens_df = itens_df.replace(to_replace=['Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7'], value='2')
    itens_df = itens_df.replace(to_replace=['Nacional, mercadoria ou bem com Conteúdo de Importação superior a 40% (quarenta por cento)'], value='3')
    itens_df = itens_df.replace(to_replace=['Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos de que tratam o Decreto-Lei no 288/1967, e as Leis no 8.248/1991, 8.387/1991,10.176/2001 e 11.484/2007'], value='4')
    itens_df = itens_df.replace(to_replace=['Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40% (quarenta por cento)'], value='5')
    itens_df = itens_df.replace(to_replace=['Estrangeira - Importação direta, sem similar nacional, constante em lista de Resolução CAMEX'], value='6')
    return itens_df

# remover linhas onde a coluna 'ItemsGroupCode' é 'UNMATCHED'
def remove_unmatched(itens_df):
    itens_df = itens_df[itens_df['ItemsGroupCode'] != 'UNMATCHED']
    return itens_df

# Rodar as funções acima
def main():
    # Carregar os DataFrames
    template_df = pd.read_csv('assets/template.csv', dtype=str)
    itens_df = pd.read_csv('assets/item.csv', dtype=str)
    columns_df = pd.read_csv('assets/columns.csv', dtype=str)
    columns_to_use = columns_df.columns.to_list()
    copy_of_first_line = columns_df.loc[0].copy()
    print(copy_of_first_line)

    # Aplicar as funções de atualização
    itens_df = itens_df[columns_to_use]
    itens_df = remove_special_chars_of_df(itens_df)
    itens_df = remove_comma(itens_df, "ItemName")
    itens_df = convert_to_yes_no(itens_df)
    itens_df = update_item_group_code(template_df, itens_df)
    itens_df = update_item_type(itens_df)
    itens_df = update_item_class(itens_df)
    itens_df = update_material_type(itens_df)
    itens_df = update_product_source(itens_df)
    itens_df["ShipType"] = ""
    
    first_line_df = pd.DataFrame([copy_of_first_line])

    # Concatenar a linha copiada com o DataFrame atualizado
    itens_df = pd.concat([first_line_df, itens_df]).reset_index(drop=True)
    
    # Salvar o DataFrame atualizado em um novo arquivo para evitar sobrescrever o original
    itens_df.to_csv('assets/itemUpdated.csv', index=False)

main()