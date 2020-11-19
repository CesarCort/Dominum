# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:56:33 2020

@author: César Cortez
"""
# =============================================================================
# ### PREPARACIÓN
# =============================================================================
import requests  # Peticion GET - POST, Lectura cadenas Json
import pandas as pd # pandas, modelado de data
import os,sys
from flatten_json import flatten  # flatten json | https://github.com/amirziai/flatten, para manejos 
from datetime import datetime
from datetime import date
#from geopy.geocoders import GoogleV3
import numpy as np
import re
# from collections import MutableMapping
import time
import random
import kudert # by dominum
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import shutil
from cred import credential
os.getcwd()

#import os, sys
os.path.abspath(os.path.dirname(sys.argv[0]))

def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '.')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out
#%%
def diasHastaFecha(day1, month1, year1, day2, month2, year2):
    
    # Función para calcular si un año es bisiesto o no
    
    def esBisiesto(year):
        return year % 4 == 0 and year % 100 != 0 or year % 400 == 0
    
    # Caso de años diferentes
    
    if (year1<year2):
        
        # Días restante primer año
        
        if esBisiesto(year1) == False:
            diasMes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            diasMes = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
     
        restoMes = diasMes[month1] - day1
    
        restoYear = 0
        i = month1 + 1
    
        while i <= 12:
            restoYear = restoYear + diasMes[i]
            i = i + 1
    
        primerYear = restoMes + restoYear
    
        # Suma de días de los años que hay en medio
    
        sumYear = year1 + 1
        totalDias = 0
    
        while (sumYear<year2):
            if esBisiesto(sumYear) == False:
                totalDias = totalDias + 365
                sumYear = sumYear + 1
            else:
                totalDias = totalDias + 366
                sumYear = sumYear + 1
    
        # Dias año actual
    
        if esBisiesto(year2) == False:
            diasMes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            diasMes = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
        llevaYear = 0
        lastYear = 0
        i = 1
    
        while i < month2:
            llevaYear = llevaYear + diasMes[i]
            i = i + 1
    
        lastYear = day2 + llevaYear
    
        return totalDias + primerYear + lastYear
    
    # Si estamos en el mismo año
    
    else:
        
        if esBisiesto(year1) == False:
            diasMes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            diasMes = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
        llevaYear = 0
        total = 0
        i = month1
        
        if i < month2:
            while i < month2:
                llevaYear = llevaYear + diasMes[i]
                i = i + 1
            total = day2 + llevaYear - 1
            return total 
        else:
            total = day2 - day1
            return total
#%%
# =============================================================================
# FLATTEN DICT ! Para leer json super anidados
# =============================================================================

# def convert_flatten(d, parent_key ='', sep ='_'): 
#     items = [] 
#     for k, v in d.items(): 
#         new_key = parent_key + sep + k if parent_key else k 
  
#         if isinstance(v, MutableMapping): 
#             items.extend(convert_flatten(v, new_key, sep = sep).items()) 
#         else: 
#             items.append((new_key, v)) 
#     return dict(items)

#%%
# =============================================================================
# Remover Outliers
# =============================================================================
def remove_outlier(df_in, col_name):
    q1 = df_in[col_name].quantile(0.25)
    q3 = df_in[col_name].quantile(0.75)
    iqr = q3-q1 #Interquartile range
    fence_low  = q1-1.5*iqr
    fence_high = q3+1.5*iqr
    df_in.loc[(df_in[col_name] < fence_low) & (df_in[col_name] > fence_high)] = np.nan
    df_normal = df_in.loc[(df_in[col_name] > fence_low) & (df_in[col_name] < fence_high)]
    mean = df_normal['salarioPretendido'].mean()
    df_in[col_name].fillna(mean,inplace=True)
    df_out = df_in
    return df_out
    
#%%

# =============================================================================
# PETICIÓN DE DATOS
# =============================================================================
def login_hiring_room(client_secret,user,password):
    #URL Requests
    URL = "https://api.hiringroom.com/v0/authenticate/login/users"
    
    body_request_to_token = {
      "grand_type": "password",
      "client_id": "dominum",
      "client_secret": client_secret,
      "username": user,
      "password": password

    }
    
    r = requests.post(url = URL, data = body_request_to_token)
    data= r.json()
    return data

# data = login_hiring_room(client_secret="7146f5b4177ae8fcec84df4829c822e6",user='rodrigo.alvarez@dominum.pe',password='Mateobenjamin2017')

#%%

#%%
### Petición VACANTES
def obtener_vacante(token,vacante='all'):
    
    if vacante == 'all':
        URL_vacante = "https://api.hiringroom.com/v0/vacancies"
        
        params_vacancies={
                            "page":0,
                            "pageSize":100,
                            "token":token,
                          }
        request_vacancies = requests.get(url=URL_vacante,params=params_vacancies)
        data_vacancies = request_vacancies.json() # Listado de Vacantes
        # with open('data_vacancies.json','wb') as f: # Escribiendo archivo json
        #         f.write(request_vacancies.content)
        #vacancies_df_json = pd.json_normalize(data_vacancies['vacantes'],max_level=1,sep="_")
        #vacancies_df_json.rename(columns={'id':'idVacantes'},inplace=True) #id_vacancies
        # hey = pd.concat([surv_melt,surv_melt.variable.str.split(':',expand=True)[1]],1)
        #dict_flattened_vacancies = flatten(data_vacancies['vacantes'], '.')
        dict_flattened_vacancies = (flatten(record, '.') for record in data_vacancies['vacantes'])
        df_vacancies = pd.DataFrame(dict_flattened_vacancies)
        
    else:
        URL_vacante = "https://api.hiringroom.com/v0/vacancies/"+vacante
        
        params_vacancies={
                            #"page":0,
                            #"pageSize":100,
                            "token":token,
                          }
        
        request_vacancies = requests.get(url=URL_vacante,params=params_vacancies)
        data_vacancies = request_vacancies.json() # Listado de Vacantes
        dict_flattened_vacancies = flatten(data_vacancies['vacante'], '.')
        df_vacancies = pd.DataFrame.from_records([dict_flattened_vacancies])
    
    df_vacancies.rename(columns={'id':'idVacante','nombre':'nombre_vacante'},inplace=True) #id_vacante
    df_vacancies = df_vacancies[['idVacante','nombre_vacante','estadoActual','client.compañia','fechaCreacion',
                                 'ubicacion.pais', 'ubicacion.provincia', 'ubicacion.ciudad'
                                 ]]
    return df_vacancies
#%%
### Zona de Testing Code
# vacancies_df_json = pd.json_normalize(data_vacancies['vacantes'],max_level=1)

# spike_cols = [col for col in df_postulants.columns if 'direccion' in col] # Consult columns
#estudios = df_postulantes_complete.filter(regex='estudios') # Directly results
#print(spike_cols)


#vacantes = obtener_vacante(vacante='all')
#vacante_bcp = obtener_vacante(vacante='5f69ea824c593146f35b53f8')
#obtener_vacante(vacante='5f69ea824c593146f35b53f8')['idVacante']

#prueba = obtener_postulante(vacante_postulantes='5f69ea824c593146f35b53f8')
#etapa_activas()
#%%
### Request POSTULANTE

def obtener_postulante(token,vacante_postulantes='all'):
    if vacante_postulantes == 'all':
        URL_postulante = "https://api.hiringroom.com/v0/postulants"
        # de momento solo sera una busqueda por paginas 1 al 10
        # se desarrollara un forma de solo buscar por cliente y vacantes
        j=0
        for i in range(40):
            params_postulants={
                           "token":token,
                           'page':i,
                           'pageSize':100
                            }
            
            request_postulants = requests.get(url=URL_postulante,params=params_postulants)
            data_postulant_json = request_postulants.json() # Listado de postulantes 
            
            if request_postulants.status_code == 200:
                dict_flattened = (flatten(record, '.') for record in data_postulant_json['curriculums'])
                df_postulants_1 = pd.DataFrame(dict_flattened)
                df_postulants_1.rename(columns={'id':'postulanteId'},inplace=True) #id_postulante
                if j ==0:
                    df_postulants = df_postulants_1
                    j=j+1
                else:
                    df_postulants = df_postulants.append(df_postulants_1,ignore_index=True)
        df_postulants.rename(columns={'vacanteId':'idVacante'},inplace=True)
    else:
        vacante_postulantes = str(vacante_postulantes) 
        URL_postulante = "https://api.hiringroom.com/v0/postulants"
        # de momento solo sera una busqueda por paginas 1 al 10
        # se desarrollara un forma de solo buscar por cliente y vacantes
        j=0
        for i in range(40):
            params_postulants={
                           "token":token,
                           'page':i,
                           'pageSize':100,
                           'vacancyId':vacante_postulantes
                            }
            
            request_postulants = requests.get(url=URL_postulante,params=params_postulants)
            data_postulant_json = request_postulants.json() # Listado de postulantes 
            
            if request_postulants.status_code == 200 :
                dict_flattened = (flatten_json(record) for record in data_postulant_json['curriculums'])
                df_postulants_1 = pd.DataFrame(dict_flattened)
                df_postulants_1.rename(columns={'id':'postulanteId'},inplace=True) #id_postulante
                if j ==0:
                    df_postulants = df_postulants_1
                    j=j+1
                else:
                    df_postulants = df_postulants.append(df_postulants_1,ignore_index=True)
            else:
                None
        #change position
        df_postulants.rename(columns={'vacanteId':'idVacante'},inplace=True)
        
    return df_postulants

#%%link CV
# URL_postulantecv = "https://api.hiringroom.com/v0/postulants/curriculum/5f693aa5518fcc1f2f09a8ad"

#%%
### Request ETAPAS ACTIVAS EN CUENTA

def etapas_activas(token):
    URL_stages = "https://api.hiringroom.com/v0/account/stages"
    params_stages={
                       "token":token,
                        }
    
    request_stages = requests.get(url=URL_stages,params=params_stages)
    data_stages = request_stages.json() # Listado de Vacantes
    df_stages = pd.DataFrame.from_dict(data_stages['stages'])
    active_stages = df_stages['nombre'].to_list()
    
    del df_stages, data_stages # liberamos memoria
    return active_stages

#%%

# =============================================================================
# # ===========================================================================
# # ### Combinación y transformaciones | Postulants & Vacants |
# # ===========================================================================
# =============================================================================

#df_postulants = obtener_postulante(vacante_postulantes='5f7157e5cfbc435a7e7fa158')
#df_vacancies = obtener_vacante(vacante='5f7157e5cfbc435a7e7fa158')
#>>> Mergue Vacantes $ postulantes
#df_postulantes_complete = df_postulants.merge(df_vacancies,on=['idVacante']) # merge 

def calculate_age(born): # Función para calcular edad
    if born is None:
        return None
    else:
        born = datetime.strptime(born, "%d-%m-%Y").date()
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def procesar(df_postulantes_complete):
    
    # =============================================================================
    #     CONVERSION
    # =============================================================================
    #df_postulantes_complete['dni'] = pd.to_numeric(df_postulantes_complete['dni'],errors='ignore')
    
    
    df_postulantes_complete['edadPostulante'] = df_postulantes_complete['fechaNacimiento'].apply(calculate_age) # calculo de la edad
    
    #categorización de Edades
     # https://www.ipsos.com/sites/default/files/inline-images/GENERACIONES-05.jpg
     # https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.businessinsider.com%2Fgeneration-you-are-in-by-birth-year-millennial-gen-x-baby-boomer-2018-3&psig=AOvVaw0woYRgDKKaz7h77QoqTBPn&ust=1600621468244000&source=images&cd=vfe&ved=0CA0QjhxqFwoTCKiDoOLZ9esCFQAAAAAdAAAAABAN
     # https://www.lavanguardia.com/vivo/20180408/442342457884/descubre-que-generacion-perteneces.html
    
    mean = df_postulantes_complete['edadPostulante'].mean()
    df_postulantes_complete['edadPostulante'].fillna(mean,inplace=True)    
    
    df_postulantes_complete['edadPostulante_grupo'] = ['Menor a 20 ' if age<20 else \
                                               'De 20 a 25' if age>=20 and age<25 else \
                                               'De 26 a 30' if age>=26 and age<30 else \
                                               'De 30 a 35' if age>=30 and age<35 else \
                                               'Mayor a 35' for age in df_postulantes_complete['edadPostulante']]
    #Categorización en Generacion por Edades
    
    df_postulantes_complete['generacion_edad'] = [ np.nan if  pd.isna(fechanacimiento) else \
                                                  'Generation Z' if datetime.strptime(fechanacimiento, "%d-%m-%Y").date().year > 1999  else  \
                                                  'Millenials' if datetime.strptime(fechanacimiento, "%d-%m-%Y").date().year > 1981 and datetime.strptime(fechanacimiento, "%d-%m-%Y").date().year < 2000  else  \
                                                  'Generation Y' if datetime.strptime(fechanacimiento, "%d-%m-%Y").date().year > 1965 and datetime.strptime(fechanacimiento, "%d-%m-%Y").date().year < 1982  else   
                                                  'Baby Boomer' for fechanacimiento in df_postulantes_complete['fechaNacimiento']]
                                         
    ###>>> Manipulación de fecha: FechaExp Desde - FechaExpHasta
    
    #Juntar fechas Desde
    df_postulantes_complete.loc[:,'experienciasLaborales.0.diaDesde'] = 1 
    df_postulantes_complete.loc[:,'experienciasLaborales.1.diaDesde'] = 1 
    
    for i in list(range(2)):
    # =============================================================================
    #         CONVERSIONES
    # =============================================================================
        
        #print(i)
            #fill faltantes HASTA & DESDE
        df_postulantes_complete['experienciasLaborales.'+str(i)+'.mesHasta'] = pd.to_numeric(df_postulantes_complete['experienciasLaborales.'+str(i)+'.mesHasta'],errors='coerce')
        df_postulantes_complete['experienciasLaborales.'+str(i)+'.añoHasta'] = pd.to_numeric(df_postulantes_complete['experienciasLaborales.'+str(i)+'.añoHasta'],errors='coerce')
        df_postulantes_complete['experienciasLaborales.'+str(i)+'.mesDesde'] = pd.to_numeric(df_postulantes_complete['experienciasLaborales.'+str(i)+'.mesDesde'],errors='coerce')
        df_postulantes_complete['experienciasLaborales.'+str(i)+'.añoDesde'] = pd.to_numeric(df_postulantes_complete['experienciasLaborales.'+str(i)+'.añoDesde'],errors='coerce')
        df_postulantes_complete.loc[df_postulantes_complete['experienciasLaborales.'+str(i)+'.mesHasta'].isnull(),'experienciasLaborales.'+str(i)+'.mesHasta'] = datetime.today().month
        df_postulantes_complete.loc[df_postulantes_complete['experienciasLaborales.'+str(i)+'.añoHasta'].isnull(),'experienciasLaborales.'+str(i)+'.añoHasta'] = datetime.today().year
    
        mesDesde = df_postulantes_complete['experienciasLaborales.'+str(i)+'.mesDesde']
        añoDesde = df_postulantes_complete['experienciasLaborales.'+str(i)+'.añoDesde']
        diaDesde = df_postulantes_complete['experienciasLaborales.'+str(i)+'.diaDesde']
        #  
        
        df_postulantes_complete['fechaExpDesde'+str(i)] = pd.to_datetime(dict(year=añoDesde, month=mesDesde, day=diaDesde))
        # Juntar Fecha Hasta
        mesHasta = df_postulantes_complete['experienciasLaborales.'+str(i)+'.mesHasta']
        #df_postulantes_complete['experienciasLaborales.'+str(i)+'.añoHasta'] = df_postulantes_complete['experienciasLaborales.'+str(i)+'.añoHasta'].replace('1945',date.today().year)
        añoHasta = df_postulantes_complete['experienciasLaborales.'+str(i)+'.añoHasta']
        df_postulantes_complete.loc[:,'experienciasLaborales.'+str(i)+'.diaHasta']=1     
        diaHasta = df_postulantes_complete.loc[:,'experienciasLaborales.'+str(i)+'.diaHasta']  
        df_postulantes_complete['fechaExpHasta'+str(i)] = pd.to_datetime(dict(year=añoHasta, month=mesHasta, day=diaHasta))    ###list comprehesion -> is Nan then today.
        
        # Si no hay fecha de termino -> Fecha de hoy
        df_postulantes_complete['fechaExpDesde'+str(i)] = [pd.to_datetime('today') if isinstance(i,pd._libs.tslibs.nattype.NaTType) else i for i in df_postulantes_complete['fechaExpDesde'+str(i)]]
        df_postulantes_complete['fechaExpHasta'+str(i)] = [pd.to_datetime('today') if isinstance(i,pd._libs.tslibs.nattype.NaTType) else i for i in df_postulantes_complete['fechaExpHasta'+str(i)]]
        df_postulantes_complete['fechaExpHasta'+str(i)] = [pd.to_datetime('today') if i.year==1945 else i for i in df_postulantes_complete['fechaExpHasta'+str(i)]]
        # Tiempo de Experencia en años
        df_postulantes_complete['tiempoExp_'+str(i)] = (df_postulantes_complete['fechaExpHasta'+str(i)] - df_postulantes_complete['fechaExpDesde'+str(i)])/np.timedelta64(1, 'Y')
    
    #Hay que eliminar fechaExpHasta0 y fechaExpDesde0 
    
    df_postulantes_complete.rename(columns={'fechaExpDesde0':'fechaExpDesde','fechaExpHasta0':'fechaExpHasta'},inplace=True)
    df_postulantes_complete.drop(columns=['fechaExpDesde1','fechaExpHasta1'],inplace=True)
    # OJO: Actualmente aveces trae unas fechas inversas y la diferencia de tiempos
    # es negativa, se esta corrigiendo multiplicandolos por -1
    df_postulantes_complete['tiempoExp_0'] = [i*-1 if i<0 else i for i in df_postulantes_complete['tiempoExp_0']]
    df_postulantes_complete['tiempoExp_1'] = [i*-1 if i<0 else i for i in df_postulantes_complete['tiempoExp_1']]
    
    ###>>> Manipulación de grado académicos
    df_postulantes_complete['gradoAcademico'] = df_postulantes_complete['estudios.0.nivel'] \
                                                    +' en '+df_postulantes_complete['estudios.0.titulo'] # Nivel Grado académico = Título + nivel
    ###>> Eliminar Duplicados
    df_postulantes_complete.drop_duplicates(subset=['postulanteId','idVacante'],keep='first',inplace=True)
    df_postulantes_complete.drop_duplicates(subset='postulanteId',keep='first',inplace=True)
    #df_postulantes_complete.drop_duplicates(subset='postulanteId',keep='first',inplace=True)
    #REPLACE | Segun usuario replace default values
    df_postulantes_complete.replace({'fuente':{'linkedinjobs':'Linkedin Jobs','indeed':'Indeed','facebook_jobs':'Facebook Jobs','alertaempleos':'Alerta Empleos','bum':'Bumeran','added':'Hunting'}},inplace=True)
    
    # =============================================================================
    #     # TRATAMIENTO DE VACIOS
    # =============================================================================
    ### SECTOR
    df_postulantes_complete.loc[df_postulantes_complete['experienciasLaborales.0.industria'].isnull(),'experienciasLaborales.0.industria'] = 'No especifica'
    # df_postulantes_complete.['experienciasLaborales.0.industria'].replace(None,'No especifica',inplace=True)
    ### GENERO
    df_postulantes_complete.loc[df_postulantes_complete['genero'].isnull(),'genero'] = 'No especifica'
    # df_postulantes_complete['genero'].replace(None,'No especifica',inplace=True)
    
    # ### SALARIO PRETENDIDO
    df_postulantes_complete.loc[df_postulantes_complete.salarioPretendido<600,'salarioPretendido'] = 0
    df_postulantes_complete.loc[df_postulantes_complete.salarioPretendido>15000,'salarioPretendido'] = 0
    mean_salario = df_postulantes_complete.salarioPretendido.mean()
    std_salario = int(df_postulantes_complete.salarioPretendido.std())
    df_postulantes_complete.loc[df_postulantes_complete.salarioPretendido==0,'salarioPretendido'] = mean_salario + random.randrange(0,std_salario)
    
    #eliminacion de outliers
    # df_postulantes_complete = remove_outlier(df_postulantes_complete,col_name='salarioPretendido')
    
    return df_postulantes_complete


# df_postulantes_complete = procesar()
# df_postulantes_complete.to_csv('postulantes_complete.csv',encoding='utf-8') # save CSV
#%%


# REQUEST COMMENTS
# Leemos los comentarios(Preguntas y Respuestas) de cada postulante a la 
# pregunta clave que el reclutador realizo 
# df_postulantes_complete[['postulanteId','idVacante']]


def request_comentario(token,df_idpost_idvac):
    i=0 # contador i
    # df_idpost_idvac es un Dataframe con postulantesId y idVacantes
    for x,y in df_idpost_idvac.iloc:
        URL_postulante_comentario = "https://api.hiringroom.com/v0/postulants/"+str(x)+"/questions/"+str(y)  
        # de momento solo sera una busqueda por paginas 1 al 10
        # se desarrollara un forma de solo buscar por cliente y vacantes
        #start_time = time.time() # STARTTIME
    
        params_comentario = {
                           "token":token,
                            }
        
        request_comentario = requests.get(url=URL_postulante_comentario,params=params_comentario)
        data_comentario_json = request_comentario.json() # Listado de Vacantes
        #print(data_comentario_json['message'].contains()
        #print(data_comentario_json)
        #main()
        #print("--- %s seconds Request---" % (time.time() - start_time))
        if request_comentario.status_code == 200 and x!='5f6d3955ad23de498246b367' and x!='5f71f11887320b769d4bc507' and x!='5f7ce5863461437828204e6a':#isinstance(data_comentario_json['respuestas'],dict):
            # print(data_comentario_json)
            # print(type(data_comentario_json))
            # print(x,y)
            #print(data_comentario_json,x)
            dict_flattened = (flatten_json(record) for record in data_comentario_json['respuestas'])
            df_comentarios = pd.DataFrame(dict_flattened)
            #print(df_comentarios)
            df_comentarios.columns = df_comentarios.columns.str.replace('0.','')
            df_comentarios.columns = df_comentarios.columns.str.replace('1.','')
            # Hay casos de respuestas duplicadas
            df_comentarios = df_comentarios.T.drop_duplicates(keep='last').T
            #print(df_comentarios.columns)
            df_comentarios.drop(['id','preguntaId','fechaCreacion'],axis='columns',inplace=True)
            df_comentarios['postulanteId'] = x 
            df_comentarios['idVacante'] = y
            if i==0:
                df_comentarios_general = df_comentarios
                i=i+1
            else:
                df_comentarios_general = df_comentarios_general.append(df_comentarios,ignore_index=True)
        else:
            None
            #df_comentarios_general['preguntaTexto'].drop_duplicates().to_list()
    return df_comentarios_general






#%%

# =============================================================================
# Tracking Del Camino del postulante | Historial 
# =============================================================================
def obtener_records(token,postulantes_id_list):
    df_record_total = pd.DataFrame(columns=['postulanteId','idVacante', 'descripcion', 'fechaCreacion', 'horaCreacion'])    
    for idpostulante in postulantes_id_list:
        URL_record_by_postulant = "https://api.hiringroom.com/v0/postulants/"+str(idpostulante)+"/records"
        params_record ={
                "token":token,
                        }
    
        request_record = requests.get(url=URL_record_by_postulant,params=params_record)
        data_record_by_postulant = request_record.json() # Listado de Vacante
        
        if request_record.status_code == 200:
            df_record = pd.DataFrame.from_dict(data_record_by_postulant['records'])
            df_record= df_record[df_record['descripcion'].str.contains("etapa")]  # filtramos record de cambio de etapa
            df_record['postulanteId']=idpostulante  # Agregamos el idPostulante
            #print(df_record)
            #Inicializamos df_record_total
            
            df_record_total = df_record_total.append(df_record,ignore_index=True) # construimos Dataframe
            #print('APPEND')
            #print(df_record_total)
        else:
            None    
    return df_record_total #Contiene {postulanteId,idVacante,descripcion,fechaCreacion}



def tracking_user_way(df_postulantes_complete,df_record_total,token):
    #Extraer Todos los Stage por el que postulante ha sido registrado y me crea un registro total
    L = etapas_activas(token)
    pat = '|'.join(r"\b{}\b".format(x) for x in L)
    df_record_total['stage'] = df_record_total['descripcion'].str.extract('('+ pat + ')', expand=False, flags=re.I)
    
    #Agregamos Stage 'NUEVO' a cada postulateId por vacante
    agg_stage_nuevo_all = df_postulantes_complete[['postulanteId','idVacante']].drop_duplicates()
    # agg_stage_nuevo_all = df_record_total[['postulanteId','idVacante']].drop_duplicates()
    agg_stage_nuevo_all['stage'] = 'POSTULANTES'
    
    df_record_total = df_record_total.append(agg_stage_nuevo_all,ignore_index=True) # construimos Dataframe
    df_record_total['stage'].replace({'EN REVISIÓN':'FILTRO CV'},inplace=True)
    df_record_total.drop(['descripcion', 'fechaCreacion',
         'horaCreacion'],axis='columns',inplace=True)
    df_record_total.drop_duplicates(subset=['postulanteId','stage'],keep='first',inplace=True)
    df_record_total.reset_index(drop=True,inplace=True)
    
    return df_record_total

def actualizar_cloud(file_name_cloud,file_name_local):
    g_login = GoogleAuth() # Actualmente funciona con mi local
    g_login.LoadCredentialsFile('cred_dominum.txt')
    drive = GoogleDrive(g_login)
    
    # R1 Folder no se edita dado que es la carpeta fija para este proyecto
    folder = drive.ListFile({'q': "title = 'Job_Benchmarking_Files' and trashed=false"}).GetList()[0] # Buscamos el Folder con el nombre 'title' en GDrive
    
    # BUSCANDO ARCHIVO | POSTULANTES_COMPLETE_DASHBOARD_HR
    # R2
    file_to_update = drive.ListFile({'q': f"title = '{file_name_cloud}' and trashed=false"}).GetList()[0] # Buscamos el Folder con el nombre 'title' en GDrive
    #len(drive.ListFile({'q': f"title = '{file_name_cloud}' and trashed=false"}).GetList())
    #file_csv = drive.CreateFile({'title':'postulantes_complete.csv', 'mimeType':'text/csv', 'parents':[{'id':folder['id']}]}) # Seteamos a que folder irá
    # R3
    print(file_to_update['webContentLink'])
    file_csv = drive.CreateFile({'id':file_to_update['id'], 'mimeType':'text/csv', 'parents':[{'id':folder['id']}]}) # Seteamos a que folder irá
    # R4
    file_csv.SetContentFile(str(file_name_local)) # ¿Que archivo local subiremos?
    # R5
    file_csv.Upload()
    
    #return print('El link de descarga del archivo actualizado es:'+file_csv.metadata['webContentLink'])
    return print('archivo '+str(file_name_local)+' fue subido a la nube')



def bajar_template_pb(nombre_archivo):
    g_login = GoogleAuth() # Actualmente funciona con mi local
    g_login.LoadCredentialsFile('cred_dominum.txt')
    drive = GoogleDrive(g_login)
    
    folder = drive.ListFile({'q': "title = 'Job_Benchmarking_Files' and trashed=false"}).GetList()[0] # Buscamos el Folder con el nombre 'title' en GDrive
    file_to_download = drive.ListFile({'q': "title = 'TEMPLATE_V2.pbix' and trashed=false"}).GetList()[0] # Buscamos el Folder con el nombre 'title' en GDrive
    #len(drive.ListFile({'q': f"title = '{file_name_cloud}' and trashed=false"}).GetList())
    #file_csv = drive.CreateFile({'title':'postulantes_complete.csv', 'mimeType':'text/csv', 'parents':[{'id':folder['id']}]}) # Seteamos a que folder irá
    # R3
    #print(file_to_update['webContentLink'])
    file = drive.CreateFile({'id':file_to_download['id'], 'mimeType':'text/csv', 'parents':[{'id':folder['id']}]}) # Seteamos a que folder irá
    nombre_archivo = nombre_archivo.replace("/","-")
    file.GetContentFile(str(f"Dashboard/{nombre_archivo}.pbix")) # ¿Que archivo local subiremos?
    return 



#%%

### SCRIPT CONSOLA | USUARIO
print('#########################################################')
print('DASHBOARD HR | Bienvenido al modulo de actualización')
print('#########################################################')
print('\n')
print('A continuacion \t')
print('Las Vacantes disponibles:')
#Login en API HIRING ROOM

#Preparamos el folder contenedor#
if os.path.exists('data'):
    None
else:
    os.makedirs('data')
#Preparamos el folder dashboard
if os.path.exists('dashboard'):
    None
else:
    os.makedirs('dashboard')
    
# Manejo de errores en Login



try:
    data = login_hiring_room(client_secret=credential.client_secret_hr,user=credential.user_hr,password=credential.pass_hr)
    vacantes = obtener_vacante(token=data['token'])
    pd.set_option('display.max_rows', vacantes.shape[0]+1)
except:
    print('Error: La conexion a HiringRoom a fallado')
    sys.exit()

# Mostramos Vacantes 
print(vacantes[['nombre_vacante','estadoActual','client.compañia']])
opcion = ''

while ~(opcion in list(vacantes.index)):
    
    opcion = input('>>>Ingrese N de la vacante a procesar: ')
    opcion = int(opcion)
    
    
    if opcion in list(vacantes.index):
        
        print('\t Su eleccion corresponde a la Sgte. Vacante: \t')
        # Mostramos vacante seleccionada
        print(vacantes.iloc[opcion])
        si_no = ''
    
        while si_no!='n' or si_no!='n': # BUCLE DE PROCESAMIENTO DE VACANTES
            si_no = input('>>>Su opcion es correcta?(Y/N): ')
            si_no = si_no.lower()
        
            if si_no=='n':
            
                print('Eliga nuevamente opcion ')
                break
            
            if si_no=='y':
                
                print('# Genial! nos estamos conectando a Hiring Room para procesar la vacante  >>'+vacantes.iloc[opcion]['nombre_vacante']+'<< ,esto puede tomar unos minutos, por favor espere...')
                print('----------------------------------------------------------------------------')
                print('| Recuerda: Si tu conexion es lenta es probable que experimentes problemas |')
                print('----------------------------------------------------------------------------')
                
                postulantes = obtener_postulante(token=data['token'],vacante_postulantes=vacantes.iloc[opcion]['idVacante'])
                df_postulantes_complete = postulantes.merge(vacantes,on=['idVacante']) # merge
                df_postulantes_complete = procesar(df_postulantes_complete)
                df_postulantes_complete.to_csv('data/postulantes_complete_dashboard_hr.csv',encoding='utf-8') # save CSV
                
                # Procesando comentarios
                print('\n# Ahora procesamos las respuestas de nuestros postulantes, por favor espere...')            
                df_comentarios_general = request_comentario(token=data['token'],df_idpost_idvac=df_postulantes_complete[['postulanteId','idVacante']])
                df_comentarios_general.to_csv('data/preguntas_respondidas_db.csv',encoding='utf-8') # save CSV
                
                # Procesando EL TRACKING DEL POSTULANTE
                print('\n# Ahora nos encontramos procesando los datos necesarios para el Funnel de la Vacante, por favor espere...')
                df_records = obtener_records(token=data['token'],postulantes_id_list=df_postulantes_complete['postulanteId'])
                df_tracking_stages = tracking_user_way(df_postulantes_complete=df_postulantes_complete,df_record_total=df_records,token=data['token'])
                df_tracking_stages.to_csv('data/historico_etapas.csv',encoding='utf-8') # save CSV
                
                # Mensaje exitoso de proceso terminado
                if len(df_tracking_stages.loc[df_tracking_stages.stage=='KUDERT']['postulanteId'].unique())>0:
                
                    si_no = ''
                    print('#########################################################')
                    print('MODULO KUDERT | Test Psicométricos')
                    print('#########################################################')
                    
                    while si_no!='n' or si_no!='n': # BUCLE DE PROCESAMIENTO DE VACANTES
                        si_no = input('\n>>> Hemos detectado que '+str(len(df_tracking_stages.loc[df_tracking_stages.stage=='KUDERT']['postulanteId'].unique()))+\
                      ' postulantes han estado en la etapa KUDERT, desea procesar sus test Psicometricos?(Y/N): ')
                        si_no = si_no.lower()
                        
                        if si_no=='n':
                            print('\nNo procesamos los test Kudert, sus archivos en local estan listos!')
                            break
                        
                        if si_no=='y':
                            print('\n# Genial! ya estamos procesando las evaluaciones Kudert  >>'+vacantes.iloc[opcion]['nombre_vacante']+'<< ,esto puede tomar unos minutos, por favor espere...')
                            # AUTH KUDERT
                            token_kudert = kudert.login_kudert(email=credential.user_kudert,password=credential.pass_kudert)
                            #token_kudert['data']['token']
                            token_kudert = token_kudert['data']['token']
                            
                            # PRE - PROCESAMIENTO KUDERT
                            filtro_kudert = df_tracking_stages[df_tracking_stages['stage']=='KUDERT']
                            filtro_kudert = df_postulantes_complete[df_postulantes_complete['postulanteId'].isin(filtro_kudert['postulanteId'].to_list())]
                            
                            # REQUEST & PROCESAMIENTO KUDERT
                            
                            request_kudert = kudert.request_psicometricos(filtro_kudert,token_kudert=token_kudert)
                            # print(request_kudert)
                            print('\n# Nos encontramos agregando Caracterizticas descriptivas a los resultados, por favor espere...')            
                            request_kudert = kudert.traits_kudert_score(request_kudert)
                            print(request_kudert)
                            
                            #Save to csv
                            request_kudert.to_csv('data/kudertscore.csv',encoding='utf-8')
                            
                            # MENSAJE FINAL
                            print('\n# Listo! La vacante y las evaluaciones KUDERT')
                            break                      
                        else:
                            print('ERROR | opcion invalida, intentelo nuevamente...')
                            
                            # Mensaje exitoso de proceso terminado
                
                else:
                     print('\nLa vacante ha sido EXITOSAMENTE PROCESADA, los archivos han sido generados en LOCAL!')   
                
                print('\n Subiendo archivos a la Nube...')
                print('----------------------------------------------------------------------------')
                print('| Recuerda: Los archivos son actualizados para que el dashboard pueda      |')
                print('|           disponer de la informacion.                                    |')
                print('----------------------------------------------------------------------------')
                
                if os.path.isfile('data/postulantes_complete_dashboard_hr.csv'):
                    actualizar_cloud(file_name_cloud='postulantes_complete_dashboard_hr.csv',file_name_local='data/postulantes_complete_dashboard_hr.csv')    
                if os.path.isfile('data/historico_etapas.csv'):
                    actualizar_cloud(file_name_cloud='historico_etapas.csv',file_name_local='data/historico_etapas.csv')
                if os.path.isfile('data/preguntas_respondidas_db.csv'):
                    actualizar_cloud(file_name_cloud='preguntas_respondidas_db.csv',file_name_local='data/preguntas_respondidas_db.csv')
                if os.path.isfile('data/kudertscore.csv'):
                    actualizar_cloud(file_name_cloud='kudertscore.csv',file_name_local='data/kudertscore.csv')
                # FALTA Agregar el archivo MATCH KUDERT
                else:None
                
                time.sleep(1)
                # Elimina la carpeta data luego de subirlo a la nube
                shutil.rmtree('data')
                # 
                print('Se esta descargando su Plantilla en la carpeta "dashboard"')
                bajar_template_pb(nombre_archivo=str(vacantes.iloc[opcion]['client.compañia'])+'_'+str(vacantes.iloc[opcion]['nombre_vacante']))
                print('PROCESO EXITOSO! Actualice su Dashboard para finalizar!')
                sys.exit()
                
                # actualizar_nube = '' # incializando variable
                # while actualizar_nube!='n' or actualizar_nube!='n': # Bucle de Actualizacion CLOUD
                #     actualizar_nube = input('Desea Actualizar la NUBE para actualizar su Dashboard JOB Benchmarking?(Y/N): ')
                #     actualizar_nube = actualizar_nube.lower()
                #     if actualizar_nube == 'y':
                #         print('Actualizando archivos a Google Drive, espere por favor..')
                #         actualizar_cloud()
                #         print('Gracias, ya puede actualizar su JOB BENCHMARKING')
                #         sys.exit()
                #         # subimos a la nube
                #     if actualizar_nube == 'n':
                #         break
                #     print('Ingrese una opcion valida')
                
                break
            
            else:
                print('ERROR | opcion invalida, intentelo nuevamente...')
                # ELECCION
                
    else:
        print('ERROR | VACANTE NO VALIDA, INTENTELO NUEVAMENTE') 
        # ELECCION VACANTE
    #break


#%%
#
#%%
# =============================================================================
# SECCION PARA CONSULTAS TEST
# =============================================================================



# R5
#file_csv.Upload()


