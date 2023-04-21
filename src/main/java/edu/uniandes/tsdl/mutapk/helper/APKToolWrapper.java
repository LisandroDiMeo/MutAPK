package edu.uniandes.tsdl.mutapk.helper;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import edu.uniandes.tsdl.mutapk.helper.Helper;
import edu.uniandes.tsdl.mutapk.log.SystemLogProcessOutput;

public class APKToolWrapper {

    public static String openAPK(String path, String extraPath) throws IOException, InterruptedException {
        String decodedPath = Helper.getInstance().getCurrentDirectory();
        // Creates folder for decoded app
//		System.out.println(decodedPath);
        File tempFolder = new File(decodedPath + File.separator + "temp");
        if (tempFolder.exists()) {
            tempFolder.delete();
        }
        tempFolder.mkdirs();
        System.out.println("> Processing your APK...  ");
        Process ps = Runtime.getRuntime().exec(new String[]{"java", "-jar", Paths.get(decodedPath, extraPath, "apktool.jar").toAbsolutePath().toString(), "d", Paths.get(decodedPath, path).toAbsolutePath().toString(), "-o", Paths.get(decodedPath, "temp").toAbsolutePath().toString(), "-f"});
        SystemLogProcessOutput log = new SystemLogProcessOutput();
        log.logProcess(ps, true);
        System.out.println("> Wow... that was an amazing APK to proccess!!! :D");
        System.out.println();
        return tempFolder.getAbsolutePath();
        // InputStream es = ps.getErrorStream();
        // byte e[] = new byte[es.available()];
        // es.read(e,0,e.length);
        // System.out.println("ERROR: "+ new String(e));
        // InputStream is = ps.getInputStream();
        // byte b[] = new byte[is.available()];
        // is.read(b,0,b.length);
        // System.out.println("INFO: "+new String(b));
        // System.out.println(decodedPath);
    }

    public static boolean buildAPK(String path, String extraPath, String appName, int mutantIndex) throws IOException, InterruptedException {
        String decodedPath = Helper.getInstance().getCurrentDirectory();
        Path parsedPathWithAppName = Paths.get(decodedPath, path, appName);
        Process ps = Runtime.getRuntime().exec(new String[]{
                "java",
                "-jar",
                Paths.get(decodedPath, extraPath, "apktool.jar").toAbsolutePath().toString(),
                "b",
                Paths.get(decodedPath, path, "src").toAbsolutePath().toString(),
                "-o",
                parsedPathWithAppName.toAbsolutePath().toString(),
                "-f"});
        System.out.println("Building mutant " + mutantIndex + "...");

        SystemLogProcessOutput log = new SystemLogProcessOutput();

        log.logProcess(ps, true);


        Path parsedPath = Paths.get(decodedPath, path);
        Process pss = Runtime.getRuntime().exec(new String[]{
                "java",
                "-jar",
                Paths.get(decodedPath, extraPath, "uber-apk-signer.jar").toAbsolutePath().toString(),
                "-a",
                parsedPath.toAbsolutePath().toString(),
                "-o", parsedPath.toAbsolutePath().toString()});

        System.out.println("Signing mutant " + mutantIndex + "...");
        
        log.logProcess(pss, true);
        
        if (Files.exists(parsedPathWithAppName.toAbsolutePath())) {
            System.out.println("SUCCESS: The " + mutantIndex + " mutant APK has been generated.");
            return true;
        } else {
            System.out.println("ERROR: The " + mutantIndex + " mutant APK has not been generated.");
            return false;
        }
    }
}