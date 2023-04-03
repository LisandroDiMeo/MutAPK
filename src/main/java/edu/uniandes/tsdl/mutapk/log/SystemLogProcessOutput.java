package edu.uniandes.tsdl.mutapk.log;

public class SystemLogProcessOutput extends LogProcessOutput {
    @Override
    void logWith(String message) {
        System.out.println(message);
    }
}
