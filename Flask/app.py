__author__ = 'Erick Cruz - 02/08/2022'

from dataclasses import replace
import locale
from datetime import date, datetime, timedelta
import json
from flask import Flask, jsonify, request
import pymongo
import requests

# setar locale para português
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

app = Flask(__name__)


@app.route('/ChatDB', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)

    intent = data['queryResult']['intent']['displayName']

    parametros = data['queryResult']['parameters']
    sessao = data['session']

    #   Tratamento do Lead para o DB Mongo
    client = pymongo.MongoClient(
        "mongodb+srv://mongoadmin:tARAmfaBjUxIJ7Bh@cluster0" +
        ".tfd36.mongodb.net/?retryWrites=true&w=majority")

    db = client.DBChat

    # Definir o Parametros para execução (Teste/Produtivo)
    for Parametros in db.Parameters.find():

        teste = Parametros['Teste']
        salva_elos = Parametros['SalvaElos']
        whatsteste = Parametros['whatsteste']
        increment = Parametros['whats_increment']

    # teste = "X"
    # salva_elos = "Não"
    # whatsteste = "11982362540"
    # 11982362539 --> ultimo tel usado no ELOS

    source = "Chat_via_WhatsApp"

    if teste is True:
        whatsnumber = whatsteste

    else:
        whatsnumber = sessao.split("+")[1]

    # Tratamentos das intents do Dialogflow
    if intent == "ConhecendoLEAD":

        print("VOCÊ ESTÁ NA ", intent, "NÚMERO: ",
              whatsnumber, "Deve salvar no ELOS: ", salva_elos)

        leadname = parametros['leadname']['name']

        print('leadname: ', leadname)
        print('WhatsApp: ', whatsnumber)
        print('Session: ', sessao)
        print('----- SOURCE ----->', source)

        dtCriaçao = datetime.now()

        db.tbLead.insert_many([
            {'whatsapp': whatsnumber, 'leadname': leadname, 'source': source,
                'dtCriação': dtCriaçao}
        ])

        print("SALVO NO MONGO")

