def get_file(self, file_path):
    self.client.get(
        f"http://cloud74:30000/remote.php/dav/files/admin/{file_path}",
        auth=("admin", "admin"),
    )


def upload_file(self, file, file_path):
    self.client.put(
        f"http://cloud74:30000/remote.php/dav/files/admin/{file_path}",
        data=file,
        auth=("admin", "admin"),
    )


def create_folder(self, name):
    self.client.request(
        "MKCOL",
        f"http://cloud74:30000/remote.php/dav/files/admin/{name}",
        auth=("admin", "admin"),
    )


def copy(self, src, dest):
    self.client.request(
        "COPY",
        f"http://cloud74:30000/remote.php/dav/files/admin/{src}",
        auth=("admin", "admin"),
        headers={
            "Destination": f"http://cloud74:30000/remote.php/dav/files/admin/{dest}"
        },
    )
