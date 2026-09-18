"""HTTP facade for the connected cockpit; no separate financial engine."""
from fastapi import Body

from .cockpit_workspace import CockpitWorkspace
from .cockpit_simulations import CockpitSimulations


def install_routes(api, decision):
    cockpit = CockpitWorkspace(decision)
    decision.work.cockpit = cockpit
    api.state.cockpit = cockpit
    simulations = CockpitSimulations(decision)
    api.state.cockpit_simulations = simulations
    prefix = '/api/cases/{case_id}/cockpit'

    @api.get(prefix + '/catalog')
    def catalog(case_id: str):
        return cockpit.catalog(case_id)

    @api.get(prefix + '/sheets/{sheet_id}')
    def sheet(case_id: str, sheet_id: str, offset: int = 0, limit: int = 100):
        return cockpit.sheet(case_id, sheet_id, offset, limit)

    @api.get(prefix + '/sheets/{sheet_id}/outputs')
    def outputs(case_id: str, sheet_id: str):
        return cockpit.outputs(case_id, sheet_id)

    @api.post(prefix + '/answers')
    def answers(case_id: str, body: dict = Body(...)):
        return cockpit.answers(case_id, body)

    @api.get(prefix + '/cells')
    def cells(case_id: str, sheet: str, row: int = 1, column: int = 1, rows: int = 100, columns: int = 26):
        return cockpit.cells(case_id, sheet, row, column, rows, columns)

    @api.post(prefix + '/operations')
    def operations(case_id: str, body: dict = Body(...)):
        return cockpit.operations(case_id, body)

    @api.post(prefix + '/sheets/{sheet_id}/records')
    def record(case_id: str, sheet_id: str, body: dict = Body(...)):
        return cockpit.record(case_id, sheet_id, body)

    @api.get(prefix + '/draft/impacts')
    def impacts(case_id: str):
        return simulations.impacts(case_id)

    @api.get(prefix + '/simulations')
    def list_simulations(case_id: str):
        return simulations.list(case_id)

    @api.post(prefix + '/simulations')
    def simulate(case_id: str, body: dict = Body(...)):
        return simulations.submit(case_id, body)

    @api.get(prefix + '/simulations/{simulation_id}')
    def simulation(case_id: str, simulation_id: str):
        return simulations.get(case_id, simulation_id)

    @api.post(prefix + '/simulations/{simulation_id}/keep')
    def keep(case_id: str, simulation_id: str, body: dict = Body(...)):
        return simulations.keep(case_id, simulation_id, body)

    @api.post(prefix + '/simulations/{simulation_id}/propose-adoption')
    def propose_adoption(case_id: str, simulation_id: str, body: dict = Body(...)):
        return simulations.propose_adoption(case_id, simulation_id, body)

    return cockpit
