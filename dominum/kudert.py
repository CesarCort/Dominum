# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 13:42:18 2020

@author: Owner
"""

#from flatten_json import flatten  # flatten json | https://github.com/amirziai/flatten, para manejos 
import requests
import pandas as pd
from collections.abc import MutableMapping

# from requests.auth import HTTPDigestAuth
#%%
# =============================================================================
# FLATTEN DICT ! Para leer json super anidados
# =============================================================================

def convert_flatten(d, parent_key ='', sep ='_'): 
    items = [] 
    for k, v in d.items(): 
        new_key = parent_key + sep + k if parent_key else k 
  
        if isinstance(v, MutableMapping): 
            items.extend(convert_flatten(v, new_key, sep = sep).items()) 
        else: 
            items.append((new_key, v)) 
    return dict(items)


def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

#%%
# =============================================================================
# Login en Api Kuder
# =============================================================================
def login_kudert(email,password):
    URL = "https://api.kudert.com/login"
    
    parametros_login = {
        'email':email,
        'password':password
                        }
    
    login = requests.post(url=URL,data=parametros_login)
    r_login = login.json()
    return r_login

# token_kudert = login_kudert(email='dominumAPI@dominum.pe',password='123456')
# token_kudert['data']['token']


#%%
#TEST KUDERT API
def perfiles_ideales(token_kudert):
    URL = "https://api.kudert.com/ideal-profile"
    # data_token = {
    #                 'code':token
    #                 }
    #r_catalog = requests.get(url=URL,auth=data_token)
    r_idealprofile = requests.get(url=URL,headers={'Authorization':token_kudert})
    r_idealprofile = r_idealprofile.json()
    contador=0
    
    for i in list(range(len(r_idealprofile['data']))):
        
        #print(r_idealprofile['data'][int(i)])
        r_idealprofile_i = flatten_json(r_idealprofile['data'][i])
        
        if contador==0:
             df_idealprofile = pd.DataFrame.from_records([r_idealprofile_i])
             contador=contador+1
        else:
            df_idealprofile = df_idealprofile.append(r_idealprofile_i,ignore_index=True)        
        
    return df_idealprofile

#%%
# TEST CODE
##CONSULTADOS los DNI de los postulantes activos en stage Kudert

#Esta lectura luego se hara desde la nube

# df_postulantes_complete = pd.read_csv('postulantes_complete.csv',encoding='utf-8')

# # Aqui 
# filtro_kudert = df_tracking_stages[df_tracking_stages['stage']=='KUDERT']
# filtro_kudert = df_postulantes_complete[df_postulantes_complete['postulanteId'].isin(filtro_kudert['postulanteId'].to_list())]

#%%
# =============================================================================
# # PERSON POSITION REQUEST PERSONA
# =============================================================================


#%%
# =============================================================================
# # REGISTRO TEST KUDERT DE CADA POSTULANTE 
# =============================================================================
def request_psicometricos(filtro_kudert,token_kudert):
    contador=0
    for dni in filtro_kudert['dni']:
        URL = "https://api.kudert.com/evaluation-list/"+str(dni)
    
        k_status_postulante = requests.get(url=URL,headers={'Authorization':token_kudert})
        #print('DNI FILTRO KUDERTS STAGE: '+ dni)
        if k_status_postulante.status_code == 200:# Solo gestionamos DNIS DE EVALUADOS QUE EXISTEN EN KUDERT
            
            k_status_postulante = k_status_postulante.json()
            #print('REQUEST EXITOSO, DATA LEN: '+str(len(k_status_postulante['data'])))
            for i in range(len(k_status_postulante['data'])): # PUEDEN HABER MUCHOS TEST ASIGNADOS A UN DNI, SOLO GESTIONAMOS LOS COMPLETADOS
                #print(k_status_postulante['data'][i].get('status'))
                if (k_status_postulante['data'][i].get('status')=='COMPLETED') is True:
                    #print(k_status_postulante['data'][i].get('id'))
                    print(k_status_postulante['data'][i].get('status'))
                    print('DNI: '+ dni)
                    id = k_status_postulante['data'][i].get('id')
                    
                    # URL = "https://api.kudert.com/test-result/"+str(id)+"/person-position?type="
                    # k_versus_perfiles_ideales = requests.get(url=URL,headers={'Authorization':r_login['data']['token']})
                    # k_versus_perfiles_ideales = k_versus_perfiles_ideales.json()
                    
                    URL = "https://api.kudert.com/test-result/"+str(id)
                    
                    k_resultados_detallados = requests.get(url=URL,headers={'Authorization':token_kudert})
                    k_resultados_detallados = k_resultados_detallados.json()
                    
                    if k_resultados_detallados['data'] is None:
                        None # Solo gestionamos los TEST COMPLETADOS
                    
                    else:
                        #print(dni)
                        # print(k_resultados_detallados['data'])
                        dict_flattened = flatten_json(k_resultados_detallados.get('data'))
                        #print(dict_flattened)
                        # print(type(dict_flattened))
                        df_kudertscore = pd.DataFrame.from_records([dict_flattened])
                        df_kudertscore['postulanteId_dni'] = dni
                        
                        if contador==0:
                            df_kudertscore_general = df_kudertscore
                            contador=contador+1
                        else:
                            df_kudertscore_general = df_kudertscore_general.append(df_kudertscore,ignore_index=True)        
                            df_kudertscore_general.drop_duplicates(subset='postulanteId_dni',keep='first',inplace=True)
                    
                    
                    
                else:
                    None
        else:
            None
            
    return df_kudertscore_general
    
# Crea un registro por cada lista de Personas
# momentaneamente eliminaremos duplicados y nos quedaremos con el primero segun id


# pd.melt(df_kudertscore_general, id_vars=['id'], value_vars=['natural_dominance','natural_influence'])
#%%

#Agregando Caracteriztica DISC
def traits_kudert_score(df_kudertscore_general):
        
    df_kudertscore_general['natural_DISC_tipo'] = df_kudertscore_general[['natural_dominance',\
                                                                                 'natural_influence', 'natural_solidity', 'natural_compliance']].idxmax(axis='columns')
    df_kudertscore_general['natural_DISC_tipo'].replace({'natural_dominance':'Dominante',
           'natural_influence':'Influyente', 'natural_solidity':'Estable', 'natural_compliance':'Cumplido'},inplace=True)
    
    #Agregando Caracteriztica IE
    df_kudertscore_general['natural_IE_tipo'] = ['Impulsividad' if i<10 and i>=0 else 'Espontaneidad' if i<30 and i>=10 else 'Mesura' if i<70 and i>=30 else 'Reflexividad' if i<90 and i>=70 else 'Rigidez' for i in df_kudertscore_general['natural_IE'] ]
    
    #Agregando Caracteriztica VELNA
    df_kudertscore_general['VELNA'] = df_kudertscore_general[['verbal','space', 'logic', 'numerical', 'abstract']].mean(axis=1)
    df_kudertscore_general['VELNA_tipo'] = ['Procrastina' if i<30 and i>=0 else '+ o -' if i<70 and i>=30 else 'Fluye' for i in df_kudertscore_general['VELNA'] ]
    
    df_kudertscore_general['natural_IE_descripcion'] = ['Impulsividad' if i<10 and i>=0 else 'Espontaneidad' if i<30 and i>=10 else 'Mesura' if i<70 and i>=30 else 'Reflexividad' if i<90 and i>=70 else 'Rigidez' for i in df_kudertscore_general['natural_IE'] ]
    return df_kudertscore_general

# Guardando datos en CSV y EXCEL
# df_kudertscore_general.to_csv('kurtscore.csv',encoding='utf-8')
# df_kudertscore_general.to_excel('kurtscore.xlsm',sheet_name='score',encoding='utf-8')

#%%
#iteracion
# print(convert_flatten(k_resultados_detallados.get('data')))
    
# for dni in kudert_activos_postulantes['dni']:
#     URL = "https://api.kudert.com/evaluation-list/"+str(dni)

#     k_status_postulante = requests.get(url=URL,headers={'Authorization':r_login['data']['token']})
#     if k_status_postulante.status_code == 200:
#         k_status_postulante = k_status_postulante.json()
        
#         id = k_status_postulante['data'][0].get('id')
        
#         # URL = "https://api.kudert.com/test-result/"+str(id)+"/person-position?type="
#         # k_versus_perfiles_ideales = requests.get(url=URL,headers={'Authorization':r_login['data']['token']})
#         # k_versus_perfiles_ideales = k_versus_perfiles_ideales.json()
        
#         URL = "https://api.kudert.com/test-result/"+str(id)

#         k_resultados_detallados = requests.get(url=URL,headers={'Authorization':r_login['data']['token']})
#         k_resultados_detallados = k_resultados_detallados.json()

# =============================================================================
# EJECUCION
# =============================================================================
#%%
# token_kudert = login_kudert(email='dominumAPI@dominum.pe',password='123456')
# token_kudert['data']['token']
# token_kudert = token_kudert['data']['token']

# filtro_kudert = df_tracking_stages[df_tracking_stages['stage']=='KUDERT']
# filtro_kudert = df_postulantes_complete[df_postulantes_complete['postulanteId'].isin(filtro_kudert['postulanteId'].to_list())]

# test_request_kudert = request_psicometricos(filtro_kudert,token_kudert=token_kudert)
# test_request_kudert = traits_kudert_score(test_request_kudert)
#%%
# for i in range(2):
#     print(k_status_postulante['data'][i].get('status')=='COMPLETED')
#     if (k_status_postulante['data'][i].get('status')=='COMPLETED') is True:
#         print(k_status_postulante['data'][i].get('id'))
#     else:
#         #break
#         None
# URL = "https://api.kudert.com/evaluation-list/10748296"
    
# k_status_postulante = requests.get(url=URL,headers={'Authorization':token_kudert})