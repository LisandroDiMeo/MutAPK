package edu.uniandes.tsdl.mutapk.selector;

import java.util.ArrayList;
import java.util.List;
import java.util.HashMap;
import java.util.Collections;

import edu.uniandes.tsdl.mutapk.detectors.MutationLocationListBuilder;
import edu.uniandes.tsdl.mutapk.exception.MutAPKException;
import edu.uniandes.tsdl.mutapk.model.MutationType;
import edu.uniandes.tsdl.mutapk.model.location.MutationLocation;

public class SelectorAmountMutantsMethod implements InterfaceSelector {

    public SelectorAmountMutantsMethod() {
    }

    public List<MutationLocation> mutantSelector(HashMap<MutationType, List<MutationLocation>> locations, SelectorType selectorType) throws MutAPKException {

        SelectorAmountMutants selectorAmountMutants = (SelectorAmountMutants) selectorType;
        int newAmountMutants = selectorAmountMutants.getAmountMutants();
        List<MutationLocation> mutationLocationList = MutationLocationListBuilder.buildList(locations);

        // Check if the amount of PFLocations is lower than the requested by the user
        if (mutationLocationList.isEmpty()) {
            throw new MutAPKException("No mutants were generated.");
        }
        if (mutationLocationList.size() < newAmountMutants) {
            System.out.println("The total of mutants requested are less than the generated. Keeping all.");
            newAmountMutants = mutationLocationList.size();
        }

        Collections.shuffle(mutationLocationList);
        ArrayList<MutationLocation> randomlySelectedMutants = new ArrayList<>();

        for (int i = 0; i < newAmountMutants; i++) {
            randomlySelectedMutants.add(mutationLocationList.get(i));
        }
        return randomlySelectedMutants;
    }

}
