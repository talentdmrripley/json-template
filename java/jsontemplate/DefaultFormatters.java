package jsontemplate;

import java.util.HashMap;

public class DefaultFormatters {

	private static HashMap<String, IFormatter> LOOKUP = new HashMap<String, IFormatter>();
	static {
		LOOKUP.put("str", new StrFormatter());
		LOOKUP.put("raw", new RawFormatter());
		LOOKUP.put("html", new HtmlFormatter());
		LOOKUP.put("html-attr-value", new HtmlAttrValueFormatter());
		LOOKUP.put("htmltag", new HtmlTagFormatter());
	}

	public static IFormatter get(String formatterName) {
		return LOOKUP.get(formatterName);
	}

	private static class RawFormatter implements IFormatter {
		public String getName() {
			return "raw";
		}

		public Object format(Object input) {
			return input;
		}
	}

	private static class HtmlFormatter implements IFormatter {
		public String getName() {
			return "html";
		}

		public Object format(Object value) {
			String s = value.toString();
			return s.replace("&", "&amp;").replace("<", "&lt;").replace(">",
					"&gt;");
		}
	}

	private static class HtmlTagFormatter extends HtmlFormatter {
		public String getName() {
			return "htmltag";
		}

	}

	private static class HtmlAttrValueFormatter implements IFormatter {
		public String getName() {
			return "html-attr-value";
		}

		public Object format(Object value) {
			String s = value.toString();
			return s.replace("&", "&amp;").replace("<", "&lt;").replace(">",
					"&gt;").replace("\"", "&quot;").replace("'", "&apos;");
		}
	}

	private static class StrFormatter implements IFormatter {

		public Object format(Object value) {
			return value.toString();
		}

		public String getName() {
			return "str";
		}

	};

}
