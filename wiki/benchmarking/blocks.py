import re
import random
import string
import os
import math

from locust import HttpUser
import actions

GENERATED_FOLDER_PREFIX = "locust-"
GENERATED_GROUP_PREFIX = "locust-minions-"
GENERATED_USERNAME_PREFIX = "minion-"
USER_PERMISSIONS = ["read:pages", "read:assets", "read:comments", "write:comments", "write:pages", 
                   "write:assets", "manage:assets", "manage:comments", "delete:pages", "manage:pages"]


def loadPage(httpUser, page):
    # Get page
    index = httpUser.client.get(url=page)

    # Use regex to find files to import
    srcs = re.findall("(?<=src=\")(.*?)(?=\")", index.text)

    # Load files
    for src in srcs:
        httpUser.client.get(url=src if src[0] == '/' else re.search(".*\\/", page).group(0) + src)


def setupUserGroup(httpUser, name):
    # Create group
    group_response = actions.createUserGroup(httpUser, name)
    assert group_response["data"]["groups"]["create"]["responseResult"]["succeeded"]

    # Update permissions
    group_id = group_response["data"]["groups"]["create"]["group"]["id"]
    permissions_response = actions.updateUserGroupPermissions(httpUser, group_id, name, USER_PERMISSIONS)
    assert permissions_response["data"]["groups"]["update"]["responseResult"]["succeeded"]

    return group_id 


def generateRandomUsersWithinGroup(httpUser, user_count=50):
    # Generate group
    group_name = GENERATED_GROUP_PREFIX + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))
    group_id = setupUserGroup(httpUser, group_name)

    # Generate user
    for _ in range(user_count):
        user_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
        name = GENERATED_USERNAME_PREFIX + user_id
        email = "{}@locust.com".format(user_id)
        password = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(15))
        actions.createUser(httpUser, group_id, email, name, password)


def generatePage(httpUser, content_instances_per_category=10, isRandom=True):
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
    content, page_template, icons = [], actions.readFile("templates/index.html"), os.listdir("assets/icons")
    images, all_images, image_template = set(), os.listdir("assets/images"), actions.readFile("templates/img.html")
    videos, all_videos, video_template = set(), os.listdir("assets/videos"), actions.readFile("templates/video.html")
    audios, all_audios, audio_template = set(), os.listdir("assets/audios"), actions.readFile("templates/audio.html")
    gifs, all_gifs, gif_template = set(), os.listdir("assets/gifs"), actions.readFile("templates/gif.html")
    all_texts, text_template = os.listdir("assets/texts"), actions.readFile("templates/text.html")

    # Shufle content if random
    if isRandom:
        random.shuffle(all_images)
        random.shuffle(all_videos)
        random.shuffle(all_audios)
        random.shuffle(all_gifs)
        random.shuffle(all_texts)
    
    # Add content
    content += [fillTemplate(image_template, random.choice(all_images) if isRandom else all_images[i], images)
                for i in range(randomOrDefault(content_instances_per_category, isRandom))]
    content += [fillTemplate(video_template, random.choice(all_videos) if isRandom else all_videos[i], videos)
                for i in range(randomOrDefault(content_instances_per_category, isRandom))]
    content += [fillTemplate(audio_template, random.choice(all_audios) if isRandom else all_audios[i], audios)
                for i in range(randomOrDefault(content_instances_per_category, isRandom))]
    content += [fillTemplate(gif_template, random.choice(all_gifs) if isRandom else all_gifs[i], gifs) 
                for i in range(randomOrDefault(content_instances_per_category, isRandom))]
    content += [fillTemplate(text_template, actions.readFile("assets/texts/{}".format(random.choice(all_texts) if isRandom else all_texts[i]))) 
                for i in range(randomOrDefault(content_instances_per_category, isRandom))]

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
    actions.createPage(httpUser, "{}/index".format(slug), "Generated page", page, tags=["locust"])


def deleteGeneratedAssets(httpUser):
    # Get existing folders in root
    folders = actions.listFoldersInParent(httpUser, 0)

    # Go through folders with 'locust-' prefix, and delete assets
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


def deleteGeneratedUserGroups(httpUser):
    # Get existing user groups
    groups = actions.listUserGroups(httpUser)

    for group in groups:
        if GENERATED_GROUP_PREFIX in group["name"]:
            actions.deleteUserGroup(httpUser, group["id"])


def deleteGeneratedUsers(httpUser):
    # Get existing users
    users = actions.listUsers(httpUser)

    # Delete users containing generated prefix
    for user in users:
        if GENERATED_USERNAME_PREFIX in user["name"] and user["id"] is not 1:
            actions.deleteUser(httpUser, user["id"])


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