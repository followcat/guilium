package hudson.plugins.guilium_plugin;

import hudson.Launcher;
import hudson.Extension;
import hudson.model.Build;
import hudson.model.BuildListener;
import hudson.model.AbstractBuild;
import hudson.tasks.Builder;
import hudson.tasks.BuildStepDescriptor;
import org.kohsuke.stapler.StaplerRequest;
import org.kohsuke.stapler.DataBoundConstructor;

import javax.management.Descriptor;

import java.io.IOException;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.File;
import java.io.FileWriter;
import java.io.BufferedWriter;

import java.security.MessageDigest;

import net.sf.json.JSONObject;
import net.sf.json.JSONArray;


/**
 * Sample {@link Builder}.
 *
 * <p>
 * When the user configures the project and enables this builder,
 * {@link DescriptorImpl#newInstance(StaplerRequest)} is invoked
 * and a new {@link GuiliumBuilder} is created. The created
 * instance is persisted to the project configuration XML by using
 * XStream, so this allows you to use instance fields (like {@link #name})
 * to remember the configuration.
 *
 * <p>
 * When a build is performed, the {@link #perform(Build, Launcher, BuildListener)} method
 * will be invoked.
 *
 * @author ZhangQuanyun
 */
public class GuiliumBuilder extends Builder {


    private final String cfile;
    private final String tplan;

    @DataBoundConstructor
    public GuiliumBuilder(String cfile, String tplan) {
        this.cfile = cfile;
        this.tplan = tplan;
    }

    public String getCfile() {
        return cfile;
    }

    public String getTplan() {
        return tplan;
    }

    private boolean saveJsonFile(String content, String absPath) throws IOException{
        File saveFile = new File(absPath);
        if(!saveFile.exists()){
            saveFile.createNewFile();
        }
        FileWriter fileWritter = new FileWriter(saveFile.getAbsolutePath());
        BufferedWriter bufferWritter = new BufferedWriter(fileWritter);
        String json_content = null;
        if (content.startsWith("[")) {
            json_content = JSONArray.fromObject(content).toString();
        }
        else {
            json_content = JSONObject.fromObject(content).toString();
        }
        bufferWritter.write(json_content);
        bufferWritter.close();
        return true;
    }

    public static String string2MD5(String inStr){
        MessageDigest md5 = null;
        try{
            md5 = MessageDigest.getInstance("MD5");
        }catch (Exception e){
            System.out.println(e.toString());
            e.printStackTrace();
            return "";
        }
        char[] charArray = inStr.toCharArray();
        byte[] byteArray = new byte[charArray.length];

        for (int i = 0; i < charArray.length; i++)
            byteArray[i] = (byte) charArray[i];
        byte[] md5Bytes = md5.digest(byteArray);
        StringBuffer hexValue = new StringBuffer();
        for (int i = 0; i < md5Bytes.length/2; i++){
            int val = ((int) md5Bytes[i]) & 0xff;
            if (val < 16)
                hexValue.append("0");
            hexValue.append(Integer.toHexString(val));
        }
        return hexValue.toString();

    }

    @Override
    public boolean perform(AbstractBuild build, Launcher launcher, BuildListener listener) {
        //save the config file and test file for python command run
        String config_file = "/tmp/config_"+string2MD5(cfile)+".json";
        String test_plan_file = "/tmp/test_"+string2MD5(tplan)+".json";
        try {
            saveJsonFile(cfile, config_file);
            saveJsonFile(tplan, test_plan_file);
        } catch(IOException e) {
            listener.getLogger().println("Exception "+ e.getMessage());
        }
        String command = "python nose_plugin/plugin.py --with-guilium --config-file="+config_file+" --test-file="+test_plan_file+" test/test_plan.py -v";
        listener.getLogger().println(command);
        boolean result = false;
        try {
            String ENV_GUILIUM_HOME = System.getenv("GUILIUM_HOME");
            Process pro = Runtime.getRuntime().exec(command, null, new File(ENV_GUILIUM_HOME));
            pro.waitFor();
            BufferedReader br = new BufferedReader(new InputStreamReader(pro.getInputStream()));
            BufferedReader br_er = new BufferedReader(new InputStreamReader(pro.getErrorStream()));
            StringBuffer sb = new StringBuffer();
            String line;
            while ((line = br.readLine()) != null || (line = br_er.readLine()) != null) {
                sb.append(line).append("\n");
                if ("OK".equals(line)) {
                    result = true;
                }
            }
            String output = sb.toString();
            listener.getLogger().println(output);
        } catch (Exception e) {
            listener.getLogger().println("Exception "+ e.getMessage());
        } finally {
            return result;
        }
    }

    @Override
    public DescriptorImpl getDescriptor() {
        return (DescriptorImpl)super.getDescriptor();
    }

    @Extension
    public static final class DescriptorImpl extends BuildStepDescriptor<Builder> {

        public DescriptorImpl() {
            load();
        }

        @Override
        public String getDisplayName() {
            return "Guilium UI Test";
        }

        @Override
        public boolean isApplicable(Class type) {
            return true;
        }

        @Override
        public boolean configure(StaplerRequest staplerRequest, JSONObject json) throws FormException {
            save();
            return true; // indicate that everything is good so far
        }
    }
}
