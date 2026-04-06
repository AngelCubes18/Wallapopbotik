"""
Gestión persistente de alertas y productos ya notificados.
Guarda todo en un JSON local (data.json).
"""
import json
import os
import uuid
from typing import Optional


class Storage:
    def __init__(self, filepath: str = "data.json"):
        self.filepath = filepath
        self._data    = self._load()

    # ── Persistencia ──────────────────────────────────────────────────────────
    def _load(self) -> dict:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"alerts": [], "seen": {}}

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    # ── Alertas ───────────────────────────────────────────────────────────────
    def add_alert(
        self,
        channel_id : int,
        keyword    : str,
        min_price  : Optional[float] = None,
        max_price  : Optional[float] = None,
    ) -> str:
        alert_id = str(uuid.uuid4())[:8]
        self._data["alerts"].append({
            "id"         : alert_id,
            "channel_id" : channel_id,
            "keyword"    : keyword.strip().lower(),
            "min_price"  : min_price,
            "max_price"  : max_price,
        })
        self._save()
        return alert_id

    def get_alerts(self) -> list[dict]:
        return list(self._data.get("alerts", []))

    def remove_alert(self, alert_id: str) -> bool:
        before = len(self._data["alerts"])
        self._data["alerts"] = [a for a in self._data["alerts"] if a["id"] != alert_id]
        # Limpiar también los "seen" de esa alerta
        self._data["seen"].pop(alert_id, None)
        if len(self._data["alerts"]) < before:
            self._save()
            return True
        return False

    # ── Productos ya vistos ───────────────────────────────────────────────────
    def filter_new(self, alert_id: str, items: list[dict]) -> list[dict]:
        """
        Recibe la lista de items de Wallapop y devuelve solo los que
        no se han notificado antes para esta alerta.
        Actualiza la memoria interna y guarda.
        """
        seen = self._data["seen"].setdefault(alert_id, [])
        new_items = [item for item in items if item["id"] not in seen]

        if new_items:
            seen.extend(item["id"] for item in new_items)
            # Mantener solo los últimos 500 IDs por alerta para no crecer infinitamente
            self._data["seen"][alert_id] = seen[-500:]
            self._save()

        return new_items
