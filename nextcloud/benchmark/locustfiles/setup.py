from locust import HttpUser
from actions import get_content_list

import json
import xmltodict


class Setup(HttpUser):
    def on_start(self):
        # get xml list of directories and files
        content_xml = get_content_list(self, "")

        # get content list of files and folders
        content_list = {"folders": [], "files": []}
        self.retrive_content_from_xml(content_xml, content_list)

        # store dict in file in JSON format
        with open("content.json", "w") as file:
            json.dump(content_list, file, indent=4, sort_keys=True)

        # end session
        self.environment.runner.quit()

    def retrive_content_from_xml(self, content_xml, content_dict, subdir=False):
        # convert xml to dict
        content = xmltodict.parse(content_xml)

        items = [item["d:href"] for item in content["d:multistatus"]["d:response"]]
        if subdir:
            items = items[1:]

        for item in items:
            entry = item[28:].replace("%20", " ") if len(item) > 28 else ""

            if entry == "" or entry[-1] == "/":
                if entry not in content_dict["folders"]:
                    content_dict["folders"].append(entry)

                self.retrive_content_from_xml(
                    get_content_list(self, entry),
                    content_dict,
                    subdir=True,
                )
            else:
                if entry not in content_dict["files"]:
                    content_dict["files"].append(entry)
