"""
Created on Tue Aug 18 14:56:33 2020

@author: César Cortez
"""

# -*- coding: utf-8 -*-
import os, sys
from dominum import hr_dominum, kudert
from cred import credential
import pandas as pd
import time
import shutil


### SCRIPT CONSOLA | USUARIO
print('#########################################################')
print('DASHBOARD HR 1.0 | Bienvenido al modulo de actualización')
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
    data = hr_dominum.login_hiring_room(client_secret=credential.client_secret_hr,user=credential.user_hr,password=credential.pass_hr)
    vacantes = hr_dominum.obtener_vacante(token=data['token'])
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
                
                try:
                    postulantes = hr_dominum.obtener_postulante(token=data['token'],vacante_postulantes=vacantes.iloc[opcion]['idVacante'])
                except:
                    print('Error con las credenciales de HR')
                    
                try:
                    df_postulantes_complete = postulantes.merge(vacantes,on=['idVacante']) # merge
                    df_postulantes_complete = hr_dominum.procesar(df_postulantes_complete)
                    df_postulantes_complete.to_csv('data/postulantes_complete_dashboard_hr.csv',encoding='utf-8') # save CSV
                except:
                    print('No hay datos a procesar o error de conectividad')
                
                
                # Procesando comentarios
                print('\n# Ahora procesamos las respuestas de nuestros postulantes, por favor espere...')            
                try:
                    df_comentarios_general = hr_dominum.request_comentario(token=data['token'],df_idpost_idvac=df_postulantes_complete[['postulanteId','idVacante']])
                    df_comentarios_general.to_csv('data/preguntas_respondidas_db.csv',encoding='utf-8') # save CSV
                except:
                    print('No hay datos a procesar o error de conectividad')
                # Procesando EL TRACKING DEL POSTULANTE
                
                
                print('\n# Ahora nos encontramos procesando los datos necesarios para el Funnel de la Vacante, por favor espere...')
                try:
                    df_records = hr_dominum.obtener_records(token=data['token'],postulantes_id_list=df_postulantes_complete['postulanteId'])
                    df_tracking_stages = hr_dominum.tracking_user_way(df_postulantes_complete=df_postulantes_complete,df_record_total=df_records,token=data['token'])
                    df_tracking_stages.to_csv('data/historico_etapas.csv',encoding='utf-8') # save CSV
                except:
                    print("Parece que hubo un error al procesar el Funnel. Verifique que existen postulantes en la vacante selecciona")
                # Mensaje exitoso de proceso terminado
                
                try:
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
                                print('\n Usted eligió no procesar los test Kudert, sus archivos en local estan listos!')
                                break
                            
                            if si_no=='y':
                                print('\n# Genial! ya estamos procesando las evaluaciones Kudert  >>'+vacantes.iloc[opcion]['nombre_vacante']+'<< ,esto puede tomar unos minutos, por favor espere...')
                                print('----------------------------------------------------------------------------')
                                print('| OJO: Solo se procesan los test Completados al 100%                       |')
                                print('----------------------------------------------------------------------------')
               
                                # AUTH KUDERT
                                token_kudert = kudert.login_kudert(email=credential.user_kudert,password=credential.pass_kudert)
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
                except:
                    print("Hubo en error al cargar modulo Kudert")
                    
                
                print('\n Subiendo archivos a la Nube...')
                print('----------------------------------------------------------------------------')
                print('| Recuerda: Los archivos son actualizados para que el dashboard pueda      |')
                print('|           disponer de la informacion.                                    |')
                print('----------------------------------------------------------------------------')
                
                
                try:
                    if os.path.isfile('data/postulantes_complete_dashboard_hr.csv'):
                        hr_dominum.actualizar_cloud(file_name_cloud='postulantes_complete_dashboard_hr.csv',file_name_local='data/postulantes_complete_dashboard_hr.csv')    
                    if os.path.isfile('data/historico_etapas.csv'):
                        hr_dominum.actualizar_cloud(file_name_cloud='historico_etapas.csv',file_name_local='data/historico_etapas.csv')
                    if os.path.isfile('data/preguntas_respondidas_db.csv'):
                        hr_dominum.actualizar_cloud(file_name_cloud='preguntas_respondidas_db.csv',file_name_local='data/preguntas_respondidas_db.csv')
                    if os.path.isfile('data/kudertscore.csv'):
                        hr_dominum.actualizar_cloud(file_name_cloud='kudertscore.csv',file_name_local='data/kudertscore.csv')
                    # FALTA Agregar el archivo MATCH KUDERT
                    else:None
                except:
                    print("Hubo un error al cargar datos a Google Cloud, verique su conexi")
                
                    
                
                time.sleep(1)
                # Elimin a la carpeta data luego de subirlo a la nube
                shutil.rmtree('data')
                # 
                print('Se esta descargando su Plantilla en la carpeta "dashboard"')
                try:
                    hr_dominum.bajar_template_pb(nombre_archivo=str(vacantes.iloc[opcion]['client.compañia'])+'_'+str(vacantes.iloc[opcion]['nombre_vacante']))
                    print('PROCESO EXITOSO! Actualice su Dashboard para finalizar!')
                    sys.exit()
                except:
                    print('Parece que Hubo un error: El template con el nombre del puesto ya existe o hay un error de conectividad')
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



