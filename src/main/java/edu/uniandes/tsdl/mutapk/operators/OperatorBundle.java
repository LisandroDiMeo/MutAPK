package edu.uniandes.tsdl.mutapk.operators;

import java.io.File;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.ResourceBundle;
import java.util.Set;

import edu.uniandes.tsdl.mutapk.detectors.MutationLocationDetector;
import edu.uniandes.tsdl.mutapk.detectors.xml.ActivityNotDefinedDetector;
import edu.uniandes.tsdl.mutapk.detectors.xml.InvalidActivityNameDetector;
import edu.uniandes.tsdl.mutapk.detectors.xml.InvalidColorDetector;
import edu.uniandes.tsdl.mutapk.detectors.xml.InvalidLabelDetector;
import edu.uniandes.tsdl.mutapk.detectors.xml.MissingPermissionDetector;
import edu.uniandes.tsdl.mutapk.detectors.xml.SDKVersionDetector;
import edu.uniandes.tsdl.mutapk.detectors.xml.WrongMainActivityDetector;
import edu.uniandes.tsdl.mutapk.detectors.xml.WrongStringResourceDetector;
import edu.uniandes.tsdl.mutapk.model.MutationType;

public class OperatorBundle {

	private static final String PROPERTY_FILE_NAME = "operators";
	private ResourceBundle bundle;

//	public enum TextBasedOperator {
//		ActivityNotDefined(1), InvalidActivityName(3), InvalidColor(3), InvalidLabel(28), MissingPermission(9), WrongStringResource(10), SDKVersion(12), WrongMainActivity(8);
//
//		public int id;
//
//		TextBasedOperator(int id) {
//			this.id = id;
//		}
//	}

	public OperatorBundle(String propertyDir) throws MalformedURLException {
		init(propertyDir);
	}

	public boolean isOperatorSelected(String id) {
		return bundle.containsKey(id);
	}

	public List<MutationLocationDetector> getTextBasedDetectors() {
		List<MutationLocationDetector> textBasedDetectors = new ArrayList<>();

		if (bundle.containsKey(MutationType.ACTIVITY_NOT_DEFINED.getId() + "")) {
			textBasedDetectors.add(new ActivityNotDefinedDetector());
		}
		if (bundle.containsKey(MutationType.INVALID_ACTIVITY_PATH.getId() + "")) {
			textBasedDetectors.add(new InvalidActivityNameDetector());
		}
		if (bundle.containsKey(MutationType.INVALID_LABEL.getId() + "")) {
			textBasedDetectors.add(new InvalidLabelDetector());
		}
		if (bundle.containsKey(MutationType.WRONG_MAIN_ACTIVITY.getId() + "")) {
			textBasedDetectors.add(new WrongMainActivityDetector());
		}
		if (bundle.containsKey(MutationType.MISSING_PERMISSION_MANIFEST.getId() + "")) {
			textBasedDetectors.add(new MissingPermissionDetector());
		}
		if (bundle.containsKey(MutationType.SDK_VERSION.getId() + "")) {
			textBasedDetectors.add(new SDKVersionDetector());
		}
		if (bundle.containsKey(MutationType.WRONG_STRING_RESOURCE.getId() + "")) {
			textBasedDetectors.add(new WrongStringResourceDetector());
		}
		if (bundle.containsKey(MutationType.INVALID_COLOR.getId() + "")) {
			textBasedDetectors.add(new InvalidColorDetector());
		}

		return textBasedDetectors;
	}

	public int getAmountOfSelectedOperators() {
		return bundle.keySet().size();
	}
	

	public String printSelectedOperators() {

		Set<String> ids = bundle.keySet();
		String selectedOperators = "Id 		| MutOperatorName\n";
		selectedOperators += "----------------|--------------\n";

		for (String id : ids) {
			selectedOperators += id + " 		| " + bundle.getString(id) + "\n";
		}
		selectedOperators += "\nAmount Selected Operators: 	" + ids.size() + "\n\n";
		selectedOperators += "-------------------------------------------\n";

		return selectedOperators;
	}

	private void init(String propertyDir) throws MalformedURLException {
		File file = new File(propertyDir);
		URL url = null;
		url = file.toURI().toURL();
		URL[] urls = { url };
		ClassLoader loader = new URLClassLoader(urls);
		bundle = ResourceBundle.getBundle(PROPERTY_FILE_NAME, Locale.getDefault(), loader);
	}

}
