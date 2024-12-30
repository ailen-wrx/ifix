package edu.anon.cs.ipr.visitors.analysis;

import java.io.File;
import java.io.IOException;
import java.util.Map;
import java.util.Scanner;

import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.CompilationUnit;

public class CloneParser {

	// added properties for the parser
	public int x;
	public int y;
	private int lineNumber;

	private void set_x(int new_x) {
		this.x = new_x;
	}

	public int get_x() {
		return this.x;
	}

	private void set_y(int new_y) {
		this.y = new_y;
	}

	public int get_y() {
		return this.y;
	}

	private void set_lineNumber(int new_lineNumber) {
		this.lineNumber = new_lineNumber;
	}

	public int get_lineNumber() {
		return this.lineNumber;
	}
	// till here

	// read file content into a string
	public String readFileToString(String filePath) throws IOException {
		File file = new File(filePath);
		StringBuilder fileContents = new StringBuilder((int) file.length());
		Scanner scanner = new Scanner(file);
		String lineSeparator = System.getProperty("line.separator");

		try {
			while (scanner.hasNextLine()) {
				fileContents.append(scanner.nextLine() + lineSeparator);
			}
			return fileContents.toString();
		} finally {
			scanner.close();
		}
	}

	public CompilationUnit parse(String file) throws IOException {
		// read file
		String str = readFileToString(file);

		// call ASPParser to generate the AST
		ASTParser parser = ASTParser.newParser(AST.JLS3);
		parser.setSource(str.toCharArray());
		parser.setKind(ASTParser.K_COMPILATION_UNIT);
		Map options = JavaCore.getOptions();
		JavaCore.setComplianceOptions(JavaCore.VERSION_1_5, options);
		parser.setCompilerOptions(options);
		final CompilationUnit cu = (CompilationUnit) parser.createAST(null);

		return cu;
	}

	private void get_x_y(int lineNumber, String str) {
		int new_lineNumber = 1; // keep track of current line number
		for (int i = 0; i < str.length(); i++) {
			if (lineNumber == new_lineNumber) {
				set_x(i);
				int j = 0;
				for (j = x; j < str.length(); j++) {
					if (str.charAt(j) == '\n') {
						set_y(j);
						break;
					}
				}
				System.out.println("x: " + get_x() + " y: " + get_y());
				System.out.println("lineNumber: " + lineNumber);
				System.out.println("strContent: " + str.substring(i, j));
				break;
			}
			if (str.charAt(i) == '\n') {
				new_lineNumber++;
			}
		}
	}

	public static void main(String[] args) throws IOException {
		CloneParser cp = new CloneParser();
		String str = cp.readFileToString(
				"D:/grafter-dataset/apache-ant-1.9.6/src/main/org/apache/tools/ant/types/PatternSet.java");
		int x = str.indexOf("public void setIncludes(String includes) {");

		cp.get_x_y(343, str);

		System.out.println("strContent: " + str.substring(cp.get_x(), cp.get_y()));
		System.out.println();
		System.out.println();
		System.out.println();
		System.out.println(x);
		System.out.println(x + 383);
		System.out.print(str.substring(10942, 11325));
	}
}
