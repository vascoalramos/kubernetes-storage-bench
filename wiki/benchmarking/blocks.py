import re
import random
import string
import os

from locust import HttpUser
import actions


def loadPage(httpUser, page):
    # Get page
    index = httpUser.client.get(url=page)

    # Use regex to find files to import
    srcs = re.findall("(?<=src=\")(.*?)(?=\")", index.text)

    # Load files
    for src in srcs:
        httpUser.client.get(url=src if src[0] == '/' else re.search(".*\\/", page).group(0) + src)


def generatePage(httpUser, token, content_instances_per_category=10):
    # Function that fills a template with a value
    def fillTemplate(template, value, tracker_set=None):
        # Add value to set
        if tracker_set != None:
            tracker_set.add(value)

        # Return filled template
        return template.replace("PLACEHOLDER", value)


    # Generate random folder to save content
    slug = "locust-{}".format(''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10)))

    # Get existing folders in root
    folders = actions.listFoldersInParent(httpUser, 0)

    # Guarantee generated slug is not taken
    taken_slugs = list(map(lambda folder: folder["slug"], folders))
    while(slug in taken_slugs):
        slug = "locust-{}".format(''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10)))

    # Create folder with generated slug
    actions.createFolder(httpUser, token, 0, slug)

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

    # Add content
    content += [fillTemplate(image_template, random.choice(all_images), images) for _ in range(random.randint(1, content_instances_per_category))]
    content += [fillTemplate(video_template, random.choice(all_videos), videos) for _ in range(random.randint(1, content_instances_per_category))]
    content += [fillTemplate(audio_template, random.choice(all_audios), audios) for _ in range(random.randint(1, content_instances_per_category))]
    content += [fillTemplate(gif_template, random.choice(all_gifs), gifs) for _ in range(random.randint(1, content_instances_per_category))]
    content += [fillTemplate(text_template, actions.readFile("assets/texts/{}".format(random.choice(all_texts)))) for _ in range(random.randint(1, content_instances_per_category))]

    # Shuffle content list
    random.shuffle(content)

    # Upload files
    [actions.uploadFile(httpUser, folder["id"], "assets/images/{}".format(asset), token) for asset in images]
    [actions.uploadFile(httpUser, folder["id"], "assets/videos/{}".format(asset), token) for asset in videos]
    [actions.uploadFile(httpUser, folder["id"], "assets/audios/{}".format(asset), token) for asset in audios]
    [actions.uploadFile(httpUser, folder["id"], "assets/gifs/{}".format(asset), token) for asset in gifs]
    [actions.uploadFile(httpUser, folder["id"], "assets/icons/{}".format(icon), token) for icon in icons]

    # Fill content to index template and create page
    page = page_template.replace("PLACEHOLDER", '\n'.join(content))
    actions.createPage(httpUser, token, "{}/index".format(slug), "Generated page", page, tags=["locust"])


def deleteGeneratedAssets(httpUser, token):
    # Get existing folders in root
    folders = actions.listFoldersInParent(httpUser, 0)

    # Go through folders with 'locust-' prefix, and delete assets
    for folder in folders:
        if "locust-" in folder["slug"]:
            assets = actions.listAssetsInFolder(httpUser, folder["id"])

            for asset in assets:
                actions.deleteAsset(httpUser, token, asset["id"])


    # After deleting assets, delete pages
    root_page_tree = getPageFullTree(httpUser, 0)
    for page in root_page_tree:
        if "locust-" in page["path"]:
            actions.deletePage(httpUser, token, page["pageId"])


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