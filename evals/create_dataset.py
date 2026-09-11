import json
from langsmith import Client
from dotenv import load_dotenv

load_dotenv()

client = Client()

with open("dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

langsmith_dataset = client.create_dataset(
    dataset_name="E-assi Requirements Evaluation",
    description="E-assi 商品需求提取评测数据集"
)

for case in dataset:
    client.create_example(
        inputs=case["inputs"],
        outputs=case["reference_outputs"],
        dataset_id=langsmith_dataset.id
    )

print("Dataset ID:", langsmith_dataset.id)
print("Dataset name:", langsmith_dataset.name)