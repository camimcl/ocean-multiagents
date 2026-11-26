import unittest

from ocean_turnos.contract import buy_fuel, set_speed, validate_action, validate_decision_doc


def doc(**over):
    decision = {"ship_id": "S1-FAROL", "proposed_by": "economy", "proposal_rationale": "x",
                "reviewed_by": "safety", "review_result": "approved", "review_rationale": "y",
                "action": buy_fuel(20)}
    decision.update(over)
    return {"advance_ticks": 25, "stop_on_events": True, "decisions": [decision]}


class TestContract(unittest.TestCase):
    def test_documento_valido(self):
        self.assertEqual(validate_decision_doc(doc()), [])

    def test_lista_vazia_e_so_avancar(self):
        self.assertEqual(validate_decision_doc({"advance_ticks": 1, "stop_on_events": True, "decisions": []}), [])

    def test_propositor_igual_revisor(self):
        self.assertIn("decisions[0]:SAME_PROPOSER_AND_REVIEWER", validate_decision_doc(doc(reviewed_by="economy")))

    def test_advance_ticks_fora_da_faixa(self):
        bad = doc()
        bad["advance_ticks"] = 0
        self.assertIn("INVALID_ADVANCE_TICKS", validate_decision_doc(bad))

    def test_navio_invalido_e_justificativa_vazia(self):
        problems = validate_decision_doc(doc(ship_id="S9-X", review_rationale=" "))
        self.assertIn("decisions[0]:INVALID_SHIP", problems)
        self.assertIn("decisions[0]:EMPTY_REVIEW_RATIONALE", problems)

    def test_acoes(self):
        self.assertEqual(validate_action({"type": "SET_SPEED", "speed_kn": "12.50"}), [])
        self.assertEqual(validate_action({"type": "SET_SPEED", "speed_kn": "18.50"}), ["INVALID_SPEED"])
        self.assertEqual(validate_action({"type": "SET_SPEED", "speed_kn": 12}), ["INVALID_SPEED"])
        self.assertEqual(validate_action({"type": "BUY_FUEL", "quantity_t": 12}), ["INVALID_FUEL_QUANTITY"])
        self.assertEqual(validate_action({"type": "DEPLOY"}), ["UNKNOWN_ACTION:DEPLOY"])
        self.assertEqual(validate_action({"type": "HOLD", "reason_code": "E04_ENGINE_FAULT", "x": 1}),
                         ["INVALID_ARGUMENTS:HOLD"])

    def test_set_speed_arredonda_no_passo(self):
        self.assertEqual(set_speed(1275)["speed_kn"], "12.50")
        self.assertEqual(set_speed(2500)["speed_kn"], "18.00")


if __name__ == "__main__":
    unittest.main()
