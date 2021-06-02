import time
from locust import HttpUser, task, between
from config import UserSimulationBenchmarkConfig
import random

import load

#{'error': 'This file is not supported. Please, make sure it is of the following type: .webm, .ogv, .ogg, .mp4, .mkv, .mov, .qt, .mqv, .m4v, .flv, .f4v, .wmv, .avi, .3gp, .3gpp, .3g2, .3gpp2, .nut, .mts, .m2ts, .mpv, .m2v, .m1v, .mpg, .mpe, .mpeg, .vob, .mxf, .mp3, .wma, .wav, .flac, .aac, .m4a, .ac3'}


class QuickstartUser(HttpUser):
    wait_time = UserSimulationBenchmarkConfig.wait_time_between_tasks
    token=''

    @task(5)
    def download(self):
        i = random.randint(0,len(self.videos)-1)
        resp1= self.client.get(self.videos[i], name="download")
        #print(resp1.json())


    @task(1)
    def upload(self):
        #i = random.randint(0,len(self.videos)-1)
        i = random.randint(0,len(load.videos)-1)
        videofile = load.path +"/" +load.videos[i]
        responsepost = self.client.post("api/v1/videos/upload",
        headers={"Authorization": "Bearer "+self.token},
        data={
            "name":"videoteste"+str(self.count),
            "channelId":"1",
            "waitTranscoding":False,
            "commentsEnabled":True,
            "privacy":'1', 
        },files=[('videofile',(load.videos[i],load.files[i],'video/mp4'))]
        )
        self.count += 1
        # print(responsepost.json())


    def on_start(self):
        resp1= self.client.get("api/v1/oauth-clients/local")

        json_resp = resp1.json()

        resptoken= self.client.post("api/v1/users/token", data={
            "client_id":json_resp['client_id'],
            "client_secret":json_resp['client_secret'],
            "grant_type":"password",
            "response_type":"code",
            "username":"root",
            "password":"ziyuzotofonorane"
        })

        #self.path = os.path.abspath("../videos")
        #self.videos = os.listdir(self.path)

        self.videos = ["/download/videos/07a766c8-9200-4155-9b44-501a563295ef-720.mp4",
                    "/download/videos/ef54e828-4119-44d8-9a9a-c79097d2eda2-720.mp4",
                    "/download/videos/6a3db13d-1506-4e95-9ae3-6c0f14392057-720.mp4",
                    "/download/videos/f19cc9ca-d590-48aa-81ae-b06daff1db3d-720.mp44",
                    "/download/videos/f9cb5188-5133-49ad-8526-03fb92f4013a-720.mp4"]
        
        self.count=0
        self.token = resptoken.json()['access_token']
