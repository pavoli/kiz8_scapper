from typing import List
from sentence_transformers import SentenceTransformer


def get_sentence_embeddings(texts: List[str], model_name: str = "distiluse-base-multilingual-cased") -> List[List[float]]:
    """
    Преобразует список текстов в эмбеддинги с помощью SentenceTransformers.

    Args:
        texts (List[str]): Список строк (предложений или документов) для кодирования.
        model_name (str): Название модели SentenceTransformer. По умолчанию - многоязычная модель.

    Returns:
        List[List[float]]: Список эмбеддингов, каждый из которых - список чисел с плавающей точкой.
    """
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()

# Пример использования
if __name__ == "__main__":
    sentences = [
        "Почему мы делаем git pull, а затем git push?",
    ]
    vectors = get_sentence_embeddings(sentences)
    for i, vec in enumerate(vectors):
        print(f"Эмбеддинг для предложения {i+1}: {vec[:5]}...")  # вывод первых 5 чисел для примера
