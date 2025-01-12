package edu.uniandes.tsdl.mutapk.helper;

import java.util.Random;

public class HexadecimalGenerator {
	
	
	public static String generateRandomHexa() {
		Random r = Helper.getRandom();
	    final char [] hex = { '0', '1', '2', '3', '4', '5', '6', '7',
	                          '8', '9', 'a', 'b', 'c', 'd', 'e', 'f' };
	    char [] s = new char[8];
	    int     n = r.nextInt(0x1000000);

//	    s[0] = '#';
	    for (int i=0;i<8;i++) {
	        s[i] = hex[n & 0xf];
	        n >>= 4;
	    }
	    return new String(s);
	}
	
	public static String generateRandomHexaLong() {
		String hexa = generateRandomHexa();
		return hexa.substring(0, hexa.length()-1)+"L";
	}

}
