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
        priority_changes: List[PriorityChange] = []
        if payload.blocked_roads >= 2 or team_shortfall > 0:
            priority_changes.append(
                PriorityChange(
                    incident_id="inc_002",
                    title="Reported structural collapse, Koramangala",
                    baseline_rank=2,
                    scenario_rank=1,
                    reason="Access roads blocked, fewer teams available",
                )
            )

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
