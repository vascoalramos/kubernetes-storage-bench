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
            "password":"vekiduvesavipiko"
        })

        #self.path = os.path.abspath("../videos")
        #self.videos = os.listdir(self.path)

        self.videos = ["/download/videos/5b4e4e1f-aa6f-4d97-851e-454de4e2d8ad-720.mp4",
                    "/download/videos/607cb2c4-6bbb-44d8-ace9-a009f06caf75-720.mp4",
                    "/download/videos/e13e1b16-0d29-4fa5-b8ff-6780033d763b-720.mp4",
                    "/download/videos/799782f3-af98-4a58-9c97-527da7c7732a-720.mp4",
                    "/download/videos/8a273bd9-63ae-40f5-87bd-7f307f2c057f-720.mp4"]
        
        self.count=0
        self.token = resptoken.json()['access_token']
