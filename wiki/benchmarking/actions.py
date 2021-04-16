from locust import HttpUser

def readFile(path):
    with open(path) as file:
        return file.read()

def graphqlQuery(httpUser, query, variables, token=""):
    return httpUser.client.post(url="/graphql", json={"query": query, "variables": variables}, headers={"Connection": "keep-alive", "Authorization": "" if not token else "Bearer {}".format(token)}).json()

def pageTreeInParent(httpUser, parent):
    return graphqlQuery(httpUser, readFile("queries/pageTreeInParent.graphql"), {"parent": parent})["data"]["pages"]["tree"]

def listFoldersInParent(httpUser, parent):
    return graphqlQuery(httpUser, readFile("queries/listFoldersInParent.graphql"), {"parentFolderId": parent})["data"]["assets"]["folders"]

def createFolder(httpUser, token, parentFolderId, folderName):
    return graphqlQuery(httpUser, readFile("queries/createFolder.graphql"), {"parentFolderId": parentFolderId, "slug": folderName}, token=token)

def listAssetsInFolder(httpUser, parentFolderId):
    return graphqlQuery(httpUser, readFile("queries/listAssetsInFolder.graphql"), {"folderId": parentFolderId})["data"]["assets"]["list"]

def deleteAsset(httpUser, token, assetId):
    return graphqlQuery(httpUser, readFile("queries/deleteAsset.graphql"), {"id": assetId}, token=token)

def deletePage(httpUser, token, pageId):
    return graphqlQuery(httpUser, readFile("queries/deletePage.graphql"), {"id": pageId}, token=token)

def login(httpUser, username, password):
    return graphqlQuery(httpUser, readFile("queries/login.graphql"), {"username": username, "password": password})["data"]["authentication"]["login"]["jwt"]

def createPage(httpUser, token, path, title, content, description="", tags=[]):
    return graphqlQuery(httpUser, readFile("queries/createPage.graphql"), {"path": path, "title": title, "tags": tags, "content": content, "description": description}, token=token)

def uploadFile(httpUser, parentFolderId, filePath, token):
    return httpUser.client.post(url="/u", data={"mediaUpload": '{{"folderId":{}}}'.format(parentFolderId)}, files={"mediaUpload": open(filePath, "rb")}, headers={"Authorization": "" if not token else "Bearer {}".format(token), "Connection": "keep-alive"})