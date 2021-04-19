import re
import random
import string
import os
import json
import math

from locust import HttpUser
import common.actions as actions

GENERATED_FOLDER_PREFIX = "locust-"
GENERATED_USERNAME_PREFIX = "minion-"
ADMIN_GROUP_ID = 1


def loadPage(httpUser, page):
    # Get page
    index = httpUser.client.get(url=page)

    # Use regex to find files to import
    srcs = re.findall("(?<=src=\")(.*?)(?=\")", index.text)

    # Load files
    for src in srcs:
        httpUser.client.get(url=src if src[0] == '/' else re.search(".*\\/", page).group(0) + src)


def getCredentials():
    # Check available users
    users = os.listdir(actions.inReferencePath("users"))
    
    user = random.choice(users)
    user_credentials = actions.readFile("users/{}".format(user)).split(" ")

    return user_credentials[0], user_credentials[1]


def applySettings(httpUser):
    # Apply comments settings
    comments_settings = json.loads(actions.readFile("settings/comments.json"))
    return actions.updateCommentsSettings(httpUser, comments_settings)


def generateUsers(httpUser, userCount=50):
    # Generate user
    for _ in range(userCount):
        user_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
        name = GENERATED_USERNAME_PREFIX + user_id
        email = "{}@locust.com".format(user_id)
        password = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(15))
        succeded = actions.createUser(httpUser, ADMIN_GROUP_ID, email, name, password)["data"]["users"]["create"]["responseResult"]["succeeded"]

        if succeded:
            actions.writeFile("users/{}.txt".format(user_id), "{} {}".format(email, password))


def generateComment(httpUser, pageId, commentLength=200):
    comment = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation + string.whitespace) for _ in range(commentLength))
    return actions.comment(httpUser, pageId, comment)


def generatePage(httpUser, contentInstancesPerCategory=10, isRandom=True):
    # Function that fills a template with a value
    def fillTemplate(template, value, tracker_set=None):
        # Add value to set
        if tracker_set != None:
            tracker_set.add(value)

        # Return filled template
        return template.replace("PLACEHOLDER", value)

    # Function to calculate how many content instances depending on "random" flag
    def randomOrDefault(content_instances_per_category, isRandom):
        return random.randint(math.floor(content_instances_per_category/2), content_instances_per_category) if isRandom else content_instances_per_category

    # Generate random folder to save content
    slug = GENERATED_FOLDER_PREFIX + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

    # Get existing folders in root
    folders = actions.listFoldersInParent(httpUser, 0)

    # Guarantee generated slug is not taken
    taken_slugs = list(map(lambda folder: folder["slug"], folders))
    while (slug in taken_slugs):
        slug = GENERATED_FOLDER_PREFIX + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

    # Create folder with generated slug
    actions.createFolder(httpUser, 0, slug)

    # Get folders again to find generated folder id
    folders = actions.listFoldersInParent(httpUser, 0)
    folder = next(filter(lambda folder: folder["slug"] == slug, folders), None)
    assert folder != None

    # Create sets to keep record of which files to upload later, list with existing content options and templates
    content, page_template, icons = [], actions.readFile("templates/index.html"), os.listdir(actions.inReferencePath("assets/icons"))
    images, all_images, image_template = set(), os.listdir(actions.inReferencePath("assets/images")), actions.readFile("templates/img.html")
    videos, all_videos, video_template = set(), os.listdir(actions.inReferencePath("assets/videos")), actions.readFile("templates/video.html")
    audios, all_audios, audio_template = set(), os.listdir(actions.inReferencePath("assets/audios")), actions.readFile("templates/audio.html")
    gifs, all_gifs, gif_template = set(), os.listdir(actions.inReferencePath("assets/gifs")), actions.readFile("templates/gif.html")
    all_texts, text_template = os.listdir(actions.inReferencePath("assets/texts")), actions.readFile("templates/text.html")

    # Shufle content if random
    if isRandom:
        random.shuffle(all_images)
        random.shuffle(all_videos)
        random.shuffle(all_audios)
        random.shuffle(all_gifs)
        random.shuffle(all_texts)
    
    # Add content
    content += [fillTemplate(image_template, random.choice(all_images) if isRandom else all_images[i], images)
                for i in range(randomOrDefault(contentInstancesPerCategory, isRandom))]
    content += [fillTemplate(video_template, random.choice(all_videos) if isRandom else all_videos[i], videos)
                for i in range(randomOrDefault(contentInstancesPerCategory, isRandom))]
    content += [fillTemplate(audio_template, random.choice(all_audios) if isRandom else all_audios[i], audios)
                for i in range(randomOrDefault(contentInstancesPerCategory, isRandom))]
    content += [fillTemplate(gif_template, random.choice(all_gifs) if isRandom else all_gifs[i], gifs) 
                for i in range(randomOrDefault(contentInstancesPerCategory, isRandom))]
    content += [fillTemplate(text_template, actions.readFile("assets/texts/{}".format(random.choice(all_texts) if isRandom else all_texts[i]))) 
                for i in range(randomOrDefault(contentInstancesPerCategory, isRandom))]

    # Shuffle content list
    if isRandom:
        random.shuffle(content)

    # Upload files
    [actions.uploadFile(httpUser, folder["id"], "assets/images/{}".format(asset)) for asset in images]
    [actions.uploadFile(httpUser, folder["id"], "assets/videos/{}".format(asset)) for asset in videos]
    [actions.uploadFile(httpUser, folder["id"], "assets/audios/{}".format(asset)) for asset in audios]
    [actions.uploadFile(httpUser, folder["id"], "assets/gifs/{}".format(asset)) for asset in gifs]
    [actions.uploadFile(httpUser, folder["id"], "assets/icons/{}".format(icon)) for icon in icons]

    # Fill content to index template and create page
    page = page_template.replace("PLACEHOLDER", '\n'.join(content))
    
    # Return page id
    return actions.createPage(httpUser, "{}/index".format(slug), "Generated page", page, tags=["locust"])["data"]["pages"]["create"]["page"]["id"]


def deleteGeneratedAssetsAndPages(httpUser):
    # Get existing folders in root
    folders = actions.listFoldersInParent(httpUser, 0)

    # Go through folders with generated prefix, and delete assets
    for folder in folders:
        if GENERATED_FOLDER_PREFIX in folder["slug"]:
            assets = actions.listAssetsInFolder(httpUser, folder["id"])

            for asset in assets:
                actions.deleteAsset(httpUser, asset["id"])

    # After deleting assets, delete pages
    root_page_tree = getPageFullTree(httpUser, 0)
    for page in root_page_tree:
        if GENERATED_FOLDER_PREFIX in page["path"]:
            actions.deletePage(httpUser, page["pageId"])


def deleteGeneratedUsers(httpUser):
    # Get existing users
    users = actions.listUsers(httpUser)

    # Delete users containing generated prefix
    for user in users:
        if GENERATED_USERNAME_PREFIX in user["name"] and user["id"] != 1:
            actions.deleteUser(httpUser, user["id"])

    # Delete user files
    for user in os.listdir(actions.inReferencePath("users")):
        os.remove(actions.inReferencePath("users/{}".format(user)))


def getPageFullTree(httpUser, parentId):
    # List to save all pages
    pages = []

    # Get page tree from parent    
    page_tree = actions.pageTreeInParent(httpUser, parentId)

    # Recursive call if leaf is folder, or add to pages otherwise
    for leaf in page_tree:
        if leaf["isFolder"]:
            pages += getPageFullTree(httpUser, leaf["id"])
        else:
            pages.append(leaf)

    return pages