import os
from datetime import date

from notion_client import Client

client = Client(auth=os.environ["NOTION_TOKEN"])
DATA_SOURCE_ID = os.environ["NOTION_DATA_SOURCE_ID"]


def push_resource(extracted: dict, source_reel_url: str, creator_handle: str = ""):
    props = {
        "Title": {"title": [{"text": {"content": extracted["title"]}}]},
        "Category": {"select": {"name": extracted["category"]}},
        "Domain Tags": {"multi_select": [{"name": t} for t in extracted.get("tags", [])]},
        "Resource Link": {"url": extracted.get("link") or None},
        "Source Reel": {"url": source_reel_url},
        "Summary": {"rich_text": [{"text": {"content": extracted.get("summary", "")}}]},
        "Creator Handle": {"rich_text": [{"text": {"content": creator_handle}}]},
        "Date Added": {"date": {"start": date.today().isoformat()}},
        "Status": {"select": {"name": "New"}},
        "Price": {"select": {"name": extracted.get("price", "Unknown")}},
        "Confidence": {"select": {"name": extracted.get("confidence", "Low")}},
    }

    return client.pages.create(
        parent={"data_source_id": DATA_SOURCE_ID},
        properties=props,
    )
