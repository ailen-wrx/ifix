package edu.anon.cs.ipr.visitors.analysis;

import java.util.ArrayList;

import edu.anon.cs.ipr.visitors.model.Token;

public class Setter {
	public String name;
	public Token token;
	public ArrayList<Token> args;

	public Setter(String name, Token t, ArrayList<Token> args) {
		this.name = name;
		this.token = t;
		this.args = new ArrayList<Token>(args);
	}
}
