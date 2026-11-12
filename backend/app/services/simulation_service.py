"""
CrisisLens What-If Emergency Simulation Service
Implements POST /simulate per API Contract v1.0 Section 4.9.
Strictly isolated from live emergency records.
"""
from typing import List
from app.database.supabase_client import get_supabase_client
from app.schemas.simulation import (
    SimulationRequest,
    SimulationResponse,
    SimulationResults,
    ResourceDemand,
    ResourceShortage,
    PriorityChange,
)
from app.utils.id_generator import generate_simulation_id
from app.utils.datetime_utils import now_utc_iso


class SimulationService:
    @staticmethod
    def run_simulation(payload: SimulationRequest) -> SimulationResponse:
        supabase = get_supabase_client()
        sim_id = generate_simulation_id()
        generated_at = now_utc_iso()

        # 1. Compute resource demand based on parameters
        # Scale demand according to population and disaster severity
        demanded_teams = max(2, int((payload.affected_population / 1500.0) * (payload.disaster_severity / 2.5)))
        demanded_ambulances = max(2, int((payload.affected_population / 2000.0) * (payload.disaster_severity / 2.0)))

        # 2. Compute shortages
        shortages: List[ResourceShortage] = []
        team_shortfall = max(0, demanded_teams - payload.rescue_teams)
        if team_shortfall > 0:
            shortages.append(
                ResourceShortage(
                    resource="rescue_teams",
                    required=demanded_teams,
                    available=payload.rescue_teams,
                    shortfall=team_shortfall,
                )
            )

        amb_shortfall = max(0, demanded_ambulances - payload.available_ambulances)
        if amb_shortfall > 0:
            shortages.append(
                ResourceShortage(
                    resource="ambulances",
                    required=demanded_ambulances,
                    available=payload.available_ambulances,
                    shortfall=amb_shortfall,
                )
            )

        # 3. Estimated response delay
        # Each blocked road adds ~4-5 minutes, each missing team adds ~2-3 minutes
        delay_minutes = (payload.blocked_roads * 5) + (team_shortfall * 2)

        # 4. Priority changes under this scenario
        # Use real incidents from the database — never hardcode incident IDs or titles
        priority_changes: List[PriorityChange] = []
        try:
            incidents_res = supabase.table("incidents").select("id, title, location_label, severity").execute()
            live_incidents = incidents_res.data or []

            if live_incidents and (payload.blocked_roads > 0 or team_shortfall > 0):
                # Fetch stored priority scores so we can base ranks on real urgency
                inc_ids = [i["id"] for i in live_incidents]
                scores_res = supabase.table("priority_scores").select("incident_id, urgency_score").in_(
                    "incident_id", inc_ids
                ).execute()
                scores_map = {s["incident_id"]: s["urgency_score"] for s in (scores_res.data or [])}

                # Assign baseline urgency score (fallback to severity-based heuristic)
                severity_fallback = {"critical": 90, "high": 70, "medium": 50, "low": 25}
                ranked = sorted(
                    live_incidents,
                    key=lambda i: scores_map.get(i["id"], severity_fallback.get(i.get("severity", "medium"), 50)),
                    reverse=True,
                )

                for baseline_rank, inc in enumerate(ranked, start=1):
                    # Scenario: blocked roads raise urgency of incidents that need fast access
                    # team shortage raises priority of incidents needing most personnel
                    base_score = scores_map.get(inc["id"], severity_fallback.get(inc.get("severity", "medium"), 50))
                    # Penalty if roads are blocked (harder to reach high-urgency sites)
                    road_penalty = payload.blocked_roads * 5
                    # Penalty if teams are short (high-urgency incidents compete harder)
                    team_penalty = team_shortfall * 3
                    scenario_score = max(0, base_score - road_penalty - team_penalty)

                    # Only emit a priority_change entry when the scenario meaningfully shifts rank
                    if road_penalty > 0 or team_penalty > 0:
                        # Recalculate scenario rank order
                        scenario_scores = {
                            i["id"]: max(0, scores_map.get(i["id"], severity_fallback.get(i.get("severity", "medium"), 50))
                                         - payload.blocked_roads * 5 - team_shortfall * 3)
                            for i in ranked
                        }
                        scenario_ranked = sorted(ranked, key=lambda i: scenario_scores[i["id"]], reverse=True)
                        scenario_rank = next(
                            (idx + 1 for idx, si in enumerate(scenario_ranked) if si["id"] == inc["id"]), baseline_rank
                        )
                        if scenario_rank != baseline_rank:
                            reasons = []
                            if payload.blocked_roads > 0:
                                reasons.append(f"{payload.blocked_roads} road(s) blocked, slowing access")
                            if team_shortfall > 0:
                                reasons.append(f"Rescue team shortfall of {team_shortfall}")
                            priority_changes.append(
                                PriorityChange(
                                    incident_id=inc["id"],
                                    title=inc["title"],
                                    baseline_rank=baseline_rank,
                                    scenario_rank=scenario_rank,
                                    reason="; ".join(reasons),
                                )
                            )
        except Exception:
            # DB unavailable during simulation — return no priority changes (never invent them)
            priority_changes = []

        # 5. Scenario summary
        if shortages:
            parts = [f"{s.resource.replace('_', ' ')} are short by {s.shortfall}" for s in shortages]
            summary = f"{', '.join(parts).capitalize()} under this scenario. Estimated response delay: {delay_minutes} minutes."
        else:
            summary = f"All resource demands satisfied under this scenario. Estimated response delay: {delay_minutes} minutes."

        results = SimulationResults(
            resource_demand=ResourceDemand(
                rescue_teams=demanded_teams,
                ambulances=demanded_ambulances,
            ),
            shortages=shortages,
            estimated_response_delay_minutes=delay_minutes,
            priority_changes=priority_changes,
            summary=summary,
        )

        response_obj = SimulationResponse(
            scenario_id=sim_id,
            is_simulation=True,
            generated_at=generated_at,
            inputs=payload,
            results=results,
        )

        # 6. Persist to simulations table (Isolated storage)
        sim_row = {
            "id": sim_id,
            "scenario_name": payload.scenario_name,
            "is_simulation": True,
            "generated_at": generated_at,
            "inputs": payload.model_dump(mode="json"),
            "results": results.model_dump(mode="json"),
        }
        try:
            supabase.table("simulations").insert(sim_row).execute()
        except Exception:
            pass

        return response_obj
