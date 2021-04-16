from locust import HttpUser

def readFile(path):
    with open(path) as file:
        return file.read()

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

def createUserGroup(httpUser, group):
    return graphqlQuery(httpUser, readFile("queries/createUserGroup.graphql"), {"name": group})

def listUserGroups(httpUser):
    return graphqlQuery(httpUser, readFile("queries/listUserGroups.graphql"), {})["data"]["groups"]["list"]

def deleteUserGroup(httpUser, group_id):
    return graphqlQuery(httpUser, readFile("queries/deleteUserGroup.graphql"), {"id": group_id})

def updateUserGroupPermissions(httpUser, group_id, name, permissions):
    return graphqlQuery(httpUser, readFile("queries/updateUserGroupPermissions.graphql"), {"id": group_id, "name": name, "permissions": permissions})

def comment(httpUser, page_id, content):
    return graphqlQuery(httpUser, readFile("queries/comment.graphql"), {"pageId": page_id, "content": content})

def createPage(httpUser, path, title, content, description="", tags=[]):
    return graphqlQuery(httpUser, readFile("queries/createPage.graphql"), {"path": path, "title": title, "tags": tags, "content": content, "description": description})

def uploadFile(httpUser, parentFolderId, filePath):
    return httpUser.client.post(url="/u", data={"mediaUpload": '{{"folderId":{}}}'.format(parentFolderId)}, files={"mediaUpload": open(filePath, "rb")}, headers={"Authorization": "Bearer {}".format(httpUser.token), "Connection": "keep-alive"})