#        colecao = db['tbLead']

        for ltLead in db.tbLead.find(
            {'whatsapp': whatsnumber}
        ):
            print(" ---->> VISÃO DA COLEÇÃO SALVA NO MONGO: ", ltLead)

        # SALVAR LEAD NO ELOS

        if salva_elos is True:

            url_update = "https://func-prd-leadpage-el-2.azurewebsites" + \
                ".net/api/espacolaser/pt-BR/SaveLead?code=" + \
                "dnhRoi7HtcRzJ1XRZ8JsYukJdKz6tY8LGVAxAYV0/e9PfQcQLIgNaw=="
            headers2 = {
                'Authorization': 'Basic MzU3MTQyNjY4MTE6QXhtMjgxOEA=',
                'Content-Type': 'application/json',
                'Cookie': 'Cookie_2=value'
            }

            # Prepara Payload para criar o LEAD
            payload2 = json.dumps({
                "id": None,
                "name": ltLead['leadname'],
                "email": "lead@whats.com",
                "phoneNumber": whatsnumber,
                "doc": "",
                "organizationalStructure": {
                    "Id": "243",
                    "FatherId": "379",
                    "Description": None,
                    "AddressLat": None,
                    "AddressLng": None,
                    "AppChannels": [
                        {
                                "channel": "ECM_BRA"
                        },
                        {
                            "channel": "LP_BRA"
                        },
                        {
                            "channel": "APP_AGE"
                        },
                        {
                            "channel": "ECM_SL_BRA"
                        },
                        {
                            "channel": "ECM_AGE"
                        }
                    ],
                    "Address": {
                        "PostalCode": "06460-030",
                        "Type": "Avenida",
                        "Description": "PIRACEMA",
                        "StateAbrev": "SP",
                        "City": "BARUERI",
                        "Neighborhood": "TAMBORÉ",
                        "Number": "669",
                        "Complement": "LOJA STB S401 D"
                    },
                    "SchedulerCalendarTime": [
                        {
                            "StartTime": "14:00",
                            "EndTime": "20:00",
                            "DaysOfWeek": [
                                0
                            ]
                        },
                        {
                            "StartTime": "10:00",
                            "EndTime": "22:00",
                            "DaysOfWeek": [
                                1,
                                2,
                                3,
                                4,
                                5,
                                6
                            ]
                        }
                    ],
                    "Phones": [
                        {
                            "Number": "+55 (11) 23971522",
                            "Type": "Commercial"
                        }
                    ],
                    "Resources": None,
                    "Emails": [
                        "tambore@espacolaser.com.br"
                    ],
                    "SchedulerResourceClassifier": 1,
                    "MaximumNumberOfDaysForScheduling": 30,
                    "Distance": 0
                },
                "status": 1,
                "isBlockToCall": True,
                "marketingDigitalBondId": None,
                "attendantId": None,
                "schedulingAttendantId": None,
                "indicatedByLead": None,
                "indicatedBy": None,
                "externalTrackingCode": None,
                "internalTrackingCode": None,
                "nextAvaliableDate": None,
                "UTM_Source": "INDIQUE_E_GANHE",
                "UTM_Medium": "MGM",
                "UTM_Campaign": "ELOVERS",
                "UTM_Content": "CHAT_VIA_WHATSAPP",
                "UTM_Term": None,
                "consentTerm": True,
                "indicateFriend": "true",
                "media": None,
                "mediaName": None,
                "gclid": None,
                "fingerPrint": None,
                "segmentation": None,
                "Schedule": None,
                "IsTermPending": True
            })

            # Atualizar LEAD no ELOS com dados da unidade
            response = requests.request(
                "POST", url_update, headers=headers2, data=payload2)

            print(">>>> Updated Lead Result ELOS: ", response.text)
            print("L-798 - JSON Update Lead: ", response.json())

            lead = response.json()['lead']

            print("Estrutura do Lead atualizada: ", lead)

            idLead = lead['Id']

            print("ESSE É O ID DO LEAD: ", idLead)

            # Update MongoDB com o ID do LEAD no ELOS
            db.tbLead.update_one({'whatsapp': whatsnumber},
                                 {'$set': {'IdLead': idLead}}
                                 )

        return jsonify({})

    elif intent == "IdentificandoUnidadesCEP":

        print("VOCÊ ESTÁ NA ", intent, "NÚMERO: ",
              whatsnumber, "Deve salvar no ELOS: ", salva_elos)

        paramcep = data['queryResult']['parameters']
        cep = paramcep['zip-code']

        # Transformando CEP em Latitude / Longitude - INICIO
        urlgoogle = "https://maps.googleapis.com" + \
            "/maps/api/geocode/json?address="
        googlekey = "&key=AIzaSyBpJYASshPjF0jZkbMMI1Gqgk2zQ0g88zw"

        loc_url = urlgoogle+cep+googlekey

        location = requests.request("GET", loc_url)

        latlng = location.json()['results'][0]['geometry']
        # Transformando CEP em Latitude / Longitude - FIM

        # PREPARA BUSCA DE UNIDADES
        lat = latlng['location']['lat']
        lng = latlng['location']['lng']
        code = "=dnhRoi7HtcRzJ1XRZ8JsYukJdKz6tY8LGVAxAYV0/e9PfQcQLIgNaw=="

        buscaunidades = "https://func-prd-leadpage-el-2.azurewebsites.net" + \
            "/api/espacolaser/pt-BR/GetEstablishments?" + \
            "attendant=&marketingDigitalBond=&skip=0&lat=" + \
            str(lat)+"&lng="+str(lng)+"&code"+code

        headerscep = {'Authorization': 'Basic MzU3MTQyNjY4MTE6QXhtMjgxOEA='}
        payloadcep = ""

        # CHAMA API PARA BUSCAR UNIDADES
        unidades = requests.request(
            "GET", buscaunidades, headers=headerscep, data=payloadcep)

        print("IdentificandoUnidadesCEP para o ", cep)

        lista_unid1 = unidades.json()['list'][0]['Description']
        lista_unid2 = unidades.json()['list'][1]['Description']
        lista_unid3 = unidades.json()['list'][2]['Description']
        lista_unid4 = unidades.json()['list'][3]['Description']
        lista_unid5 = unidades.json()['list'][4]['Description']

        id_unid1 = unidades.json()['list'][0]['Id']
        id_unid2 = unidades.json()['list'][1]['Id']
        id_unid3 = unidades.json()['list'][2]['Id']
        id_unid4 = unidades.json()['list'][3]['Id']
        id_unid5 = unidades.json()['list'][4]['Id']

        FatherId1 = unidades.json()['list'][0]['FatherId']
        FatherId2 = unidades.json()['list'][1]['FatherId']
        FatherId3 = unidades.json()['list'][2]['FatherId']
        FatherId4 = unidades.json()['list'][3]['FatherId']
        FatherId5 = unidades.json()['list'][4]['FatherId']

