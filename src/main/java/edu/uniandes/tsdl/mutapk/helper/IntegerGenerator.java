package edu.uniandes.tsdl.mutapk.helper;

public class IntegerGenerator {

	private static final int MINIMUM = 0;
	private static final int MAXIMUM = 9999;

	public static int generateRandomInt(int minimum, int maximum){
		
		return minimum + (int)(Helper.getRandom().nextDouble() * maximum);
	}
	
	
	public static int generateRandomInt(){
		//Generate random integers between -9999 and 9999
		return (generateRandomInt(MINIMUM, MAXIMUM*2)-MAXIMUM);
	}
}
