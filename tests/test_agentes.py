import unittest

from ocean_turnos.agents import coordinator, economy, navigation, safety
from ocean_turnos.contract import Proposal, set_speed
from ocean_turnos.graph import deliberate
from ocean_turnos.pack import parse_pack
from ocean_turnos.tools import fuel
from tests import fakes


class TestFerramentas(unittest.TestCase):
    def test_consumo_cubico(self):
        a = fuel.burn_t_per_tick(1.2, 0.0, 14, load_factor=1.0)
        b = fuel.burn_t_per_tick(1.2, 0.0, 12, load_factor=1.0)
        self.assertAlmostEqual(a, 0.2)
        self.assertAlmostEqual(b / a, (12 / 14) ** 3)

    def test_compra_multiplo_de_5_e_limitada(self):
        self.assertEqual(fuel.purchase_to_cover(30, 20, 33, 0, max_quantity_t=80), 50)
        self.assertEqual(fuel.purchase_to_cover(300, 20, 33, 0, max_quantity_t=82), 80)
        self.assertEqual(fuel.purchase_to_cover(10, 60, 33, 0, max_quantity_t=80), 0)


class TestEconomia(unittest.TestCase):
    def test_compra_na_origem_quando_falta(self):
        view = parse_pack(fakes.pack(ships={"S1-FAROL": fakes.ship(fuel_milli=30_000)}))
        props = [p for p in economy.propose(view) if p.ship_id == "S1-FAROL"]
        self.assertEqual(len(props), 1)
        self.assertEqual(props[0].action["type"], "BUY_FUEL")
        self.assertEqual(props[0].action["quantity_t"] % 5, 0)

    def test_nao_compra_com_tanque_suficiente(self):
        view = parse_pack(fakes.pack(ships={"S1-FAROL": fakes.ship(fuel_milli=140_000)}))
        self.assertFalse([p for p in economy.propose(view) if p.ship_id == "S1-FAROL"])


class TestNavegacao(unittest.TestCase):
    def test_tempestade_no_trecho_exposto_reduz_para_12(self):
        view = parse_pack(fakes.pack(tick=125, events=[fakes.storm()],
                                     ships={"S1-FAROL": fakes.underway(in_exposed_segment_now=True)}))
        prop = next(p for p in navigation.propose(view) if p.ship_id == "S1-FAROL")
        self.assertEqual(prop.action, {"type": "SET_SPEED", "speed_kn": "12.00"})

    def test_sem_mudanca_nao_repete_comando(self):
        view = parse_pack(fakes.pack(ships={"S1-FAROL": fakes.underway()}))
        self.assertFalse([p for p in navigation.propose(view) if p.ship_id == "S1-FAROL"])

    def test_pane_e04_hold_depois_reparo(self):
        faulty = fakes.underway(e04_active=True, active_limit_speed_kn="10.00")
        moving = parse_pack(fakes.pack(ships={"S4-ATLAS": faulty}))
        self.assertEqual(next(p for p in navigation.propose(moving) if p.ship_id == "S4-ATLAS").action["type"], "HOLD")
        stopped = fakes.underway(e04_active=True, ship_state="HOLDING", effective_speed_kn="0.00",
                                 allowed_actions_now=[{"action": "REPAIR", "constraints": {}}])
        view = parse_pack(fakes.pack(ships={"S4-ATLAS": stopped}))
        self.assertEqual(next(p for p in navigation.propose(view) if p.ship_id == "S4-ATLAS").action["type"], "REPAIR")


class TestSeguranca(unittest.TestCase):
    def _review(self, action, **ship_over):
        view = parse_pack(fakes.pack(events=[fakes.storm()], ships={"S1-FAROL": fakes.underway(**ship_over)}))
        return safety.review(Proposal("S1-FAROL", "navigation", action, "x"), view)

    def test_veta_acao_nao_permitida(self):
        r = self._review({"type": "BUY_FUEL", "quantity_t": 20})
        self.assertFalse(r.approved)
        self.assertEqual(r.codes, ["NOT_ALLOWED_NOW"])

    def test_veta_velocidade_insegura_na_tempestade(self):
        r = self._review(set_speed(1400), in_exposed_segment_now=True, target_speed_kn="12.00")
        self.assertEqual(r.codes, ["STORM_UNSAFE_SPEED"])

    def test_veta_risco_de_combustivel(self):
        r = self._review(set_speed(1800), fuel_milli=34_000)
        self.assertEqual(r.codes, ["FUEL_RESERVE_RISK"])

    def test_aprova_ajuste_seguro(self):
        self.assertTrue(self._review(set_speed(1200)).approved)


class TestCoordenador(unittest.TestCase):
    def test_tick0_compra_e_nao_manda_velocidade_junto(self):
        doc = deliberate(fakes.pack(ships={"S1-FAROL": fakes.ship(fuel_milli=30_000)}))
        s1 = [d for d in doc["decisions"] if d["ship_id"] == "S1-FAROL"]
        self.assertEqual([d["action"]["type"] for d in s1], ["BUY_FUEL"])
        self.assertTrue(all(d["proposed_by"] != d["reviewed_by"] for d in doc["decisions"]))
        self.assertTrue(doc["stop_on_events"])

    def test_navio_com_combustivel_zarpa(self):
        doc = deliberate(fakes.pack(ships={"S2-MARE": fakes.ship(fuel_milli=140_000)}))
        s2 = [d["action"] for d in doc["decisions"] if d["ship_id"] == "S2-MARE"]
        self.assertEqual(s2, [{"type": "SET_SPEED", "speed_kn": "14.00"}])

    def test_caixa_insuficiente_vira_veto(self):
        view = parse_pack(fakes.pack(available_cent=1_000_000,
                                     ships={sid: fakes.ship(fuel_milli=30_000) for sid in ("S1-FAROL", "S2-MARE")}))
        _, reviewed = coordinator.decide(view)
        fuel_reviews = [r for p, r in reviewed if p.action["type"] == "BUY_FUEL"]
        self.assertTrue(any(r.codes == ["CASH_LIMIT"] for r in fuel_reviews))

    def test_advance_ticks_no_fim_da_rodada(self):
        doc = deliberate(fakes.pack(tick=425), advance_ticks_max=50)
        self.assertEqual(doc["advance_ticks"], 7)


if __name__ == "__main__":
    unittest.main()
