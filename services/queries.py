class ReadQueries:
    def __init__(self, filepath):
        with open(filepath) as text_file:
            text_data = text_file.readlines()

        new_data = []
        for t in text_data:
            new_data.append(t.replace("\n", ""))

        self.queries = new_data
