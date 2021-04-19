import os, random, string

import actions.common as common
import actions.graphqlQueries as graphqlQueries

GENERATED_USERNAME_PREFIX = "minion-"
ADMIN_GROUP_ID = 1


def getCredentials(greenletId):
    # Check available users
    users = os.listdir(common.inReferencePath("users"))
    users.remove(".gitignore")
    users.sort()
    
    if greenletId >= len(users):
        raise Exception("Not enough users!")

    user_credentials = common.readFile("users/{}".format(users[greenletId])).split(" ")

    return user_credentials[0], user_credentials[1]


def generateUsers(httpUser, userCount=50):
    # Generate user
    for _ in range(userCount):
        user_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
        name = GENERATED_USERNAME_PREFIX + user_id
        email = "{}@locust.com".format(user_id)
        password = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(15))
        succeded = graphqlQueries.createUser(httpUser, ADMIN_GROUP_ID, email, name, password)["data"]["users"]["create"]["responseResult"]["succeeded"]

        if succeded:
            common.writeFile("users/{}".format(user_id), "{} {}".format(email, password))


def deleteGeneratedUsers(httpUser):
    # Get existing users
    users = graphqlQueries.listUsers(httpUser)

    # Delete users containing generated prefix
    for user in users:
        if GENERATED_USERNAME_PREFIX in user["name"] and user["id"] != 1:
            graphqlQueries.deleteUser(httpUser, user["id"])

    # Delete users files
    files = os.listdir(common.inReferencePath("users"))
    files.remove(".gitignore")

    for user in files:
        os.remove(common.inReferencePath("users/{}".format(user)))