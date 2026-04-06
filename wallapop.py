"""
Módulo para consultar Wallapop usando wallapy 0.5.1
"""
from typing import Optional
from wallapy import WallaPyClient


class WallapopClient:
    def __init__(self):
        self._client = WallaPyClient()

    async def search(
        self,
        keyword   : str,
        min_price : Optional[float] = None,
        max_price : Optional[float] = None,
        max_items : int = 20,
    ) -> list[dict]:

        # En wallapy 0.5.1 check_wallapop es un método async
        results = await self._client.check_wallapop(
            product_name    = keyword,
            min_price       = int(min_price) if min_price is not None else None,
            max_price       = int(max_price) if max_price is not None else None,
            max_total_items = max_items,
            order_by        = "newest",
        )

        if not results:
            return []

        items = []
        for r in results:
            items.append({
                "id"          : str(r.get("id") or r.get("itemId") or hash(r.get("title", ""))),
                "title"       : r.get("title", "Sin título"),
                "description" : r.get("description", ""),
                "price"       : r.get("price"),
                "url"         : r.get("link") or r.get("url", ""),
                "image"       : r.get("image") or r.get("thumbnail") or r.get("pictures", [None])[0],
                "location"    : r.get("location", "—"),
                "seller"      : r.get("seller") or r.get("user", "—"),
            })
        return items