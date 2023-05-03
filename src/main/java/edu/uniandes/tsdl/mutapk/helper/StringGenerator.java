package edu.uniandes.tsdl.mutapk.helper;

import java.nio.charset.StandardCharsets;
import java.util.UUID;

public class StringGenerator {

	
	public static String generateRandomString(){
		long aux = Helper.getRandom().nextLong();
		return UUID.nameUUIDFromBytes(String.valueOf(aux).getBytes(StandardCharsets.UTF_8)).toString()
				.replaceAll("-", "");
	}
}
