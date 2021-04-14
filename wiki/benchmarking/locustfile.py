import re
import json
import random
import string
import time
from ntpath import basename
from locust import HttpUser, task, between


def readFile(path):
    with open(path) as file:
        return file.read()


def graphqlQuery(httpUser, query, vars, auth_token=""):
    return httpUser.client.post(url="/graphql", json={"query": query, "variables": vars}, headers={"Connection": "keep-alive", "Authorization": auth_token})


def getContentFromParentPage(httpUser, parent):
    pages = []

    page_response = graphqlQuery(httpUser, readFile("queries/pageTree.graphql"), {"parent": parent})

    for item in page_response.json()["data"]["pages"]["tree"]:
        if item["isFolder"]:
            pages += getContentFromParentPage(httpUser, item["id"])
        else:
            pages.append("/" + item["path"])

    return pages


def login(httpUser, username, password):
    login_response = graphqlQuery(httpUser, readFile("queries/login.graphql"), {"username": username, "password": password})
    return login_response.json()["data"]["authentication"]["login"]["jwt"]


def getRootPageTree(httpUser):
    return getContentFromParentPage(httpUser, 0)


def createPage(httpUser, auth_token):
    path = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
    title = "NASA"
    content = "<h1>Artemis</h1>"

    return writePage(httpUser, auth_token, path, title, content, tags=["locust"])


def writePage(httpUser, auth_token, path, title, content, description="", tags=[]):
    return graphqlQuery(httpUser, readFile("queries/createPage.graphql"), {"path": path, "title": title, "tags": tags, "content": content, "description": description}, auth_token=auth_token)


def loadPage(httpUser, page):
    index = httpUser.client.get(url=page)

    srcs = re.findall("(?<=src=\")(.*?)(?=\")", index.text)
    hrefs = re.findall("(?<=href=\")(.*?)(?=\")", index.text)

    for src in srcs:
        httpUser.client.get(url=src if src[0] == '/' else re.search(".*\\/", page).group(0) + src)

    for href in hrefs:
        if href[0] != '#':
            httpUser.client.get(url=href if href[0] == '/' else re.search(".*\\/", page).group(0) + href)


def uploadFile(httpUser, parentFolderId, filePath, auth_token):
    return httpUser.client.post(url="/u", data={"mediaUpload": '{{"folderId":{}}}'.format(parentFolderId)}, files={"mediaUpload": open(filePath, "rb")}, headers={"Authorization": auth_token, "Connection": "keep-alive"})


class ReadFromWiki(HttpUser):
    available_pages = []
    token = "Bearer "
    
    def on_start(self):
        self.token += login(self, "admin", "passwd")
        self.available_pages = getRootPageTree(self)

    @task
    def requestAllPages(self):
        loadPage(self, random.choice(self.available_pages))
        createPage(self, self.token)