#       Atualizando Lead no MongoDB com dados de localização
        db.tbLead.update_one(
            {'whatsapp': whatsnumber},
            {'$set': {'lat': lat}}
        )

        db.tbLead.update_one(
            {'whatsapp': whatsnumber},
            {'$set': {'lng': lng}}
        )

        db.tbLead.update_one(
            {'whatsapp': whatsnumber},
            {'$set': {'idun1': id_unid1,
                      'FatherId1': FatherId1,
                      'unid1': lista_unid1,
                      'idun2': id_unid2,
                      'FatherId2': FatherId2,
                      'unid2': lista_unid2,
                      'idun3': id_unid3,
                      'FatherId3': FatherId3,
                      'unid3': lista_unid3,
                      'idun4': id_unid4,
                      'FatherId4': FatherId4,
                      'unid4': lista_unid4,
                      'idun5': id_unid5,
                      'FatherId5': FatherId5,
                      'unid5': lista_unid5}}
        )

        for ltLead in db.tbLead.find(
            {'whatsapp': whatsnumber}
        ).sort('dtCriação'):
            print(" ---- VISÃO DA COLEÇÃO SALVA NO MONGO: ", ltLead)

        #       Atualizando Lead no MongoDB com dados de localização - FIM

        reply = 'Perfeito... para o seu CEP '+cep + \
            ', encontramos as unidades abaixo prontas para lhe atender:\n ' + \
            '\n*1.* '+lista_unid1 + '\n' + \
            '\n*2.* '+lista_unid2 + '\n' + \
            '\n*3.* '+lista_unid3 + '\n' + \
            '\n*4.* '+lista_unid4 + '\n' + \
            '\n*5.* '+lista_unid5

        print("RESPOSTA PARA O WHATSAPP: ", reply)

        return jsonify({
            'fulfillmentText': reply
        })

    elif intent == "EscolhendoData":

        print("VOCÊ ESTÁ NA ", intent, "NÚMERO: ",
              whatsnumber, "Deve salvar no ELOS: ", salva_elos)

        # Salvando opção de unidade
        opcao_unidade = data['queryResult']['parameters']['unidade']

        db.tbLead.update_one(
            {'whatsapp': whatsnumber},
            {'$set': {'SelectedUnid': opcao_unidade}}
        )

        hj = date.today()

        # Definindo datas para ofertar
        dt_op1 = hj + timedelta(days=1)
        dt_op2 = hj + timedelta(days=2)
        dt_op3 = hj + timedelta(days=3)
        dt_op4 = hj + timedelta(days=4)
        dt_op5 = hj + timedelta(days=5)

        # Trasnformando data em String
        op1 = datetime.strftime(dt_op1, '%d/%m/%Y')
        op2 = datetime.strftime(dt_op2, '%d/%m/%Y')
        op3 = datetime.strftime(dt_op3, '%d/%m/%Y')
        op4 = datetime.strftime(dt_op4, '%d/%m/%Y')
        op5 = datetime.strftime(dt_op5, '%d/%m/%Y')

        # Definindo dias da semana das datas à ofertar
        ds1 = dt_op1.weekday()

        if ds1 == 0:

            of1 = "*SEGUNDA-FEIRA* - "+op1
            of2 = "*TERÇA-FEIRA*   - "+op2
            of3 = "*QUARTA-FEIRA*  - "+op3
            of4 = "*QUINTA-FEIRA*  - "+op4
            of5 = "*SEXTA-FEIRA*   - "+op5

        elif ds1 == 1:

            of1 = "*TERÇA-FEIRA*  - "+op1
            of2 = "*QUARTA-FEIRA* - "+op2
            of3 = "*QUINTA-FEIRA* - "+op3
            of4 = "*SEXTA-FEIRA*  - "+op4
            of5 = "*SÁBADO*       - "+op5

        elif ds1 == 2:

            of1 = "*QUARTA-FEIRA* - "+op1
            of2 = "*QUINTA-FEIRA* - "+op2
            of3 = "*SEXTA-FEIRA*  - "+op3
            of4 = "*SÁBADO*       - "+op4
            of5 = "*DOMINGO*      - "+op5

        elif ds1 == 3:

            of1 = "*QUINTA-FEIRA*  - "+op1
            of2 = "*SEXTA-FEIRA*   - "+op2
            of3 = "*SÁBADO*        - "+op3
            of4 = "*DOMINGO*       - "+op4
            of5 = "*SEGUNDA-FEIRA* - "+op5

        elif ds1 == 4:

            of1 = "*SEXTA-FEIRA*   - "+op1
            of2 = "*SÁBADO*        - "+op2
            of3 = "*DOMINGO*       - "+op3
            of4 = "*SEGUNDA-FEIRA* - "+op4
            of5 = "*TERÇA-FEIRA*   - "+op5

        elif ds1 == 5:

            of1 = "*SÁBADO*        - "+op1
            of2 = "*DOMINGO*       - "+op2
            of3 = "*SEGUNDA-FEIRA* - "+op3
            of4 = "*TERÇA-FEIRA*   - "+op4
            of5 = "*QUARTA-FEIRA*  - "+op5

        else:

            of1 = "*DOMINGO*       - "+op1
            of2 = "*SEGUNDA-FEIRA* - "+op2
            of3 = "*TERÇA-FEIRA*   - "+op3
            of4 = "*QUARTA-FEIRA*  - "+op4
            of5 = "*QUINTA-FEIRA*  - "+op5

        print("..>>>> DATA: ", of1, ":-D")

        reply = "Legal, agora me fala qual seria a melhor data para " + \
            "agendarmos a sua avaliação:\n" + \
            '\n' + of1 + \
            '\n' + of2 + \
            '\n' + of3 + \
            '\n' + of4 + \
            '\n' + of5 + '\n' + \
            "\nVocê também pode me digitar *outra data* se lhe atender melhor"

        return jsonify({
            'fulfillmentText': reply
        })

    elif intent == "EscolhendoHorario":

        print("VOCÊ ESTÁ NA ", intent, "NÚMERO: ",
              whatsnumber, "Deve salvar no ELOS: ", salva_elos)

        dt = data['queryResult']['parameters']['dt']

        db.tbLead.update_one(
            {'whatsapp': whatsnumber},
            {'$set': {'dt_agenda': dt}}
        )

        for ltLead in db.tbLead.find(
            {'whatsapp': whatsnumber}
        ).sort('dtCriação', -1):
            print(" ---- VISÃO DA COLEÇÃO SALVA NO MONGO: ", ltLead)

        opcao_unidade = ltLead['SelectedUnid']

        if salva_elos is True:
            idLead = ltLead['IdLead']

        else:
            idLead = "18569919"

        if opcao_unidade == "1":

            unid_selecionada = ltLead['idun1']
            unidade = ltLead['unid1']

        elif opcao_unidade == "2":

            unid_selecionada = ltLead['idun2']
            unidade = ltLead['unid2']

        elif opcao_unidade == "3":

            unid_selecionada = ltLead['idun3']
            unidade = ltLead['unid3']

        elif opcao_unidade == "4":

            unid_selecionada = ltLead['idun4']
            unidade = ltLead['unid4']

        elif opcao_unidade == "5":

            unid_selecionada = ltLead['idun5']
            unidade = ltLead['unid5']

        else:

            print("Não foi possível identificar a opção")

            return jsonify({'fulfillmentText': "Não foi possível" +
                            "identificar a opção,por favor digite o" +
                            "número que representa a unidade desejada."})

        if unid_selecionada:

            db.tbLead.update_one(
                {'whatsapp': whatsnumber},
                {'$set': {'unidade': unidade}}
            )

            # Definições para busca de horários
            url_hora = "https://func-prd-leadpage-el-2.azurewebsites.net" + \
                "/api/espacolaser/pt-BR/GetAvaliableTimes?" + \
                "code=dnhRoi7HtcRzJ1XRZ8JsYukJdKz6tY8LGVAxAYV0/e9PfQcQLIgNaw=="
            headers = {
                'Authorization': 'Basic MzU3MTQyNjY4MTE6QXhtMjgxOEA=',
                'Content-Type': 'application/json',
                'Cookie': 'Cookie_2=value'
            }

            payload = json.dumps({
                "lead": {
                    "id": idLead,
                    "name": ltLead['leadname'],
                    "email": None,
                    "phoneNumber": whatsnumber,
                    "doc": None,
                    "organizationalStructure": {
                        "Id": unid_selecionada,
                        "Description": None,
                        "AddressLat": None,
                        "AddressLng": None,
                        "Address": None,
                        "SchedulerCalendarTime": None
                    },
                    "status": 1,
                    "isBlockToCall": True,
                    "marketingDigitalBondId": None,
                    "attendantId": None,
                    "schedulingAttendantId": None,
                    "indicatedByLead": None,
                    "indicatedBy": None,
                    "externalTrackingCode": None,
                    "internalTrackingCode": None,
                    "nextAvaliableDate": "2022-08-23T03:00:00.000Z",
                    "UTM_Source": None,
                    "UTM_Medium": None,
                    "UTM_Campaign": None,
                    "UTM_Content": None,
                    "UTM_Term": None,
                    "consentTerm": True,
                    "indicateFriend": "true",
                    "media": None,
                    "mediaName": None,
                    "gclid": None,
                    "fingerPrint": None,
                    "segmentation": None,
                    "schedulerSuggestionInterval": 30
                },
                "date": dt,
                "morning": True,
                "afternoon": True,
                "night": True
            })

            # "date": "2022-08-30T03:00:00.000Z"

            response = requests.request(
                "POST", url_hora, headers=headers, data=payload)

            print(">>> RETORNO DA API DE HORÁRIO:")
            print(response.text)
            print(">>> RETORNO DA API DE HORÁRIO - FIM")

            agenda1 = response.json()['times'][0]
            agenda2 = response.json()['times'][1]
            agenda3 = response.json()['times'][2]
            agenda4 = response.json()['times'][3]
            agenda5 = response.json()['times'][4]
            agenda6 = response.json()['times'][5]
            agenda7 = response.json()['times'][6]
            agenda8 = response.json()['times'][7]
            agenda9 = response.json()['times'][8]

            dtagend = agenda1.split("T")[0]
            hora1 = agenda1.split("T")[1]
            hora2 = agenda2.split("T")[1]
            hora3 = agenda3.split("T")[1]
            hora4 = agenda4.split("T")[1]
            hora5 = agenda5.split("T")[1]
            hora6 = agenda6.split("T")[1]
            hora7 = agenda7.split("T")[1]
            hora8 = agenda8.split("T")[1]
            hora9 = agenda9.split("T")[1]

            db.tbLead.update_one(
                {'whatsapp': whatsnumber},
                {'$set': {'dtagenda': dtagend, 'hora1': hora1,
                          'hora2': hora2, 'hora3': hora3,
                          'hora4': hora4, 'hora5': hora5,
                          'hora6': hora6, 'hora7': hora7,
                          'hora8': hora8, 'hora9': hora9
                          }}
            )

            for ltLead in db.tbLead.find(
                    {'whatsapp': whatsnumber}).sort('dtCriação', -1):
                print(" ---- VISÃO DA COLEÇÃO SALVA NO MONGO: ", ltLead)

            dt_agenda = dtagend.split(
                "-")[2]+"/"+dtagend.split("-")[1]+"/"+dtagend.split("-")[0]

            reply = "Sem problemas nenhum, na unidade " + \
                "*"+ltLead['unid1']+"*" + \
                    " temos os seguintes horários disponíveis para o dia " + \
                '*'+dt_agenda+'*\n' + \
                '\n*1.* ' + hora1.split(":")[0] + \
                "h"+hora1.split(":")[1] + '\n' + \
                '\n*2.* ' + hora2.split(":")[0] + \
                "h"+hora2.split(":")[1] + '\n' + \
                '\n*3.* ' + hora3.split(":")[0] + \
                "h"+hora3.split(":")[1] + '\n' + \
                '\n*4.* ' + hora4.split(":")[0] + \
                "h"+hora4.split(":")[1] + '\n' + \
                '\n*5.* ' + hora5.split(":")[0] + \
                "h"+hora5.split(":")[1] + '\n' + \
                '\n*6.* ' + hora6.split(":")[0] + \
                "h"+hora6.split(":")[1] + '\n' + \
                '\n*7.* ' + hora7.split(":")[0] + \
                "h"+hora7.split(":")[1] + '\n' + \
                '\n*8.* ' + hora8.split(":")[0] + \
                "h"+hora8.split(":")[1] + '\n' + \
                '\n*9.* ' + hora9.split(":")[0] + \
                "h"+hora9.split(":")[1] + '\n'

            # Defini se deve salvar os dados da unidade no ELOS
            if salva_elos is True:

                # DEFININDO DADOS DA UNIDADE PARA ATUALIZAR O LEAD
                AddressLat = ltLead['lat']
                AddressLng = ltLead['lng']

                if ltLead['SelectedUnid'] == "1":

                    Id = ltLead['idun1']
                    FatherId = ltLead['FatherId1']
                    Description = ltLead['unid1']

                elif ltLead['SelectedUnid'] == "2":

                    Id = ltLead['idun2']
                    FatherId = ltLead['FatherId2']
                    Description = ltLead['unid2']

                elif ltLead['SelectedUnid'] == "3":

                    Id = ltLead['idun3']
                    FatherId = ltLead['FatherId3']
                    Description = ltLead['unid3']

                elif ltLead['SelectedUnid'] == "4":

                    Id = ltLead['idun4']
                    FatherId = ltLead['FatherId4']
                    Description = ltLead['unid4']

                elif ltLead['SelectedUnid'] == "5":

                    Id = ltLead['idun5']
                    FatherId = ltLead['FatherId5']
                    Description = ltLead['unid5']

                else:

                    print("NÃO FOI POSSÍVEL DEFINIR UNIDADE SELECIONADA!")

                    reply = "Não foi possível determinar a unidade" +\
                            " selecionada, me informe o seu CEP novamente" + \
                            " por favor"

                    return jsonify({
                        'fulfillmentText': reply
                    })

                url_update = "https://func-prd-leadpage-el-2.azurewebsites" + \
                    ".net/api/espacolaser/pt-BR/SaveLead?code=" + \
                    "dnhRoi7HtcRzJ1XRZ8JsYukJdKz6tY8LGVAxAYV0/e9PfQcQLIgNaw=="

                headers2 = {
                    'Authorization': 'Basic MzU3MTQyNjY4MTE6QXhtMjgxOEA=',
                    'Content-Type': 'application/json',
                    'Cookie': 'Cookie_2=value'
                }

                # Prepara Payload para Update Lead - Dados da Unidade
                payload2 = json.dumps({
                    "id": ltLead['IdLead'],
                    "name": ltLead['leadname'],
                    "email": "lead@whats.com",
                    "phoneNumber": whatsnumber,
                    "doc": "",
                    "organizationalStructure": {
                        "Id": Id,
                        "FatherId": FatherId,
                        "Description": Description,
                        "AddressLat": AddressLat,
                        "AddressLng": AddressLng,
                        "AppChannels": [
                            {
                                "channel": "ECM_BRA"
                            },
                            {
                                "channel": "LP_BRA"
                            },
                            {
                                "channel": "APP_AGE"
                            },
                            {
                                "channel": "ECM_SL_BRA"
                            },
                            {
                                "channel": "ECM_AGE"
                            }
                        ],
                        "Address": {
                            "PostalCode": "06460-030",
                            "Type": "Avenida",
                            "Description": "PIRACEMA",
                            "StateAbrev": "SP",
                            "City": "BARUERI",
                            "Neighborhood": "TAMBORÉ",
                            "Number": "669",
                            "Complement": "LOJA STB S401 D"
                        },
                        "SchedulerCalendarTime": [
                            {
                                "StartTime": "14:00",
                                "EndTime": "20:00",
                                "DaysOfWeek": [
                                    0
                                ]
                            },
                            {
                                "StartTime": "10:00",
                                "EndTime": "22:00",
                                "DaysOfWeek": [
                                    1,
                                    2,
                                    3,
                                    4,
                                    5,
                                    6
                                ]
                            }
                        ],
                        "Phones": [
                            {
                                "Number": "+55 (11) 23971522",
                                "Type": "Commercial"
                            }
                        ],
                        "Resources": None,
                        "Emails": [
                            "tambore@espacolaser.com.br"
                        ],
                        "SchedulerResourceClassifier": 1,
                        "MaximumNumberOfDaysForScheduling": 30,
                        "Distance": 0
                    },
                    "status": 1,
                    "isBlockToCall": True,
                    "marketingDigitalBondId": None,
                    "attendantId": None,
                    "schedulingAttendantId": None,
                    "indicatedByLead": None,
                    "indicatedBy": None,
                    "externalTrackingCode": None,
                    "internalTrackingCode": None,
                    "nextAvaliableDate": None,
                    "UTM_Source": "INDIQUE_E_GANHE",
                    "UTM_Medium": "MGM",
                    "UTM_Campaign": "ELOVERS",
                    "UTM_Content": "CHAT_VIA_WHATSAPP",
                    "UTM_Term": None,
                    "consentTerm": True,
                    "indicateFriend": "true",
                    "media": None,
                    "mediaName": None,
                    "gclid": None,
                    "fingerPrint": None,
                    "segmentation": None,
                    "Schedule": None,
                    "IsTermPending": True
                })

                # Atualizar LEAD no ELOS com dados da unidade
                response = requests.request(
                    "POST", url_update, headers=headers2, data=payload2)

                print(">>>> Updated Lead Result ELOS: ", response.text)

                lead = response.json()['lead']

                idLead = lead['Id']

                print("ATUALIZAÇÃO CONCLUÍDA PARA ID_LEAD: ", idLead)

            return jsonify({
                'fulfillmentText': reply
            })

        else:

            print("Não foi possível identificar a opção")

            return jsonify({'fulfillmentText': "Não foi possível" +
                            "identificar a opção,por favor digite o" +
                            "número que representa a unidade desejada."})

    elif intent == "FinalizandoAgenda":

        print("VOCÊ ESTÁ NA ", intent, "NÚMERO: ",
              whatsnumber, "Deve salvar no ELOS: ", salva_elos)

        opcao_horario = data['queryResult']['parameters']['agenda']

        # Update MongoDB com opção de horário selecionada
        db.tbLead.update_one({'whatsapp': whatsnumber},
                             {'$set': {'SelectedAgend': opcao_horario}}
                             )

        # Seleciona histórico do chat do usuário
        for ltLead in db.tbLead.find(
                {'whatsapp': whatsnumber}).sort('dtCriação', 1):
            print(" ---- VISÃO DA COLEÇÃO SALVA NO MONGO: ", ltLead)

            dt_agenda_ini = ltLead['dtagenda']

            dt_agenda = dt_agenda_ini.split(
                "-")[2]+"/"+dt_agenda_ini.split("-")[1] + \
                "/"+dt_agenda_ini.split("-")[0]

            print("DATA DE AGENDA: ", dt_agenda)

            # DEFININDO DADOS DA AGENDA PARA EFETIVAR O AGENDAMENTO
            if opcao_horario == 1.0:

                hr = ltLead['hora1']
                h_formt = hr.split(":")[0]+":"+hr.split(":")[1]

                hora_agenda = ltLead['dtagenda']+"T"+ltLead['hora1']

                print("AGENDA PARA ELOS-1: ", hora_agenda)

            elif opcao_horario == 2.0:

                hr = ltLead['hora2']
                h_formt = hr.split(":")[0]+":"+hr.split(":")[1]

                hora_agenda = ltLead['dtagenda']+"T"+ltLead['hora2']

                print("AGENDA PARA ELOS-2: ", hora_agenda)

            elif opcao_horario == 3.0:

                hr = ltLead['hora3']
                h_formt = hr.split(":")[0]+":"+hr.split(":")[1]

                hora_agenda = ltLead['dtagenda']+"T"+ltLead['hora3']

                print("AGENDA PARA ELOS-3: ", hora_agenda)

            elif opcao_horario == 4.0:

                hr = ltLead['hora4']
                h_formt = hr.split(":")[0]+":"+hr.split(":")[1]

                hora_agenda = ltLead['dtagenda']+"T"+ltLead['hora4']

                print("AGENDA PARA ELOS-4: ", hora_agenda)

            elif opcao_horario == 5.0:

                hr = ltLead['hora5']
                h_formt = hr.split(":")[0]+":"+hr.split(":")[1]

                hora_agenda = ltLead['dtagenda']+"T"+ltLead['hora5']

                print("AGENDA PARA ELOS-5: ", hora_agenda)

            elif opcao_horario == 6.0:

                hr = ltLead['hora6']
                h_formt = hr.split(":")[0]+":"+hr.split(":")[1]

                hora_agenda = ltLead['dtagenda']+"T"+ltLead['hora6']

                print("AGENDA PARA ELOS-6: ", hora_agenda)

            elif opcao_horario == 7.0:

                hr = ltLead['hora7']
                h_formt = hr.split(":")[0]+":"+hr.split(":")[1]

                hora_agenda = ltLead['dtagenda']+"T"+ltLead['hora7']

                print("AGENDA PARA ELOS-7: ", hora_agenda)

            elif opcao_horario == 8.0:

                hr = ltLead['hora8']
                h_formt = hr.split(":")[0]+":"+hr.split(":")[1]

                hora_agenda = ltLead['dtagenda']+"T"+ltLead['hora8']

                print("AGENDA PARA ELOS-8: ", hora_agenda)

            elif opcao_horario == 9.0:

                hr = ltLead['hora9']
                h_formt = hr.split(":")[0]+":"+hr.split(":")[1]

                hora_agenda = ltLead['dtagenda']+"T"+ltLead['hora9']

                print("AGENDA PARA ELOS-9: ", hora_agenda)

            else:

                print("NÃO FOI POSSÍVEL IDENTIFICAR HORÁRIO PARA AGENDAMENTO!")

            # Update MongoDB com a Agenda definida
            agenda = dt_agenda+" - "+h_formt

            db.tbLead.update_one({'whatsapp': whatsnumber},
                                 {'$set': {'Agenda': agenda}}
                                 )

            # Ajusta o número de teste de acordo com Parameters
            new_whats_teste = whatsnumber + increment

            db.Parameters.update_one({'whatsapp': whatsnumber},
                                     {'$set': {'whatsapp': new_whats_teste}}
                                     )

            print("***--->>> OS DADOS SERÃO SALVOS NO ELOS: ", salva_elos)

            if salva_elos is True:

                lead = response.json()['lead']
                idLead = lead['Id']

                url_ag = "https://func-prd-leadpage-el-2.azurewebsites" + \
                    ".net/api/espacolaser/pt-BR/DoSchedule?code=" + \
                    "dnhRoi7HtcRzJ1XRZ8JsYukJdKz6tY8LGVAxAYV0/e9PfQcQLIgNaw=="
                headers3 = {
                    'Authorization': 'Basic MzU3MTQyNjY4MTE6QXhtMjgxOEA=',
                    'Content-Type': 'application/json',
                    'Cookie': 'Cookie_2=value'
                }

                print("ESSE É O ID DO LEAD: ", idLead)

                # Realizar Agendamento para o LEAD
                payload3 = json.dumps({
                    "lead": {
                        "id": idLead,
                        "name": ltLead['leadname'],
                        "email": None,
                        "phoneNumber": whatsnumber,
                        "doc": None,
                        "organizationalStructure": {
                            "Id": ltLead['idun1'],
                            "Description": ltLead['unid1'],
                            "AddressLat": None,
                            "AddressLng": None,
                            "Address": None,
                            "SchedulerCalendarTime": None
                        },
                        "status": 1,
                        "isBlockToCall": True,
                        "marketingDigitalBondId": None,
                        "attendantId": None,
                        "schedulingAttendantId": None,
                        "indicatedByLead": None,
                        "indicatedBy": None,
                        "externalTrackingCode": None,
                        "internalTrackingCode": None,
                        "nextAvaliableDate": "2022-08-23T03:00:00.000Z",
                        "UTM_Source": None,
                        "UTM_Medium": None,
                        "UTM_Campaign": None,
                        "UTM_Content": None,
                        "UTM_Term": None,
                        "consentTerm": True,
                        "indicateFriend": "true",
                        "media": None,
                        "mediaName": None,
                        "gclid": None,
                        "fingerPrint": None,
                        "segmentation": None,
                        "schedulerSuggestionInterval": 30
                    },
                    "date": hora_agenda
                })

                # Criar Agenda para o LEAD no ELOS
                response = requests.request(
                    "POST", url_ag, headers=headers3, data=payload3)

                print("RETORNO DA SCHEDULE ELOS: ", response.text)

                result_sch = response.json()['error']

                if result_sch is False:

                    # Update MongoDB com o ID do LEAD no ELOS
                    db.tbLead.update_one({'whatsapp': whatsnumber},
                                         {'$set': {'ag_error': result_sch}}
                                         )

                    reply = "Parabéns, *"+ltLead['leadname'] + \
                        "* seu agendamento foi realizado com sucesso na *" + \
                        Description+"* na data *"+dt_agenda + \
                        "* às *"+h_formt + \
                        "*"+"\n\nNos vemos em breve! :-D"

                    print("VERIFICAR RETORNO", reply)

                    return jsonify({'fulfillmentText': reply})

                else:

                    # Update MongoDB com o ID do LEAD no ELOS
                    db.tbLead.update_one({'whatsapp': whatsnumber},
                                         {'$set': {'IdLead': idLead,
                                                   'ag_error': result_sch}}
                                         )

                    reply = "Infelizmente o horário selecionado já foi" +\
                        "utilizado, por favor selecione um novo horário" +\
                        "para efetivar o seu agendamento:"

                    print("VERIFICAR RETORNO", reply)

                    return jsonify({'fulfillmentText': reply})

            else:

                reply = "Parabéns, *"+ltLead['leadname'] + \
                    "* seu agendamento foi realizado com sucesso na *" + \
                    Description+"* na data *"+dt_agenda+"* às *" + \
                    h_formt+"*\n" + \
                    "\nNos vemos em breve! :-D"

                print("VERIFICAR RETORNO", reply)

                return jsonify({'fulfillmentText': reply})

    elif intent == "Default Fallback Intent":

        print("VOCÊ ESTÁ NA ", intent, "NÚMERO: ",
              whatsnumber, "Deve salvar no ELOS: ", salva_elos)

        print(data)

        return jsonify({})

    elif intent == "Default Welcome Intent":

        print("VOCÊ ESTÁ NA ", intent, "NÚMERO: ", whatsnumber)

