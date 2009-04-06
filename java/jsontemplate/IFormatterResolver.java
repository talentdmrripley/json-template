package jsontemplate;

public interface IFormatterResolver {
	public IFormatter getFormatterForFormatString(String formatString);
}
