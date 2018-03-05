import os

def find_files(directory):
    paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            paths.append(filepath)
    return [path for path in paths if path.endswith(".md")]


def scrape(read_path):
    print("reading .md files...")
    for fl in find_files(read_path):
        print(fl)
        # new_file = transform_token(fl)
        # with open(fl, "r") as infile:
        #     total_old = []
        #     total_new = []
        #     with open(fl+".s3253481", "w") as outfile:
        #         for line in infile:
        #             line = line.rstrip()
        #
        #
        #         for sentence in new_file:
        #             for line in sentence:
        #                 total_new.append(line)
        #
        #
        #         for line in total_new:
        #             string2 = ''.join(line)



def main():
    scrape("./")


if __name__ == '__main__':
    main()

