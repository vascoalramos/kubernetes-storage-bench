import pathlib
from locust import HttpUser

def inReferencePath(path):
    return "{}/{}".format(str(pathlib.Path(__file__).parent.parent.parent.absolute()), path)

def writeFile(path, content):
    with open(inReferencePath(path), "w") as f:
        f.write(content)

def readFile(path):
    with open(inReferencePath(path)) as f:
        return f.read()

def graphqlQuery(httpUser, query, variables, auth=True):
    return httpUser.client.post(url="/graphql", json={"query": query, "variables": variables}, headers={"Connection": "keep-alive", "Authorization": "Bearer {}".format(httpUser.token if auth else "")}).json()

def pageTreeInParent(httpUser, parent):
    return graphqlQuery(httpUser, readFile("queries/pageTreeInParent.graphql"), {"parent": parent})["data"]["pages"]["tree"]

def listFoldersInParent(httpUser, parent):
    return graphqlQuery(httpUser, readFile("queries/listFoldersInParent.graphql"), {"parentFolderId": parent})["data"]["assets"]["folders"]

def createFolder(httpUser, parentFolderId, folderName):
    return graphqlQuery(httpUser, readFile("queries/createFolder.graphql"), {"parentFolderId": parentFolderId, "slug": folderName})

def listAssetsInFolder(httpUser, parentFolderId):
    return graphqlQuery(httpUser, readFile("queries/listAssetsInFolder.graphql"), {"folderId": parentFolderId})["data"]["assets"]["list"]

def deleteAsset(httpUser, assetId):
    return graphqlQuery(httpUser, readFile("queries/deleteAsset.graphql"), {"id": assetId})

def deletePage(httpUser, pageId):
    return graphqlQuery(httpUser, readFile("queries/deletePage.graphql"), {"id": pageId})

def login(httpUser, username, password):
    return graphqlQuery(httpUser, readFile("queries/login.graphql"), {"username": username, "password": password}, auth=False)["data"]["authentication"]["login"]["jwt"]

def createUser(httpUser, group, email, name, password):
    return graphqlQuery(httpUser, readFile("queries/createUser.graphql"), {"group": group, "email": email, "name": name, "passwordRaw": password})

def listUsers(httpUser):
    return graphqlQuery(httpUser, readFile("queries/listUsers.graphql"), {})["data"]["users"]["list"]

def deleteUser(httpUser, user_id):
    return graphqlQuery(httpUser, readFile("queries/deleteUser.graphql"), {"id": user_id})

def comment(httpUser, page_id, content):
    return graphqlQuery(httpUser, readFile("queries/comment.graphql"), {"pageId": page_id, "content": content})

def updateCommentsSettings(httpUser, settings):
    return graphqlQuery(httpUser, readFile("queries/updateCommentsSettings.graphql"), {"providers": settings})

def createPage(httpUser, path, title, content, description="", tags=[]):
    return graphqlQuery(httpUser, readFile("queries/createPage.graphql"), {"path": path, "title": title, "tags": tags, "content": content, "description": description})

def uploadFile(httpUser, parentFolderId, filePath):
    return httpUser.client.post(url="/u", data={"mediaUpload": '{{"folderId":{}}}'.format(parentFolderId)}, files={"mediaUpload": open(inReferencePath(filePath), "rb")}, headers={"Authorization": "Bearer {}".format(httpUser.token), "Connection": "keep-alive"})