import os, random, string

import actions.common as common
import actions.graphqlQueries as graphqlQueries

GENERATED_API_KEY_PREFIX = "locust-key-"


def getApiKey(greenletId):
    # Check available API keys
    apiKeys = os.listdir(os.fspath(common.inReferencePath("api-keys")))
    apiKeys.remove(".gitignore")
    apiKeys.sort()    
    
    if greenletId >= len(apiKeys):
        raise Exception("Not enough API keys!")

    return common.readFile("api-keys/{}".format(apiKeys[greenletId]))


def generateApiKeys(httpUser, keyCount=50):
    # Generate key
    for _ in range(keyCount):
        key_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
        key_response = graphqlQueries.createApiKey(httpUser, GENERATED_API_KEY_PREFIX + key_id)

        if key_response["data"]["authentication"]["createApiKey"]["responseResult"]["succeeded"]:
            common.writeFile("api-keys/{}".format(key_id), key_response["data"]["authentication"]["createApiKey"]["key"])


def deleteGeneratedApiKeys(httpUser):
    # Get existing API keys
    api_keys = graphqlQueries.listApiKeys(httpUser)

    # Delete API keys which name contain generated prefix
    for api_key in api_keys:
        if GENERATED_API_KEY_PREFIX in api_key["name"]:
            graphqlQueries.revokeApiKey(httpUser, api_key["id"])

    # Delete API keys files
    files = os.listdir(common.inReferencePath("api-keys"))
    files.remove(".gitignore")

    for api_key in files:
        os.remove(common.inReferencePath("api-keys/{}".format(api_key)))