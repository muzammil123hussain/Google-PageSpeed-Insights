import csv
import json
from os import sep
import time

import requests


class WebsiteAudit():

    def __init__(self, csv_path):
        self.url_datasets = []
        self.messages = []
        self.__read_file(csv_path)
    

    def __read_file(self, csv_path):
        with open(csv_path) as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                google_speedtest_api = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={row[0]}&strategy={row[1]}'
                
                dataset = { 'url' : google_speedtest_api,
                    'response' : None,
                    'score' : 0,
                    'device' : None
                    }

                self.url_datasets.append(dataset)


    def __calculate_score(self, response):
        return int (response['lighthouseResult']['categories']['performance']['score'] * 100)

    def __check_device(self, response):
        return str (response['lighthouseResult']['configSettings']['formFactor'])

    def __trim_url(self, response):
        return str (response['id'])


    def __report(self,message):
        WEBHOOK_URL = "https://hooks.slack.com/services/you_slack_chanel_token"
        response = requests.post(
            WEBHOOK_URL, json={'text': str(message)},
            headers={'Content-Type': 'application/json'} )
        print(message)
        return response

    def audit(self):
        slack_msg = ""
        for dataset in self.url_datasets:
            is_success = True
            while (is_success):
                time.sleep(5)
                response = requests.get(dataset['url'])
                code = response.status_code
                if code == 429:
                    continue
                else:
                    is_success = False
                    dataset['response'] = response.json()
                    dataset['url'] = self.__trim_url(dataset['response'])
                    dataset['score'] = self.__calculate_score(dataset['response'])
                    dataset['device'] = self.__check_device(dataset['response'])
                    #print ( dataset['device'] , dataset['score'] )
                    if dataset['device'] == 'mobile' and dataset['score'] < 50:
                        slack_msg += f"{dataset['url']}  {dataset['score']}  {dataset['device']} \n"
                    elif dataset['device'] == 'desktop' and dataset['score'] < 75:
                        slack_msg += f"{dataset['url']}  {dataset['score']}  {dataset['device']} \n"
        print (slack_msg)
        self.__report(slack_msg)

smartchoice_speed_test = WebsiteAudit(csv_path='urls_to_run.csv')
smartchoice_speed_test.audit()
