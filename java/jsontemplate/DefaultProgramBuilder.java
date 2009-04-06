package jsontemplate;

import java.util.ArrayList;

public class DefaultProgramBuilder implements IProgramBuilder {

	Section currentBlock;
	private ArrayList<Section> stack;
	private IFormatterResolver moreFormatters;

	public DefaultProgramBuilder(IFormatterResolver moreFormatters) {
		this.currentBlock = new Section();
		this.stack = new ArrayList<Section>();
		this.stack.add(this.currentBlock);
		this.moreFormatters = moreFormatters;
	}

	public Section getRoot() {
		return this.currentBlock;
	}

	public void append(IStatement statement) {
		this.currentBlock.append(statement);
	}

	IFormatter getFormatter(String formatString) {
		IFormatter formatter = moreFormatters
				.getFormatterForFormatString(formatString);
		if (formatter == null) {
			formatter = DefaultFormatters.get(formatString);
		}
		if (formatter == null) {
			throw new BadFormatterError(formatString);
		}
		return formatter;
	}

	public void appendSubstitution(String name, String... formatters) {
		ArrayList<IFormatter> formatterObjects = new ArrayList<IFormatter>();
		for (String formatString : formatters) {
			formatterObjects.add(this.getFormatter(formatString));
		}
		this.currentBlock.append(new SubstitutionStatement(name,
				(IFormatter[]) formatterObjects
						.toArray(new IFormatter[formatterObjects.size()])));

	}

	public void newSection(boolean repeated, String sectionName) {
		Section newBlock = new Section(sectionName);
		if (repeated) {
			this.currentBlock.append(new RepeatedSectionStatement(newBlock));
		}
		else {
			this.currentBlock.append(new SectionStatement(newBlock));
		}
		this.stack.add(newBlock);
		this.currentBlock = newBlock;
		
	}

	public void newClause(String name) {
		this.currentBlock.newClause(name);
	}

	public void endSection() {
		this.stack.remove(this.stack.size() - 1);
		this.currentBlock = this.stack.get(this.stack.size() - 1);
	}

}
