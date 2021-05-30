import time
import random
from locust import HttpUser, task, between
from config import StaticBenchmarkConfig

#{'error': 'This file is not supported. Please, make sure it is of the following type: .webm, .ogv, .ogg, .mp4, .mkv, .mov, .qt, .mqv, .m4v, .flv, .f4v, .wmv, .avi, .3gp, .3gpp, .3g2, .3gpp2, .nut, .mts, .m2ts, .mpv, .m2v, .m1v, .mpg, .mpe, .mpeg, .vob, .mxf, .mp3, .wma, .wav, .flac, .aac, .m4a, .ac3'}




class QuickstartUser(HttpUser):
    wait_time = StaticBenchmarkConfig.read_page_wait_seconds
    token=''

    @task
    def download(self):
        i = random.randint(0,len(self.videos)-1)
        resp1= self.client.get(self.videos[i], name="download")
        #print(resp1.json())
        #self.client.get("/download/videos/c5c7a933-3df1-45d1-b6d4-c6568db828a7-2160.mp4")



    def on_start(self):
        #resp1= self.client.get("api/v1/oauth-clients/local")

        #json_resp = resp1.json()

        #resptoken= self.client.post("api/v1/users/token", data={
        #    "client_id":json_resp['client_id'],
        #    "client_secret":json_resp['client_secret'],
        #    "grant_type":"password",
        #    "response_type":"code",
        #    "username":"root",
        #    "password":"vekiduvesavipiko"
        #})

        self.videos = ["/download/videos/5b4e4e1f-aa6f-4d97-851e-454de4e2d8ad-720.mp4",
                    "/download/videos/607cb2c4-6bbb-44d8-ace9-a009f06caf75-720.mp4",
                    "/download/videos/e13e1b16-0d29-4fa5-b8ff-6780033d763b-720.mp4",
                    "/download/videos/799782f3-af98-4a58-9c97-527da7c7732a-720.mp4",
                    "/download/videos/8a273bd9-63ae-40f5-87bd-7f307f2c057f-720.mp4"]
        
        #self.count=0
        #self.token = resptoken.json()['access_token']