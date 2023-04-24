package edu.uniandes.tsdl.mutapk.processors;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.antlr.runtime.RecognitionException;
import org.antlr.runtime.tree.CommonTree;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.filefilter.TrueFileFilter;

import edu.uniandes.tsdl.antlr.smaliParser;
import edu.uniandes.tsdl.mutapk.helper.ASTHelper;
import edu.uniandes.tsdl.mutapk.helper.Helper;
import edu.uniandes.tsdl.mutapk.model.SmaliAST;

public class SourceCodeProcessor {

    public void generateASTsMap(String extrasFolder, String packageName, HashMap<String, SmaliAST> smaliASTs) throws IOException, RecognitionException {
        String decodedPath = Helper.getInstance().getCurrentDirectory();
        String folderPath = Paths.get(decodedPath, "temp").toAbsolutePath().toString();
        ArrayList<String> folderPaths = findSmaliFilePaths(folderPath);
        for(String path : folderPaths){
            Collection<File> files = FileUtils.listFiles(new File(path), TrueFileFilter.INSTANCE, TrueFileFilter.INSTANCE);

            ArrayList<File> usefulFilesFromPath = files.stream().filter(aFile -> {
                boolean isSmaliFile = aFile.getPath().endsWith(".smali");
                boolean isFileFromPackage = false;
                try {
                    isFileFromPackage = aFile.getCanonicalPath().contains(packageName.replace(".", Helper.isWindows() ? "\\" : "/"));
                } catch (Exception e) {
                    // Skip
                }
                boolean isFinishListener = aFile.getName().contains("FinishListener.java");
                boolean isSMSReceiver = aFile.getName().contains("SMSInstrumentedReceiver.java");
                boolean isInstrumentedActivity = aFile.getName().contains("InstrumentedActivity.java");
                boolean isEmmaInstrumentation = aFile.getName().contains("EmmaInstrumentation.java");
                return isSmaliFile && isFileFromPackage && !isFinishListener && !isSMSReceiver && !isInstrumentedActivity && !isEmmaInstrumentation;
            }).collect(Collectors.toCollection(ArrayList::new));

            for (File file : usefulFilesFromPath) {
                if (file.getName().endsWith(".smali") && file.getCanonicalPath().contains(packageName.replace(".", Helper.isWindows() ? "\\" : "/")) && !file.getName().contains("EmmaInstrumentation.java") && !file.getName().contains("FinishListener.java") && !file.getName().contains("InstrumentedActivity.java") && !file.getName().contains("SMSInstrumentedReceiver.java")) {
                    String filePath = file.getAbsolutePath();
                    CommonTree baseAST = ASTHelper.getAST(file.getAbsolutePath());
                    // TODO: Do all files in java have Class descriptors?
                    String unitName = baseAST.getFirstChildWithType(smaliParser.CLASS_DESCRIPTOR).getText();

                    SmaliAST temp = new SmaliAST(unitName, filePath, baseAST);
                    smaliASTs.put(unitName, temp);
                }
            }
        }

    }

    public static ArrayList<String> findSmaliFilePaths(String decodedPath, String ...more) {
        ArrayList<String> result = new ArrayList<>();
        Path dir = Paths.get(decodedPath, more);
        // get all paths in the temp directory that start with "smali"
        // this is because some newer apps separate their classes in
        // multiple smali dirs.
        try (Stream<Path> paths = Files.list(dir)) {
            paths.filter(path -> path.getFileName().toString().startsWith("smali"))
                    .forEach(path -> result.add(path.toAbsolutePath().toString()));
        } catch (IOException e){
            result.add(Paths.get(decodedPath, "temp", "smali").toAbsolutePath().toString());
        }
        return result;
    }

}