#        ltLead = db.tbLead.find({'whatsapp': whatsnumber})

        try:

            for ltLead in db.tbLead.find(
                    {'whatsapp': whatsnumber}).sort('dtCriação'):
                print("Reultado da Leitura do MongoDB: ", ltLead)

            dt_agenda = ltLead['Agenda']
            unidade = ltLead['unidade']

            print("LEAD AGENDADO")

            reply = "Olá, *"+ltLead['leadname']+"*, me chamo MEL!" + \
                " \n\nSou a assistente virtual da Espaçolaser. " + \
                "\nVerifiquei aqui que você já possuí uma agenda " + \
                " na unidade *"+unidade+"* na data: *" + \
                dt_agenda+"* para sua avaliação!\n" + \
                "\n Me diga como posso lhe ajudar!"

            return jsonify({'fulfillmentText': reply})

        except Exception:
            print("LEAD NÃO CADASTRADO")

            return jsonify({})

    elif intent == "QueroReagendar - yes":

        print("VOCÊ ESTÁ NA ", intent, "NÚMERO: ",
              whatsnumber, "Deve salvar no ELOS: ", salva_elos)

        for ltLead in db.tbLead.find(
                {'whatsapp': whatsnumber}).sort('dtCriação'):

            unidade = ltLead['unidade']

        hj = date.today()

        # Definindo datas para ofertar
        dt_op1 = hj + timedelta(days=1)
        dt_op2 = hj + timedelta(days=2)
        dt_op3 = hj + timedelta(days=3)
        dt_op4 = hj + timedelta(days=4)
        dt_op5 = hj + timedelta(days=5)

        # Trasnformando data em String
        op1 = datetime.strftime(dt_op1, '%d/%m/%Y')
        op2 = datetime.strftime(dt_op2, '%d/%m/%Y')
        op3 = datetime.strftime(dt_op3, '%d/%m/%Y')
        op4 = datetime.strftime(dt_op4, '%d/%m/%Y')
        op5 = datetime.strftime(dt_op5, '%d/%m/%Y')

        # Definindo dias da semana das datas à ofertar
        ds1 = dt_op1.weekday()

        if ds1 == 0:

            of1 = "*SEGUNDA-FEIRA* - "+op1
            of2 = "*TERÇA-FEIRA*   - "+op2
            of3 = "*QUARTA-FEIRA*  - "+op3
            of4 = "*QUINTA-FEIRA*  - "+op4
            of5 = "*SEXTA-FEIRA*   - "+op5

        elif ds1 == 1:

            of1 = "*TERÇA-FEIRA*  - "+op1
            of2 = "*QUARTA-FEIRA* - "+op2
            of3 = "*QUINTA-FEIRA* - "+op3
            of4 = "*SEXTA-FEIRA*  - "+op4
            of5 = "*SÁBADO*       - "+op5

        elif ds1 == 2:

            of1 = "*QUARTA-FEIRA* - "+op1
            of2 = "*QUINTA-FEIRA* - "+op2
            of3 = "*SEXTA-FEIRA*  - "+op3
            of4 = "*SÁBADO*       - "+op4
            of5 = "*DOMINGO*      - "+op5

        elif ds1 == 3:

            of1 = "*QUINTA-FEIRA*  - "+op1
            of2 = "*SEXTA-FEIRA*   - "+op2
            of3 = "*SÁBADO*        - "+op3
            of4 = "*DOMINGO*       - "+op4
            of5 = "*SEGUNDA-FEIRA* - "+op5

        elif ds1 == 4:

            of1 = "*SEXTA-FEIRA*   - "+op1
            of2 = "*SÁBADO*        - "+op2
            of3 = "*DOMINGO*       - "+op3
            of4 = "*SEGUNDA-FEIRA* - "+op4
            of5 = "*TERÇA-FEIRA*   - "+op5

        elif ds1 == 5:

            of1 = "*SÁBADO*        - "+op1
            of2 = "*DOMINGO*       - "+op2
            of3 = "*SEGUNDA-FEIRA* - "+op3
            of4 = "*TERÇA-FEIRA*   - "+op4
            of5 = "*QUARTA-FEIRA*  - "+op5

        else:

            of1 = "*DOMINGO*       - "+op1
            of2 = "*SEGUNDA-FEIRA* - "+op2
            of3 = "*TERÇA-FEIRA*   - "+op3
            of4 = "*QUARTA-FEIRA*  - "+op4
            of5 = "*QUINTA-FEIRA*  - "+op5

        reply = "Legal, agora me fala qual seria a melhor data para " + \
            "agendarmos a sua avaliação na unidade *: "+unidade + \
            '*\n\n' + of1 + \
            '\n' + of2 + \
            '\n' + of3 + \
            '\n' + of4 + \
            '\n' + of5 + '\n' + \
            "\nVocê também pode me digitar *outra data* se lhe atender melhor"

        return jsonify({'fulfillmentText': reply})

    elif intent == "QueroReagendar - no":

        print("VOCÊ ESTÁ NA ", intent, "NÚMERO: ",
              whatsnumber, "Deve salvar no ELOS: ", salva_elos)

        for ltLead in db.tbLead.find(
                {'whatsapp': whatsnumber}).sort('dtCriação'):

            reply = "Sem problemas, *"+ltLead['leadname'] + \
                "* me informe seu *CEP* para lhe mostrar as" + \
                " unidades mais próximas."

        return jsonify({'fulfillmentText': reply})
