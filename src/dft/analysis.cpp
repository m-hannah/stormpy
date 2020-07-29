#include "analysis.h"

#include "storm-dft/parser/DFTJsonParser.h"
#include "storm-dft/builder/ExplicitDFTModelBuilder.h"
#include "storm-dft/storage/dft/DFTIsomorphism.h"
#include "storm-dft/api/storm-dft.h"



// Thin wrapper for DFT analysis
template<typename ValueType>
//std::vector<ValueType> analyzeDFT(storm::storage::DFT<ValueType> const& dft, std::vector<std::shared_ptr<storm::logic::Formula const>> const& properties, bool symred, bool allowModularisation, std::set<size_t> const& relevantEvents = {}, double approximationError = 0.0, storm::builder::ApproximationHeuristic approximationHeuristic = storm::builder::ApproximationHeuristic::DEPTH) {
std::vector<ValueType> analyzeDFT(storm::storage::DFT<ValueType> const& dft, std::vector<std::shared_ptr<storm::logic::Formula const>> const& properties, bool symred, bool allowModularisation, std::set<size_t> const& relevantEvents, bool allowDCForRelevant) {
    typename storm::modelchecker::DFTModelChecker<ValueType>::dft_results dftResults = storm::api::analyzeDFT(dft, properties, symred, allowModularisation, relevantEvents, allowDCForRelevant, 0.0, storm::builder::ApproximationHeuristic::DEPTH, false);

    std::vector<ValueType> results;
    for (auto result : dftResults) {
        results.push_back(boost::get<ValueType>(result));
    }
    return results;
}


// Define python bindings
void define_analysis(py::module& m) {

    m.def("analyze_dft", &analyzeDFT<double>, "Analyze the DFT", py::arg("dft"), py::arg("properties"), py::arg("symred")=true, py::arg("allow_modularisation")=false, py::arg("relevant_events")=std::set<size_t>(), py::arg("dc_for_relevant")=false);

    m.def("transform_dft", &storm::api::applyTransformations<double>, "Apply transformations on DFT", py::arg("dft"), py::arg("unique_constant_be"), py::arg("binary_fdeps"));

    m.def("is_well_formed", &storm::api::isWellFormed<double>, "Check whether DFT is well-formed.", py::arg("dft"), py::arg("check_valid_for_analysis") = true);

    m.def("compute_relevant_events", &storm::api::computeRelevantEvents<double>, "Compute relevant event ids from properties and additional relevant names", py::arg("dft"), py::arg("properties"), py::arg("additional_relevant_names") = std::vector<std::string>());
}
