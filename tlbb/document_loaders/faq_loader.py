import logging
from typing import List, Optional

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders.helpers import detect_file_encodings

logger = logging.getLogger(__name__)

QA_SEP = '====='


class FAQLoader(BaseLoader):
    """Load text file.


    Args:
        file_path: Path to the file to load.

        encoding: File encoding to use. If `None`, the file will be loaded
        with the default system encoding.

        autodetect_encoding: Whether to try to autodetect the file encoding
            if the specified encoding fails.
    """

    def __init__(
        self,
        file_path: str,
        qa_sep: str = QA_SEP,
        encoding: Optional[str] = None,
        autodetect_encoding: bool = False,
    ):
        """Initialize with file path."""
        self.file_path = file_path
        self.qa_sep = qa_sep
        self.encoding = encoding
        self.autodetect_encoding = autodetect_encoding

    def load(self) -> List[Document]:
        """Load from file path."""
        text = ""
        try:
            with open(self.file_path, encoding=self.encoding) as f:
                text = f.read()
        except UnicodeDecodeError as e:
            if self.autodetect_encoding:
                detected_encodings = detect_file_encodings(self.file_path)
                for encoding in detected_encodings:
                    logger.debug(f"Trying encoding: {encoding.encoding}")
                    try:
                        with open(self.file_path, encoding=encoding.encoding) as f:
                            text = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
            else:
                raise RuntimeError(f"Error loading {self.file_path}") from e
        except Exception as e:
            raise RuntimeError(f"Error loading {self.file_path}") from e

        print(f"------------------- FAQLoader :{text}")
        docs = []
        docs_q = []
        docs_a = []
        arr = text.split(self.qa_sep)
        for item in arr:
            print(item)
            question, answer = item.strip().split("\n", 1)
            question = question.replace("Question: ", "")
            answer = answer.replace("Answer: ", "")
            metadata_q = {"source": self.file_path, "doc_category": "FAQ", "doc_sub_category": "Question"}
            metadata_a = {"source": self.file_path, "doc_category": "FAQ", "doc_sub_category": "Answer"}
            doc_q = Document(page_content=question, metadata=metadata_q)
            docs.append(doc_q)
            doc_a = Document(page_content=answer, metadata=metadata_a)
            docs.append(doc_a)

        return docs
