import time
import random
from locust import HttpUser, task, between

#{'error': 'This file is not supported. Please, make sure it is of the following type: .webm, .ogv, .ogg, .mp4, .mkv, .mov, .qt, .mqv, .m4v, .flv, .f4v, .wmv, .avi, .3gp, .3gpp, .3g2, .3gpp2, .nut, .mts, .m2ts, .mpv, .m2v, .m1v, .mpg, .mpe, .mpeg, .vob, .mxf, .mp3, .wma, .wav, .flac, .aac, .m4a, .ac3'}




class QuickstartUser(HttpUser):
    wait_time = between(1, 2.5)
    token=''

    @task
    def download(self):
        i = random.randint(0,len(self.videos)-1)
        resp1= self.client.get(self.videos[i])
        print(resp1.json())
        #self.client.get("/download/videos/c5c7a933-3df1-45d1-b6d4-c6568db828a7-2160.mp4")



    def on_start(self):
        resp1= self.client.get("api/v1/oauth-clients/local")

        json_resp = resp1.json()

        resptoken= self.client.post("api/v1/users/token", data={
            "client_id":json_resp['client_id'],
            "client_secret":json_resp['client_secret'],
            "grant_type":"password",
            "response_type":"code",
            "username":"root",
            "password":"ratazolojizefixu"
        })

        self.videos = ["/download/videos/83cb3f62-5e5f-4a8e-b1d0-975b4155b398-720.mp4",
                    "/download/videos/8e02813f-4a9a-4720-9273-1dcdcad59364-720.mp4",
                    "/download/videos/ee9bf5a5-bc88-4061-80b9-696296dfc39c-720.mp4"]
        
        self.count=0
        self.token = resptoken.json()['access_token']