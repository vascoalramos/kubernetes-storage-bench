import os, random, string, re, math

import actions.common as common
import actions.graphqlQueries as graphqlQueries

GENERATED_FOLDER_PREFIX = "locust-"

def loadPage(httpUser, page):
    # Prepare url
    if page[0] != "/":
        page = "/" + page

    # Get page
    index = httpUser.client.get(url=page, name="Load page")

    # Use regex to find files to import
    srcs = re.findall("(?<=src=\")(.*?)(?=\")", index.text)

    # Load files
    for src in srcs:
        httpUser.client.get(url=src if src[0] == '/' else re.search(".*\\/", page).group(0) + src, name="Load content")


def generateComment(httpUser, pageId, commentLength=200):
    comment = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation + string.whitespace) for _ in range(commentLength))
    return graphqlQueries.comment(httpUser, pageId, comment)


def generatePage(httpUser, dataset, contentInstancesPerCategory=10, constant=False):
    # Function that fills a template with a value
    def fillTemplate(template, value, tracker_set=None):
        # Add value to set
        if tracker_set != None:
            tracker_set.add(value)

        # Return filled template
        return template.replace("PLACEHOLDER", value)

    # Function to calculate how many content instances depending on "random" flag
    def randomOrDefault(content_instances_per_category, constant):
        return random.randint(math.floor(content_instances_per_category/2), content_instances_per_category) if constant else content_instances_per_category

    # Generate random folder to save content
    slug = GENERATED_FOLDER_PREFIX + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

    # Get existing folders in root
    folders = graphqlQueries.listFoldersInParent(httpUser, 0)

    # Guarantee generated slug is not taken
    taken_slugs = list(map(lambda folder: folder["slug"], folders))
    while (slug in taken_slugs):
        slug = GENERATED_FOLDER_PREFIX + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

    # Create folder with generated slug
    graphqlQueries.createFolder(httpUser, 0, slug)

    # Get folders again to find generated folder id
    folders = graphqlQueries.listFoldersInParent(httpUser, 0)
    folder = next(filter(lambda folder: folder["slug"] == slug, folders), None)
    assert folder != None

    # Create sets to keep record of which files to upload later, list with existing content options and templates
    content, page_template, icons = [], common.readFile("templates/index.html"), dataset["icons"]
    images, image_template, all_images = set(), common.readFile("templates/img.html"), dataset["images"]
    videos, video_template, all_videos = set(), common.readFile("templates/video.html"), dataset["videos"]
    audios, audio_template, all_audios = set(), common.readFile("templates/audio.html"), dataset["audios"]
    gifs, gif_template, all_gifs = set(), common.readFile("templates/gif.html"), dataset["gifs"]
    all_texts, text_template = dataset["texts"], common.readFile("templates/text.html")
    
    # Add content
    content += [fillTemplate(image_template, random.choice(list(all_images.keys())), images)
                for i in range(randomOrDefault(contentInstancesPerCategory, constant))]
    content += [fillTemplate(video_template, random.choice(list(all_videos.keys())), videos)
                for i in range(randomOrDefault(contentInstancesPerCategory, constant))]
    content += [fillTemplate(audio_template, random.choice(list(all_audios.keys())), audios)
                for i in range(randomOrDefault(contentInstancesPerCategory, constant))]
    content += [fillTemplate(gif_template, random.choice(list(all_gifs.keys())), gifs) 
                for i in range(randomOrDefault(contentInstancesPerCategory, constant))]
    content += [fillTemplate(text_template, (random.choice(list(map(lambda x: str(x), all_texts.values())))))
                for i in range(randomOrDefault(contentInstancesPerCategory, constant))]

    # Shuffle content list
    random.shuffle(content)

    # Upload files
    [graphqlQueries.uploadFile(httpUser, folder["id"], all_images[asset], asset) for asset in images]
    [graphqlQueries.uploadFile(httpUser, folder["id"], all_videos[asset], asset) for asset in videos]
    [graphqlQueries.uploadFile(httpUser, folder["id"], all_audios[asset], asset) for asset in audios]
    [graphqlQueries.uploadFile(httpUser, folder["id"], all_gifs[asset], asset) for asset in gifs]
    [graphqlQueries.uploadFile(httpUser, folder["id"], icons[icon], icon) for icon in icons.keys()]

    # Fill content to index template and create page
    page = page_template.replace("PLACEHOLDER", '\n'.join(content))
    
    # Return page id
    return graphqlQueries.createPage(httpUser, "{}/index".format(slug), "Generated page", page, tags=["locust"])["data"]["pages"]["create"]["page"]["id"]


def getPageFullTree(httpUser, parentId):
    # List to save all pages
    pages = []

    # Get page tree from parent    
    page_tree = graphqlQueries.pageTreeInParent(httpUser, parentId)

    # Recursive call if leaf is folder, or add to pages otherwise
    for leaf in page_tree:
        if leaf["isFolder"]:
            pages += getPageFullTree(httpUser, leaf["id"])
        else:
            pages.append(leaf)

    return pages


def deleteGeneratedAssetsAndPages(httpUser):
    # Get existing folders in root
    folders = graphqlQueries.listFoldersInParent(httpUser, 0)

    # Go through folders with generated prefix, and delete assets
    for folder in folders:
        if GENERATED_FOLDER_PREFIX in folder["slug"]:
            assets = graphqlQueries.listAssetsInFolder(httpUser, folder["id"])

            for asset in assets:
                graphqlQueries.deleteAsset(httpUser, asset["id"])

    # After deleting assets, delete pages
    root_page_tree = getPageFullTree(httpUser, 0)
    for page in root_page_tree:
        if GENERATED_FOLDER_PREFIX in page["path"]:
            graphqlQueries.deletePage(httpUser, page["pageId"])