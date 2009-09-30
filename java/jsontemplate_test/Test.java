package jsontemplate_test;

import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;

import jsontemplate.Template;
import jsontemplate.TemplateCompileOptions;

import jsontemplate_test.org.json.JSONArray;
import jsontemplate_test.org.json.JSONException;
import jsontemplate_test.org.json.JSONObject;

public class Test {

	private static String slurp(String filename) throws IOException {
		FileReader reader = new FileReader(filename);
		StringBuilder stringBuilder = new StringBuilder();
		char[] buf = new char[8192];
		while (true) {
			int charsRead = reader.read(buf);
			if (charsRead < 0)
				break;
			stringBuilder.append(buf, 0, charsRead);
		}
		return stringBuilder.toString();
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		if (args.length != 1) {
			System.err
					.println("args: name of json file containing keys: template, options, dictionary");
			System.exit(1);
		}
		try {
			String s = slurp(args[0]);
			System.err.println(s);
			JSONObject obj = new JSONObject(s);
			String template = (String) obj.get("template");
			JSONObject optionsDict = (JSONObject) obj.get("options");
			Object dictionary = obj.get("dictionary");
			TemplateCompileOptions options = new TemplateCompileOptions();
			if (optionsDict.has("meta")) {
				options.setMeta(optionsDict.getString("meta"));
			}
			if (optionsDict.has("default_formatter")) {
				Object defaultFormatter = optionsDict.get("default_formatter");
				if (JSONObject.NULL.equals(defaultFormatter)) {
					options.setDefaultFormatter(null);
				} else {
					options.setDefaultFormatter(defaultFormatter.toString());
				}
			}
			if (optionsDict.has("format_char")) {
				char formatChar = optionsDict.getString("format_char").charAt(0);
				options.setFormatChar(formatChar);
			}
			System.out.print(new Template(template, null, options)
					.expand(convertObject(dictionary)));
		} catch (Exception e) {
			System.err.println("EXCEPTION: " + e.getClass().getSimpleName());
			e.printStackTrace();
			System.exit(1);
		}
	}

	private static HashMap<String, Object> jsonObjectToHash(JSONObject obj) {
		HashMap<String, Object> dictionaryMap = new HashMap<String, Object>();
		for (Iterator iterator = obj.keys(); iterator.hasNext();) {
			String key = (String) iterator.next();
			Object value;
			try {
				value = obj.get(key);
				dictionaryMap.put(key, convertObject(value));
			} catch (JSONException e) {
			}
		}
		return dictionaryMap;
	}

	private static Object convertObject(Object value) {
		if (value instanceof JSONArray) {
			return jsonArrayToList((JSONArray) value);
		} else if (JSONObject.NULL.equals(value)) {
			return null;
		}
		else if (value instanceof JSONObject) {
			return jsonObjectToHash((JSONObject) value);
		}
		else {
			return value;
		}
	}

	private static List<Object> jsonArrayToList(JSONArray value) {
		int length = value.length();
		ArrayList<Object> result = new ArrayList<Object>(length);
		for (int i = 0; i < length; i++) {
			try {
				result.add(convertObject(value.get(i)));
			} catch (JSONException e) {
			}
		}
		return result;
	}

}
