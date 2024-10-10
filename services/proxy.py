class GetProxy:
    def __init__(self):
        try:
            with open("./data/proxy_list.txt", "r") as text_file:
                proxy_addr = text_file.read().replace("\n", "").strip()

            if len(proxy_addr) < 5:
                proxy_addr = None
        except FileNotFoundError:
            proxy_addr = None

        self.proxy_addr = proxy_addr


class AddProxy:
    def __init__(self, proxy):
        with open("./data/proxy_list.txt", "w+") as text_file:
            text_file.write(proxy)
