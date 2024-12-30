package edu.anon.cs.ipr.instrument;

import java.io.*;
import java.util.ArrayList;
import java.util.Scanner;

import edu.anon.cs.ipr.instrument.*;

public class InstruThread extends Thread {
    String filePath;
    int linenumber;
    String patch;
    String testName;
    String destination;
    String moduleName;
    String methodName;
    String directoryPath;
    int i;
    boolean result;
    String tracesFilePath;
    String typeInfoPath;
    String scriptPath;

    public boolean getResult() {
        return this.result;
    }

    public InstruThread(String filePath, int linenumber, String patch, String testName, String destination,
            String moduleName, String methodName, String directoryPath, int i, String tracesFilePath, String typeInfoPath, String scriptPath) {
        this.filePath = filePath;
        this.linenumber = linenumber;
        this.patch = patch;
        this.testName = testName;
        this.destination = destination;
        this.moduleName = moduleName;
        this.methodName = methodName;
        this.directoryPath = directoryPath;
        this.i = i;
        this.tracesFilePath = tracesFilePath;
        this.typeInfoPath = typeInfoPath;
        this.scriptPath = scriptPath;
    }

    public void instruTrace() {
        Scanner sc;
        try {
            sc = new Scanner(new File("F:\\CSVDemo.csv"));
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            return;
        }
        sc.useDelimiter(","); // sets the delimiter pattern
        while (sc.hasNext()) {
            String[] list = sc.nextLine().split(",");
        }
    }

    public void run() {

        String projectName = directoryPath.split("/")[directoryPath.split("/").length - 1];

        // read execution traces from a txt file, these execution traces do not include
        // our target file
        ArrayList<String> traces = new ArrayList<>();
        try {
            Scanner sc = new Scanner(new File(tracesFilePath));
            while (sc.hasNext()) {
                // System.out.println(sc.nextLine());
                traces.add(directoryPath + sc.nextLine());
            }
            sc.close();
        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("IPRTraecs txt file unreadable");
        }

        // for each of the trace info, we want to insert print statements
        ArrayList<String> paths = new ArrayList<>(); // this contains all the paths we should analyze in the call stack
        for (String each : traces) {
            String path = each.split(",")[0];
            int lineN = Integer.valueOf(each.split(",")[1]);
            path = path.replaceFirst(directoryPath, destination);
            paths.add(path);
            CloneInstrument.preprocessTrace(path, lineN, this.typeInfoPath);
        }

        this.result = CloneInstrument.showDiff(filePath, linenumber, patch, testName, destination, moduleName,
                methodName, this.typeInfoPath, this.scriptPath);
        if (i == 0) {
            System.out.println("[IPR] Project with buggy line has been tested.");
        } else {
            System.out.println("[IPR] Project with patch No." + Integer.toString(i) + " has been tested.");
        }

        // pass our return values back to CloneInstrument
        CloneInstrument.success.set(i, result);

        // copy our test results to a more obvious location
        try {
            org.apache.commons.io.FileUtils.copyFile(new File(
                    filePath.substring(0, filePath.lastIndexOf("/") + 1) + "iprOutput" + Integer.toString(linenumber)
                            + ".txt"),
                    new File(System.getProperty("user.home") + "/.ipr/" + projectName + "/iproutput/"
                            + Integer.toString(i)
                            + "#" + filePath.substring(filePath.lastIndexOf("/") + 1) + "#"
                            + Integer.toString(linenumber) + ".csv"));
        } catch (IOException e) {
            e.printStackTrace();
        }
        // now we only move the output file for our target file, we should also move
        // output files for the call stack
        for (String each : traces) {
            String path = each.split(",")[0];
            int lineN = Integer.valueOf(each.split(",")[1]);
            path = path.replaceFirst(directoryPath, destination);
            try {
                org.apache.commons.io.FileUtils.copyFile(new File(
                        path.substring(0, path.lastIndexOf("/") + 1) + "iprOutput" + Integer.toString(lineN) + ".txt"),
                        new File(System.getProperty("user.home") + "/.ipr/" + projectName + "/iproutput/" +
                                Integer.toString(i) + "#" + path.substring(path.lastIndexOf("/") + 1) +
                                "#" + Integer.toString(lineN) + ".csv"));
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
