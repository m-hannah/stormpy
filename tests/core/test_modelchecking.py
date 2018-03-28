import stormpy
import stormpy.logic
from helpers.helper import get_example_path

import math


class TestModelChecking:
    def test_model_checking_prism_dtmc(self):
        program = stormpy.parse_prism_program(get_example_path("dtmc", "die.pm"))
        formulas = stormpy.parse_properties_for_prism_program("P=? [ F \"one\" ]", program)
        model = stormpy.build_model(program, formulas)
        assert model.nr_states == 13
        assert model.nr_transitions == 20
        assert len(model.initial_states) == 1
        initial_state = model.initial_states[0]
        assert initial_state == 0
        result = stormpy.model_checking(model, formulas[0])
        assert math.isclose(result.at(initial_state), 0.16666666666666663)

    def test_model_checking_prism_mdp(self):
        program = stormpy.parse_prism_program(get_example_path("mdp", "coin2-2.nm"))
        formulas = stormpy.parse_properties_for_prism_program("Pmin=? [ F \"finished\" & \"all_coins_equal_1\"]", program)
        model = stormpy.build_model(program, formulas)
        assert model.nr_states == 272
        assert model.nr_transitions == 492
        assert len(model.initial_states) == 1
        initial_state = model.initial_states[0]
        assert initial_state == 0
        result = stormpy.model_checking(model, formulas[0])
        assert math.isclose(result.at(initial_state), 0.3828117384)


    def test_model_checking_jani_dtmc(self):
        jani_model, properties = stormpy.parse_jani_model(get_example_path("dtmc", "die.jani"))
        formula = properties["Probability to throw a six"]
        model = stormpy.build_model(jani_model, [formula])
        assert model.nr_states == 13
        assert model.nr_transitions == 20
        assert len(model.initial_states) == 1
        initial_state = model.initial_states[0]
        assert initial_state == 0
        result = stormpy.model_checking(model, formula)
        assert math.isclose(result.at(initial_state), 0.16666666666666663)

    def test_model_checking_jani_dtmc(self):
        jani_model, properties = stormpy.parse_jani_model(get_example_path("dtmc", "die.jani"))
        formula = properties["Expected number of coin flips"]
        model = stormpy.build_model(jani_model, [formula])
        assert model.nr_states == 13
        assert model.nr_transitions == 20
        assert len(model.initial_states) == 1
        initial_state = model.initial_states[0]
        assert initial_state == 0
        # Unsupported formula yields None result
        result = stormpy.model_checking(model, formula)
        assert result is None

    def test_model_checking_dtmc_all_labels(self):
        program = stormpy.parse_prism_program(get_example_path("dtmc", "die.pm"))
        formulas = stormpy.parse_properties_for_prism_program("P=? [ F \"one\" ]", program)
        model = stormpy.build_model(program)
        assert model.nr_states == 13
        assert model.nr_transitions == 20
        assert len(model.initial_states) == 1
        initial_state = model.initial_states[0]
        assert initial_state == 0
        result = stormpy.model_checking(model, formulas[0])
        assert math.isclose(result.at(initial_state), 0.16666666666666663)
        formulas = stormpy.parse_properties_for_prism_program("P=? [ F \"two\" ]", program)
        result = stormpy.model_checking(model, formulas[0])
        assert math.isclose(result.at(initial_state), 0.16666666666666663)

    def test_model_checking_all_dtmc(self):
        program = stormpy.parse_prism_program(get_example_path("dtmc", "die.pm"))
        formulas = stormpy.parse_properties_for_prism_program("P=? [ F \"one\" ]", program)
        model = stormpy.build_model(program, formulas)
        assert model.nr_states == 13
        assert model.nr_transitions == 20
        result = stormpy.model_checking(model, formulas[0])
        assert result.result_for_all_states
        reference = [0.16666666666666663, 0.3333333333333333, 0, 0.6666666666666666, 0, 0, 0, 1, 0, 0, 0, 0, 0]
        assert all(map(math.isclose, result.get_values(), reference))

    def test_model_checking_only_initial(self):
        program = stormpy.parse_prism_program(get_example_path("dtmc", "die.pm"))
        formulas = stormpy.parse_properties_for_prism_program("Pmax=? [F{\"coin_flips\"}<=3 \"one\"]", program)
        model = stormpy.build_model(program, formulas)
        assert len(model.initial_states) == 1
        initial_state = model.initial_states[0]
        assert initial_state == 0
        result = stormpy.model_checking(model, formulas[0], only_initial_states=True)
        assert not result.result_for_all_states
        assert math.isclose(result.at(initial_state), 0.125)

    def test_model_checking_prob01(self):
        program = stormpy.parse_prism_program(get_example_path("dtmc", "die.pm"))
        formulaPhi = stormpy.parse_properties("true")[0]
        formulaPsi = stormpy.parse_properties("\"six\"")[0]
        model = stormpy.build_model(program, [formulaPsi])
        phiResult = stormpy.model_checking(model, formulaPhi)
        phiStates = phiResult.get_truth_values()
        assert phiStates.number_of_set_bits() == model.nr_states
        psiResult = stormpy.model_checking(model, formulaPsi)
        psiStates = psiResult.get_truth_values()
        assert psiStates.number_of_set_bits() == 1
        (prob0, prob1) = stormpy.compute_prob01_states(model, phiStates, psiStates)
        assert prob0.number_of_set_bits() == 9
        assert prob1.number_of_set_bits() == 1
        (prob0, prob1) = stormpy.compute_prob01min_states(model, phiStates, psiStates)
        assert prob0.number_of_set_bits() == 9
        assert prob1.number_of_set_bits() == 1
        (prob0, prob1) = stormpy.compute_prob01max_states(model, phiStates, psiStates)
        assert prob0.number_of_set_bits() == 9
        assert prob1.number_of_set_bits() == 1
        labelprop = stormpy.core.Property("cora", formulaPsi.raw_formula)
        result = stormpy.model_checking(model, labelprop)
        assert result.get_truth_values().number_of_set_bits() == 1

    def test_model_checking_ctmc(self):
        model = stormpy.build_model_from_drn(get_example_path("ctmc", "dft.drn"))
        formulas = stormpy.parse_properties("T=? [ F \"failed\" ]")
        assert model.nr_states == 16
        assert model.nr_transitions == 33
        assert len(model.initial_states) == 1
        initial_state = model.initial_states[0]
        assert initial_state == 0
        result = stormpy.model_checking(model, formulas[0])
        assert math.isclose(result.at(initial_state), 4.166666667)
