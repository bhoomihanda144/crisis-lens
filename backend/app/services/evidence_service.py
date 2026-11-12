"""
CrisisLens Evidence Relationship Graph Service
Implements GET /incidents/{id}/evidence-graph per API Contract v1.0 Section 4.8.
Node ID equals the Report ID.
Edges point from the later/derived report (source) to the earlier/reference report (target).
"""
from typing import List, Dict, Any, Set
from app.database.supabase_client import get_supabase_client
from app.schemas.evidence import EvidenceGraphResponse, GraphNode, GraphEdge
from app.schemas.common import SourceType, FreshnessStatus, RelationshipType
from app.utils.datetime_utils import calculate_freshness
from app.core.exceptions import NotFoundException


class EvidenceService:
    @staticmethod
    def get_evidence_graph(incident_id: str) -> EvidenceGraphResponse:
        supabase = get_supabase_client()

        # 1. Verify incident exists
        inc_res = supabase.table("incidents").select("*").eq("id", incident_id).limit(1).execute()
        if not inc_res.data:
            raise NotFoundException("Incident", incident_id)

        # 2. Fetch associated reports
        rep_res = supabase.table("reports").select("*").eq("incident_id", incident_id).order("reported_at", desc=False).execute()
        reports = rep_res.data or []

        # If no reports directly linked, check reports near same location or recent
        if not reports:
            inc_loc = inc_res.data[0].get("location_label", "")
            rep_res = supabase.table("reports").select("*").ilike("location_label", f"%{inc_loc[:10]}%").order("reported_at", desc=False).limit(10).execute()
            reports = rep_res.data or []

        # 3. Fetch ALL stored relationships where either endpoint is in this incident's reports
        all_report_ids: Set[str] = set(rep["id"] for rep in reports)

        # Build role map from stored relationships before building nodes
        # Keys: report_id → role string derived from stored data
        role_map: Dict[str, RelationshipType] = {}
        raw_edges_data: List[Dict[str, Any]] = []
        if all_report_ids:
            # Fetch edges where this report is the source (later/derived)
            src_res = supabase.table("report_relationships").select("*").in_(
                "source_report_id", list(all_report_ids)
            ).execute()
            raw_edges_data.extend(src_res.data or [])

            # Fetch edges where this report is the target (earlier/reference)
            tgt_res = supabase.table("report_relationships").select("*").in_(
                "target_report_id", list(all_report_ids)
            ).execute()
            # Avoid duplicates
            seen_ids = {e["id"] for e in raw_edges_data}
            for e in (tgt_res.data or []):
                if e["id"] not in seen_ids:
                    raw_edges_data.append(e)

            # Derive role from stored relationship type
            for e in raw_edges_data:
                src_id = e["source_report_id"]
                rel_type = e["type"]
                if rel_type == "forwarded":
                    role_map[src_id] = RelationshipType.FORWARDED
                elif rel_type == "duplicate":
                    if src_id not in role_map:
                        role_map[src_id] = RelationshipType.DUPLICATE
                elif rel_type == "corroborating":
                    if src_id not in role_map:
                        role_map[src_id] = RelationshipType.CORROBORATING
                elif rel_type == "conflicting":
                    if src_id not in role_map:
                        role_map[src_id] = RelationshipType.CONFLICTING

        nodes: List[GraphNode] = []
        report_ids: Set[str] = set()

        for rep in reports:
            r_id = rep["id"]
            report_ids.add(r_id)

            # Determine role: forwarded_from field always wins
            if rep.get("forwarded_from"):
                role = RelationshipType.FORWARDED
            elif r_id in role_map:
                role = role_map[r_id]
            else:
                # Only mark as original if not classified by any stored relationship.
                # We cannot assume corroboration from chronological order.
                role = RelationshipType.ORIGINAL

            # Freshness
            freshness = calculate_freshness(rep["reported_at"])
            fresh_status = FreshnessStatus(freshness["status"])

            # Excerpt
            txt = rep.get("text", "")
            excerpt = (txt[:60] + "...") if len(txt) > 60 else txt

            node = GraphNode(
                id=r_id,
                report_id=r_id,
                label=f"{rep['source_type'].capitalize()}: {rep['location_label']}",
                role=role,
                source_type=SourceType(rep["source_type"]),
                source_name=rep["source_name"],
                timestamp=rep["reported_at"],
                excerpt=excerpt,
                freshness_status=fresh_status,
            )
            nodes.append(node)

        # Build edges from actual stored relationships only — never invent edges
        edges: List[GraphEdge] = []
        for re in raw_edges_data:
            # Only include edges where both endpoints belong to this incident's reports
            # (target may be outside the set for forwarded_from refs; include anyway for provenance)
            edges.append(
                GraphEdge(
                    id=re["id"],
                    source=re["source_report_id"],  # later/derived report
                    target=re["target_report_id"],  # earlier/reference report
                    type=RelationshipType(re["type"]),
                    label=re.get("label") or f"{re['type'].capitalize()} ({re.get('confidence', 1.0):.2f})",
                    confidence=re.get("confidence", 1.0),
                )
            )
        # NOTE: If no stored relationships exist, edges remains [] — this is correct behavior.

        return EvidenceGraphResponse(
            incident_id=incident_id,
            nodes=nodes,
            edges=edges,
        )
