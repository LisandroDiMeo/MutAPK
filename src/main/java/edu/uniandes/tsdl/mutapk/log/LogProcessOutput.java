package edu.uniandes.tsdl.mutapk.log;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

abstract class LogProcessOutput {

    private static final String EXECUTED_WITH_ERRORS = "Process executed with errors: ";
    abstract void logWith(String message);

    public void logProcess(Process process, boolean shouldWait) throws IOException, InterruptedException {
        InputStreamReader inputStreamReader = new InputStreamReader(process.getInputStream());
        BufferedReader bufferedReader = new BufferedReader(inputStreamReader);
        String line;
        while ((line = bufferedReader.readLine()) != null) {
            logWith(line);
        }
        inputStreamReader = new InputStreamReader(process.getErrorStream());
        bufferedReader = new BufferedReader(inputStreamReader);
        boolean showErrorLogMessage = false;
        while ((line = bufferedReader.readLine()) != null) {
            if (!showErrorLogMessage) {
                logWith(EXECUTED_WITH_ERRORS);
                showErrorLogMessage = true;
            }
            logWith(line);
        }
        if (shouldWait) process.waitFor();
    }


}

