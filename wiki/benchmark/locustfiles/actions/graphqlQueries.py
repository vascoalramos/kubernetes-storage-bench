from locust import HttpUser
from actions.common import readFile, inReferencePath

def graphqlQuery(httpUser, name, query, variables={}, auth=True):
    return httpUser.client.post(url="/graphql", name=name, json={"query": query, "variables": variables}, headers={"Connection": "keep-alive", "Authorization": "Bearer {}".format(httpUser.token if hasattr(httpUser, "token") and auth else "")}).json()

def pageTreeInParent(httpUser, parent):
    return graphqlQuery(httpUser, "Query Page Tree", readFile("queries/pageTreeInParent.graphql"), {"parent": parent})["data"]["pages"]["tree"]

def listFoldersInParent(httpUser, parent):
    return graphqlQuery(httpUser, "List Folders", readFile("queries/listFoldersInParent.graphql"), {"parentFolderId": parent})["data"]["assets"]["folders"]

def createFolder(httpUser, parentFolderId, folderName):
    return graphqlQuery(httpUser, "Create Folder", readFile("queries/createFolder.graphql"), {"parentFolderId": parentFolderId, "slug": folderName})

def listAssetsInFolder(httpUser, parentFolderId):
    return graphqlQuery(httpUser, "List Assets", readFile("queries/listAssetsInFolder.graphql"), {"folderId": parentFolderId})["data"]["assets"]["list"]

def deleteAsset(httpUser, assetId):
    return graphqlQuery(httpUser, "Delete Asset", readFile("queries/deleteAsset.graphql"), {"id": assetId})

def deletePage(httpUser, pageId):
    return graphqlQuery(httpUser, "Delete Page", readFile("queries/deletePage.graphql"), {"id": pageId})

def login(httpUser, username, password):
    return graphqlQuery(httpUser, "Login", readFile("queries/login.graphql"), {"username": username, "password": password}, auth=False)["data"]["authentication"]["login"]["jwt"]

def manageApiAccessState(httpUser, state):
    return graphqlQuery(httpUser, "Toggle API Access", readFile("queries/manageApiAccessState.graphql"), {"enabled": state})

def createApiKey(httpUser, name):
    return graphqlQuery(httpUser, "Create API Key", readFile("queries/createApiKey.graphql"), {"name": name})

def listApiKeys(httpUser):
    return graphqlQuery(httpUser, "List API Keys", readFile("queries/listApiKeys.graphql"))["data"]["authentication"]["apiKeys"]

def revokeApiKey(httpUser, key_id):
    return graphqlQuery(httpUser, "Revoke API Key", readFile("queries/revokeApiKey.graphql"), {"id": key_id})

def createUser(httpUser, group, email, name, password):
    return graphqlQuery(httpUser, "Create User", readFile("queries/createUser.graphql"), {"group": group, "email": email, "name": name, "passwordRaw": password})

def listUsers(httpUser):
    return graphqlQuery(httpUser, "List Users", readFile("queries/listUsers.graphql"))["data"]["users"]["list"]

def deleteUser(httpUser, user_id):
    return graphqlQuery(httpUser, "Delete User", readFile("queries/deleteUser.graphql"), {"id": user_id})

def comment(httpUser, page_id, content):
    return graphqlQuery(httpUser, "Comment", readFile("queries/comment.graphql"), {"pageId": page_id, "content": content})

def updateCommentsSettings(httpUser, settings):
    return graphqlQuery(httpUser, "Update Comments Settings", readFile("queries/updateCommentsSettings.graphql"), settings)

def updateSecuritySettings(httpUser, settings):
    return graphqlQuery(httpUser, "Update Security Settings", readFile("queries/updateSecuritySettings.graphql"), settings)

def createPage(httpUser, path, title, content, description="", tags=[]):
    return graphqlQuery(httpUser, "Create Page", readFile("queries/createPage.graphql"), {"path": path, "title": title, "tags": tags, "content": content, "description": description})

def uploadFile(httpUser, parentFolderId, filePath):
    return httpUser.client.post(url="/u", name="Upload file", data={"mediaUpload": '{{"folderId":{}}}'.format(parentFolderId)}, files={"mediaUpload": open(inReferencePath(filePath), "rb")}, headers={"Authorization": "Bearer {}".format(httpUser.token), "Connection": "keep-alive"})