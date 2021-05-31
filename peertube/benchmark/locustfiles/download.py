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

        self.videos = ["/download/videos/087e0cc0-6f08-4666-b3d2-59ffa0527c12-720.mp4",
                    "/download/videos/6d5253be-78ec-4cf9-b35f-3759629672ec-720.mp4",
                    "/download/videos/4ed20867-4cb9-45e4-b987-2483aa830c33-720.mp4",
                    "/download/videos/0dd78ad0-4cf9-4858-b454-19bf9f34c5f2-720.mp4",
                    "/download/videos/b70ffc25-12da-4aac-b52b-cecdebce49a0-720.mp4"]
        
        #self.count=0
        #self.token = resptoken.json()['access_token']