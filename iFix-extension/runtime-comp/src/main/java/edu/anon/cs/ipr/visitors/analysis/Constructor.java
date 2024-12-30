package edu.anon.cs.ipr.visitors.analysis;

import java.util.ArrayList;

import edu.anon.cs.ipr.visitors.model.Token;

public class Constructor {
	public String name;
	public ArrayList<Token> args;

	public Constructor(String name, ArrayList<Token> args) {
		this.name = name;
		this.args = new ArrayList<Token>(args);
	}
}
