from typing import List, Dict, Optional

import numpy as np
from faiss import normalize_L2
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores import Milvus
from sklearn.preprocessing import normalize

from configs import SCORE_THRESHOLD, kbs_config, text_splitter_dict

from server.knowledge_base.kb_service.base import KBService, SupportedVSType, EmbeddingsFunAdapter, \
    score_threshold_process
from server.knowledge_base.utils import KnowledgeFile


class MilvusKBService(KBService):
    milvus: Milvus

    @staticmethod
    def get_collection(milvus_name):
        from pymilvus import Collection
        return Collection(milvus_name)

    # def save_vector_store(self):
    #     if self.milvus.col:
    #         self.milvus.col.flush()

    def get_doc_by_id(self, id: str) -> Optional[Document]:
        if self.milvus.col:
            data_list = self.milvus.col.query(expr=f'pk == {id}', output_fields=["*"])
            if len(data_list) > 0:
                data = data_list[0]
                text = data.pop("text")
                return Document(page_content=text, metadata=data)

    @staticmethod
    def search(milvus_name, content, limit=3):
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10},
        }
        c = MilvusKBService.get_collection(milvus_name)
        return c.search(content, "embeddings", search_params, limit=limit, output_fields=["content"])

    def do_create_kb(self):
        pass

    def vs_type(self) -> str:
        return SupportedVSType.MILVUS

    def _load_milvus(self, embeddings: Embeddings = None):
        if embeddings is None:
            embeddings = self._load_embeddings()
        self.milvus = Milvus(embedding_function=EmbeddingsFunAdapter(embeddings),
                             collection_name=self.kb_name, connection_args=kbs_config.get("milvus"))

    def do_init(self):
        self._load_milvus()

    def do_drop_kb(self):
        if self.milvus.col:
            self.milvus.col.release()
            self.milvus.col.drop()

    def do_search(self, query: str, top_k: int, score_threshold: float, embeddings: Embeddings):
        self._load_milvus(embeddings=EmbeddingsFunAdapter(embeddings))
        return score_threshold_process(score_threshold, top_k, self.milvus.similarity_search_with_score(query, top_k))

    def do_add_doc(self, docs: List[Document], **kwargs) -> List[Dict]:
        # TODO: workaround for bug #10492 in langchain
        # langchain中milvus会将第一次传入的docs中的第一个doc.metadata中的keys作为初始化vector_db的fields，并且必须保证每一个doc.metadata中的keys相同才行
        # 这里doc.metadata只增加了headers，如果有额外的元数据，也需要特殊处理
        # 经过测试faiss不会出现此问题
        fields = []
        headers = text_splitter_dict["MarkdownHeaderTextSplitter"]["headers_to_split_on"]
        for key, header in headers:
            fields.append(header)

        for doc in docs:
            for k, v in doc.metadata.items():
                doc.metadata[k] = str(v)
            for field in self.milvus.fields:
                doc.metadata.setdefault(field, "")
            # 第一次传入docs时，vector_db还没初始化，self.milvus.fields还是空的，所以需要自己保证每个doc.metadata中的keys相同
            for field in fields:
                doc.metadata.setdefault(field, "")
            doc.metadata.pop(self.milvus._text_field, None)
            doc.metadata.pop(self.milvus._vector_field, None)

        ids = self.milvus.add_documents(docs)
        doc_infos = [{"id": id, "metadata": doc.metadata} for id, doc in zip(ids, docs)]
        return doc_infos

    def do_delete_doc(self, kb_file: KnowledgeFile, **kwargs):
        if self.milvus.col:
            filepath = kb_file.filepath.replace('\\', '\\\\')
            delete_list = [item.get("pk") for item in
                           self.milvus.col.query(expr=f'source == "{filepath}"', output_fields=["pk"])]
            self.milvus.col.delete(expr=f'pk in {delete_list}')

    def do_clear_vs(self):
        if self.milvus.col:
            self.do_drop_kb()
            self.do_init()


if __name__ == '__main__':
    # 测试建表使用
    from server.db.base import Base, engine

    Base.metadata.create_all(bind=engine)
    milvusService = MilvusKBService("test")
    # milvusService.add_doc(KnowledgeFile("README.md", "test"))

    print(milvusService.get_doc_by_id("444022434274215486"))
    # milvusService.delete_doc(KnowledgeFile("README.md", "test"))
    # milvusService.do_drop_kb()
    # print(milvusService.search_docs("如何启动api服务"))
