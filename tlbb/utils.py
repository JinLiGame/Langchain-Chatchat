import os
import traceback
from datetime import datetime

# 分割后存储路径
SPLIT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs/split_documents")
if not os.path.exists(SPLIT_PATH):
    os.mkdir(SPLIT_PATH)


def save_2_file_split_documents(docs, kb_name, doc_name, custom):
    doc_name = os.path.splitext(doc_name)[0]
    cur_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{kb_name}_{doc_name}_{custom}_{cur_time}.txt"
    output = os.path.join(SPLIT_PATH, file_name)
    # print(f"save_2_file_split_documents output:{output}")
    with open(output, "w") as file:
        file.write(f"total items:{len(docs)}")
        file.write("\n")
        file.write("\n")

        i = 1
        for doc in docs:
            file.write(f"------------ item: {i}\n")
            i = i + 1
            file.write(doc.page_content)
            file.write("\n")


def save_documents_2_file(docs, kb_name, doc_name, custom):
    doc_name = os.path.splitext(doc_name)[0]
    cur_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{kb_name}_{doc_name}_{custom}_{cur_time}.txt"
    output = os.path.join(SPLIT_PATH, file_name)
    # print(f"save_documents_2_file output:{output}")
    with open(output, "w") as file:
        file.write(f"total items:{len(docs)}")
        file.write("\n")
        file.write("\n")

        i = 1
        for doc in docs:
            file.write(f"------------ item: {i}\n")
            i = i + 1
            file.write(str(doc))
            file.write("\n")


def print_stack(msg):
    print(msg)
    traceback.print_stack()


def print_documents(docs):
    for doc in docs:
        print(doc)
