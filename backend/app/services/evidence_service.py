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

        nodes: List[GraphNode] = []
        report_ids: Set[str] = set()

        for idx, rep in enumerate(reports):
            r_id = rep["id"]
            report_ids.add(r_id)

            # Determine role
            if rep.get("forwarded_from"):
                role = RelationshipType.FORWARDED
            elif idx == 0:
                role = RelationshipType.ORIGINAL
            else:
                role = RelationshipType.CORROBORATING

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

        # 3. Fetch relationships (edges)
        edges: List[GraphEdge] = []
        if report_ids:
            edges_res = supabase.table("report_relationships").select("*").in_("source_report_id", list(report_ids)).execute()
            raw_edges = edges_res.data or []

            for re in raw_edges:
                # Ensure target is also in or relevant
                edges.append(
                    GraphEdge(
                        id=re["id"],
                        source=re["source_report_id"],  # later report
                        target=re["target_report_id"],  # earlier report
                        type=RelationshipType(re["type"]),
                        label=re.get("label") or f"{re['type'].capitalize()} ({re.get('confidence', 1.0):.2f})",
                        confidence=re.get("confidence", 1.0),
                    )
                )

            # If no recorded edges but multiple reports exist, link subsequent reports to original report
            if not edges and len(nodes) > 1:
                original_id = nodes[0].id
                for later_node in nodes[1:]:
                    edges.append(
                        GraphEdge(
                            id=f"edge_{later_node.id}_{original_id}",
                            source=later_node.id,
                            target=original_id,
                            type=later_node.role,
                            label=f"{later_node.role.value.capitalize()} confirmation",
                            confidence=0.85,
                        )
                    )

        return EvidenceGraphResponse(
            incident_id=incident_id,
            nodes=nodes,
            edges=edges,
        )
